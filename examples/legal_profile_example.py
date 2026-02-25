"""
Example: legal profile with dsRAG.

This example demonstrates selecting a legal-oriented profile and querying
without manually tuning retrieval defaults.
"""

from dsrag.knowledge_base import KnowledgeBase


def main():
    kb = KnowledgeBase(
        kb_id="legal_profile_demo",
        profile="legal_default",
        exists_ok=True,
    )

    kb.add_document(
        doc_id="demo_contract_doc",
        text="This agreement may be terminated for cause upon material breach with 30 days cure period.",
    )

    results = kb.query(["Under what conditions can the agreement be terminated?"])
    print(f"Retrieved {len(results)} segments")


if __name__ == "__main__":
    main()
