"""
Example: finance profile with dsRAG.

This example demonstrates selecting a domain profile and still overriding
specific config values when needed.
"""

from dsrag.knowledge_base import KnowledgeBase


def main():
    kb = KnowledgeBase(
        kb_id="finance_profile_demo",
        profile="finance_default",
        exists_ok=True,
    )

    # You can provide text directly to avoid file parsing setup in quick experiments.
    kb.add_document(
        doc_id="demo_finance_doc",
        text="Revenue increased by 12% year-over-year while operating margin declined.",
        auto_context_config={"get_section_summaries": False},  # explicit override
    )

    # Query uses profile defaults when rse_params/vector_search_top_k are omitted.
    results = kb.query(["What changed in revenue and operating margin?"])
    print(f"Retrieved {len(results)} segments")


if __name__ == "__main__":
    main()
