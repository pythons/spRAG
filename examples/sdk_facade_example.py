"""
Example: use the SDK facade contract.
"""

from dsrag import DSRAGSDK, AddDocumentRequest, CreateKBRequest, QueryRequest


def main():
    sdk = DSRAGSDK()
    print(sdk.create_kb(CreateKBRequest(kb_id="sdk_demo")))
    print(
        sdk.add_document(
            AddDocumentRequest(
                kb_id="sdk_demo",
                doc_id="doc_1",
                text="This is a simple SDK facade demo.",
            )
        )
    )
    print(
        sdk.query(
            QueryRequest(
                kb_id="sdk_demo",
                search_queries=["What is this document about?"],
            )
        )
    )


if __name__ == "__main__":
    main()
