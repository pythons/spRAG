import importlib.util
import os
import platform
from datetime import datetime, timezone
from typing import Dict, List


OPTIONAL_DEPENDENCIES = {
    "openai": "openai",
    "cohere": "cohere",
    "anthropic": "anthropic",
    "google-genai": "google.genai",
    "google-generativeai": "google.generativeai",
    "chromadb": "chromadb",
    "weaviate": "weaviate",
    "qdrant": "qdrant_client",
    "milvus": "pymilvus",
    "pinecone": "pinecone",
    "postgres": "psycopg2",
    "boto3": "boto3",
}


SENSITIVE_ENV_VARS = [
    "OPENAI_API_KEY",
    "COHERE_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "VOYAGE_API_KEY",
]


def _is_importable(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def run_diagnostics() -> Dict:
    """
    Return a lightweight diagnostics report for common setup/runtime issues.
    """
    dependencies: Dict[str, bool] = {}
    for feature, module_name in OPTIONAL_DEPENDENCIES.items():
        dependencies[feature] = _is_importable(module_name)

    environment: Dict[str, bool] = {}
    for env_name in SENSITIVE_ENV_VARS:
        environment[env_name] = bool(os.getenv(env_name))

    missing_deps: List[str] = [name for name, installed in dependencies.items() if not installed]
    missing_envs: List[str] = [name for name, configured in environment.items() if not configured]

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": dependencies,
        "environment": environment,
        "missing_dependency_features": missing_deps,
        "missing_env_vars": missing_envs,
    }
