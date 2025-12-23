"""
LLM Fallback Mechanism
Provides fallback from Groq to Gemini for LLM queries
"""

import os
from typing import Optional
from llama_index.llms.groq import Groq
try:
    from llama_index.llms.gemini import Gemini
except ImportError:
    try:
        from llama_index.llms.google import Gemini
    except ImportError:
        Gemini = None
import yaml
from pathlib import Path


def create_llm_with_fallback(
    groq_api_key: Optional[str] = None,
    groq_model: str = "llama-3.3-70b-versatile",
    gemini_api_key: Optional[str] = None,
    gemini_model: str = "gemini-2.0-flash",
    load_from_config: bool = True
) -> Optional[object]:
    """
    Create LLM with fallback mechanism (Groq -> Gemini).
    
    Args:
        groq_api_key: Groq API key (optional if load_from_config)
        groq_model: Groq model name
        gemini_api_key: Gemini API key (optional if load_from_config)
        gemini_model: Gemini model name
        load_from_config: Whether to load API keys from Config.yaml
        
    Returns:
        LLM instance (Groq or Gemini) or None if neither is available
    """
    # Load from config if requested
    if load_from_config:
        config = _load_config()
        if config:
            groq_config = config.get('groq', {})
            gemini_config = config.get('gemini', {})
            
            if not groq_api_key:
                groq_api_key = groq_config.get('api_key') or os.getenv('GROQ_API_KEY')
            if not gemini_api_key:
                gemini_api_key = gemini_config.get('api_key') or os.getenv('GEMINI_API_KEY')
            
            if not groq_model:
                groq_model = groq_config.get('model', groq_model)
            if not gemini_model:
                gemini_model = gemini_config.get('model', gemini_model)
    
    # Try Groq first
    if groq_api_key:
        try:
            print("🔧 Initializing Groq LLM...")
            llm = Groq(api_key=groq_api_key, model=groq_model)
            print("✅ Groq LLM initialized successfully")
            return llm
        except Exception as e:
            print(f"⚠️  Failed to initialize Groq: {e}")
    
    # Fallback to Gemini
    if gemini_api_key and Gemini:
        try:
            print("🔧 Initializing Gemini LLM (fallback)...")
            llm = Gemini(api_key=gemini_api_key, model=gemini_model)
            print("✅ Gemini LLM initialized successfully")
            return llm
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini: {e}")
    
    print("⚠️  No LLM available (neither Groq nor Gemini)")
    return None


def _load_config(config_path: str = "Config.yaml") -> Optional[dict]:
    """Load configuration from YAML file."""
    config_paths = [
        config_path,
        Path(__file__).parent / config_path,
        Path(__file__).parent.parent / config_path
    ]
    
    for path in config_paths:
        if Path(path).exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️  Failed to load config from {path}: {e}")
    
    return None

