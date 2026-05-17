"""
LexGuard Configuration
Central configuration for API keys, model names, and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── API Keys ──────────────────────────────────────────────────────────────────
# Groq settings (single unified provider)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Default to a smaller, higher-throughput model to reduce rate-limit pressure.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
HF_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ── Risk Scoring Weights ─────────────────────────────────────────────────────
RISK_WEIGHTS = {
    "CRITICAL": 40,
    "HIGH": 20,
    "MEDIUM": 8,
    "LOW": 2,
}

# ── Grade Thresholds ─────────────────────────────────────────────────────────
GRADE_THRESHOLDS = {
    "F": 70,
    "D": 50,
    "C": 30,
    "B": 15,
    # Anything <= 15 is "A"
}

# ── Application Settings ─────────────────────────────────────────────────────
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
CHROMA_PERSIST_DIR = PROJECT_ROOT / "data" / "chroma_db"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# ── Server Settings ──────────────────────────────────────────────────────────
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
