"""
Example: use vertical templates for finance/legal workflows.
"""

from dsrag import (
    create_kb_from_template,
    apply_template_to_add_document_kwargs,
    query_with_template,
)


def main():
    kb = create_kb_from_template("finance", kb_id="finance_template_demo")

    add_kwargs = apply_template_to_add_document_kwargs(
        "finance",
        {
            "chunking_config": {"chunk_size": 1000},
        },
    )
    kb.add_document(
        doc_id="demo_finance_doc",
        text="Revenue increased while gross margin compressed due to input costs.",
        **add_kwargs,
    )

    results = query_with_template(
        kb,
        "finance",
        ["What changed in margin and why?"],
    )
    print(results)


if __name__ == "__main__":
    main()
