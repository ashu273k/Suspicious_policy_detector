"""
Agent Orchestrator — Routes clauses to appropriate agents, runs analysis,
and merges results.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from .base_agent import BaseAgent
from .liability_agent import LiabilityAgent
from .privacy_agent import PrivacyAgent
from .ip_agent import IPAgent
from .arbitration_agent import ArbitrationAgent
from .financial_agent import FinancialAgent


def create_agents(doc_token_count: int = 0) -> list[BaseAgent]:
    """Initialize all analysis agents."""
    return [
        LiabilityAgent(doc_token_count=doc_token_count),
        PrivacyAgent(doc_token_count=doc_token_count),
        IPAgent(doc_token_count=doc_token_count),
        ArbitrationAgent(doc_token_count=doc_token_count),
        FinancialAgent(doc_token_count=doc_token_count),
    ]


def analyze_clauses(
    clauses: list[dict],
    full_contract: str = "",
    doc_token_count: int = 0,
    max_workers: int = 1,
    progress_callback: Optional[callable] = None,
) -> list[dict]:
    """
    Run all appropriate agents on each clause.

    Args:
        clauses: List of extracted clause dicts
        full_contract: Full contract text for context
        doc_token_count: Token count for LLM routing
        max_workers: Concurrent analysis threads
        progress_callback: Optional fn(completed, total) for progress tracking

    Returns:
        List of analyzed clause dicts with agent results merged in
    """
    agents = create_agents(doc_token_count)
    analyzed = []
    total_tasks = 0

    # Build task list: (clause, agent) pairs
    tasks = []
    for clause in clauses:
        clause_type = clause.get("clause_type", "GENERAL")
        matching_agents = [a for a in agents if a.can_handle(clause_type)]

        # Always run liability agent as baseline
        if not any(isinstance(a, LiabilityAgent) for a in matching_agents):
            matching_agents.insert(0, LiabilityAgent(doc_token_count=doc_token_count))

        for agent in matching_agents:
            tasks.append((clause, agent))

    total_tasks = len(tasks)
    completed = 0

    # Group results by clause_id
    results_by_clause = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(agent.analyze, clause, full_contract): (clause, agent)
            for clause, agent in tasks
        }

        for future in as_completed(future_to_task):
            clause, agent = future_to_task[future]
            clause_id = clause.get("clause_id")

            try:
                result = future.result()
            except Exception as e:
                result = {
                    "agent": agent.name,
                    "clause_id": clause_id,
                    "severity": "LOW",
                    "error": str(e),
                }

            if clause_id not in results_by_clause:
                results_by_clause[clause_id] = {
                    "clause": clause,
                    "agent_results": [],
                }

            results_by_clause[clause_id]["agent_results"].append(result)

            completed += 1
            if progress_callback:
                progress_callback(completed, total_tasks)

    # Merge and determine highest severity per clause
    for clause_id in sorted(results_by_clause.keys()):
        entry = results_by_clause[clause_id]
        agent_results = entry["agent_results"]

        # Find the highest severity across all agents
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
        max_severity = "NONE"
        for r in agent_results:
            sev = r.get("severity", "NONE")
            if severity_order.get(sev, 0) > severity_order.get(max_severity, 0):
                max_severity = sev

        analyzed.append({
            "clause": entry["clause"],
            "agent_results": agent_results,
            "max_severity": max_severity,
        })

    return analyzed
