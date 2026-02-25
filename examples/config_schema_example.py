"""
Example: export stable KB config schema.
"""

from dsrag.knowledge_base import KnowledgeBase


def main():
    kb = KnowledgeBase(kb_id="config_schema_demo")
    print(kb.export_config_schema())


if __name__ == "__main__":
    main()
