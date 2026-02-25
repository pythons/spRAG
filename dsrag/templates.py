from copy import deepcopy
from typing import Any, Dict, List


VERTICAL_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "finance": {
        "profile": "finance_default",
        "ingestion_defaults": {
            "auto_context_config": {
                "get_section_summaries": True,
                "section_summarization_guidance": "Focus on financial metrics, period-over-period deltas, and risk disclosures.",
            },
            "semantic_sectioning_config": {
                "use_semantic_sectioning": True,
            },
            "chunking_config": {
                "chunk_size": 900,
            },
        },
        "query_defaults": {
            "rse_params": "balanced",
            "vector_search_top_k": 240,
            "return_mode": "text",
        },
    },
    "legal": {
        "profile": "legal_default",
        "ingestion_defaults": {
            "auto_context_config": {
                "get_section_summaries": True,
                "section_summarization_guidance": "Emphasize obligations, exceptions, timelines, and jurisdiction-specific constraints.",
            },
            "semantic_sectioning_config": {
                "use_semantic_sectioning": True,
            },
            "chunking_config": {
                "chunk_size": 850,
            },
        },
        "query_defaults": {
            "rse_params": "balanced",
            "vector_search_top_k": 230,
            "return_mode": "text",
        },
    },
}


def list_vertical_templates() -> List[str]:
    return sorted(VERTICAL_TEMPLATES.keys())


def get_vertical_template(template_name: str) -> Dict[str, Any]:
    if template_name not in VERTICAL_TEMPLATES:
        available = ", ".join(list_vertical_templates())
        raise ValueError(
            f"Unknown template '{template_name}'. Available templates: {available}"
        )
    return deepcopy(VERTICAL_TEMPLATES[template_name])


def _merge_dict(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(defaults)
    for key, value in overrides.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def apply_template_to_add_document_kwargs(
    template_name: str, add_document_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    template = get_vertical_template(template_name)
    ingestion_defaults = template.get("ingestion_defaults", {})
    return _merge_dict(ingestion_defaults, add_document_kwargs or {})


def apply_template_to_query_kwargs(
    template_name: str, query_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    template = get_vertical_template(template_name)
    query_defaults = template.get("query_defaults", {})
    return _merge_dict(query_defaults, query_kwargs or {})


def create_kb_from_template(template_name: str, kb_id: str, **knowledge_base_kwargs):
    template = get_vertical_template(template_name)
    profile = knowledge_base_kwargs.pop("profile", template["profile"])
    from dsrag.knowledge_base import KnowledgeBase

    return KnowledgeBase(kb_id=kb_id, profile=profile, **knowledge_base_kwargs)


def query_with_template(kb, template_name: str, search_queries: List[str], **query_kwargs):
    merged_query_kwargs = apply_template_to_query_kwargs(template_name, query_kwargs)
    return kb.query(search_queries=search_queries, **merged_query_kwargs)
