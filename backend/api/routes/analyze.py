"""
Analyze Route — Run the full analysis pipeline on an uploaded document.
"""

import json
from fastapi import APIRouter, Body, HTTPException

from api.schemas import AnalysisReport
from api.routes.upload import get_document
from ingestion.preprocessor import estimate_token_count
from extraction.clause_extractor import extract_clauses
from extraction.embedder import embed_clauses
from agents.orchestrator import analyze_clauses
from scoring.aggregator import aggregate_results
from reporting.report_builder import build_report
from rag.vector_store import store_clauses

router = APIRouter()

# In-memory report store
reports = {}


@router.post("/analyze", response_model=AnalysisReport)
async def analyze_document(request: dict = Body(default_factory=dict)):
    """
    Run the full LexGuard analysis pipeline on an uploaded document.

    Pipeline:
    1. Retrieve document text
    2. Extract clauses via LLM
    3. Generate embeddings & store in ChromaDB
    4. Run multi-agent analysis
    5. Score and aggregate results
    6. Generate executive summary
    7. Build final report
    """
    document_id = request.get("document_id") or request.get("documentId")
    if not document_id:
        raise HTTPException(status_code=400, detail="document_id is required")

    # 1. Get document
    doc = get_document(document_id)
    contract_text = doc["text"]
    token_count = estimate_token_count(contract_text)

    if not contract_text.strip():
        raise HTTPException(status_code=422, detail="Document contains no extractable text")

    print(f"📄 Analyzing '{doc['filename']}' ({token_count} est. tokens)...")

    # 2. Extract clauses
    print("🔍 Step 1/5: Extracting clauses...")
    try:
        clauses = extract_clauses(contract_text)
    except Exception as e:
        import traceback

        print("⚠️ Exception during clause extraction:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Clause extraction failed: {e}")

    if not clauses:
        raise HTTPException(status_code=422, detail="No clauses could be extracted from the document")

    print(f"   ✅ Extracted {len(clauses)} clauses")

    # 3. Generate embeddings and store
    print("📊 Step 2/5: Generating embeddings...")
    try:
        clauses = embed_clauses(clauses)
        store_clauses(document_id, clauses)
    except Exception as e:
        print(f"   ⚠️  Embedding/storage warning: {e}")

    # 4. Multi-agent analysis
    print("🤖 Step 3/5: Running agent analysis...")
    try:
        analyzed = analyze_clauses(
            clauses=clauses,
            full_contract=contract_text,
            doc_token_count=token_count,
            max_workers=1,  # Serialize calls to reduce TPM/RPM bursts
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {e}")

    print(f"   ✅ Analyzed {len(analyzed)} clauses across multiple agents")

    # 5. Score and aggregate
    print("📈 Step 4/5: Scoring...")
    score_result = aggregate_results(analyzed)
    print(f"   ✅ Score: {score_result['overall_score']}/100 (Grade: {score_result['grade']})")

    # 6-7. Build report with executive summary
    print("📝 Step 5/5: Generating report...")
    try:
        report_data = build_report(
            document_id=document_id,
            filename=doc["filename"],
            analyzed_clauses=analyzed,
            score_result=score_result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")

    # Cache the report
    reports[report_data["report_id"]] = report_data
    reports[f"doc_{document_id}"] = report_data

    print(f"✅ Analysis complete for '{doc['filename']}'")

    return AnalysisReport(**report_data)
