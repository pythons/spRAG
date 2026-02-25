from copy import deepcopy
from typing import Any, Dict


DEFAULT_PROFILE = "general_balanced"


PROFILE_PRESETS: Dict[str, Dict[str, Any]] = {
    "general_balanced": {
        "auto_context_config": {
            "use_generated_title": True,
            "get_document_summary": True,
            "get_section_summaries": False,
            "llm_max_concurrent_requests": 5,
        },
        "semantic_sectioning_config": {
            "use_semantic_sectioning": True,
            "llm_max_concurrent_requests": 5,
            "min_avg_chars_per_section": 500,
        },
        "chunking_config": {
            "chunk_size": 800,
            "min_length_for_chunking": 1600,
        },
        "query_defaults": {
            "rse_params": "balanced",
            "vector_search_top_k": 200,
        },
    },
    "finance_default": {
        "auto_context_config": {
            "use_generated_title": True,
            "get_document_summary": True,
            "get_section_summaries": True,
            "llm_max_concurrent_requests": 8,
        },
        "semantic_sectioning_config": {
            "use_semantic_sectioning": True,
            "llm_max_concurrent_requests": 8,
            "min_avg_chars_per_section": 600,
        },
        "chunking_config": {
            "chunk_size": 900,
            "min_length_for_chunking": 1800,
        },
        "query_defaults": {
            "rse_params": {
                "max_length": 20,
                "overall_max_length": 40,
                "minimum_value": 0.45,
                "irrelevant_chunk_penalty": 0.16,
                "overall_max_length_extension": 8,
                "decay_rate": 35,
                "top_k_for_document_selection": 15,
                "chunk_length_adjustment": True,
            },
            "vector_search_top_k": 240,
        },
    },
    "legal_default": {
        "auto_context_config": {
            "use_generated_title": True,
            "get_document_summary": True,
            "get_section_summaries": True,
            "llm_max_concurrent_requests": 8,
        },
        "semantic_sectioning_config": {
            "use_semantic_sectioning": True,
            "llm_max_concurrent_requests": 8,
            "min_avg_chars_per_section": 550,
        },
        "chunking_config": {
            "chunk_size": 850,
            "min_length_for_chunking": 1700,
        },
        "query_defaults": {
            "rse_params": {
                "max_length": 18,
                "overall_max_length": 45,
                "minimum_value": 0.42,
                "irrelevant_chunk_penalty": 0.15,
                "overall_max_length_extension": 10,
                "decay_rate": 40,
                "top_k_for_document_selection": 16,
                "chunk_length_adjustment": True,
            },
            "vector_search_top_k": 230,
        },
    },
}


def get_profile_preset(profile: str) -> Dict[str, Any]:
    if profile not in PROFILE_PRESETS:
        available = ", ".join(sorted(PROFILE_PRESETS.keys()))
        raise ValueError(f"Unknown profile '{profile}'. Available profiles: {available}")
    return deepcopy(PROFILE_PRESETS[profile])


def merge_with_profile_defaults(profile_defaults: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge profile defaults with user config.
    User values always take precedence over profile defaults.
    """
    merged = deepcopy(profile_defaults)
    merged.update(user_config)
    return merged
