"""
Example: capture dsRAG telemetry events in memory.
"""

from dsrag import InMemoryTelemetrySink
from dsrag.knowledge_base import KnowledgeBase


def main():
    sink = InMemoryTelemetrySink()
    kb = KnowledgeBase(kb_id="telemetry_demo", telemetry_sink=sink)

    kb.add_document(doc_id="doc_1", text="Simple telemetry demo text.")
    kb.query(search_queries=["What is this document about?"])

    for event in sink.get_events():
        print(event["event_type"], event["status"], event.get("duration_ms"))


if __name__ == "__main__":
    main()
