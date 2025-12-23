"""Configuration for RAG System"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "DATA"
RAW_DIR = DATA_DIR / "raw"

# Vector store directory
VECTORSTORE_DIR = REPO_ROOT / "vectorstore"

# Streamlit Configuration
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"
