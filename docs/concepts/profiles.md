# Profiles

Profiles provide domain-tuned defaults for ingestion and query settings.

Available profiles:
- `general_balanced` (default)
- `finance_default`
- `legal_default`

## What a profile controls
- AutoContext defaults
  - title/summary generation behavior
  - section summary behavior and concurrency
- Semantic sectioning defaults
  - enablement and concurrency
  - `min_avg_chars_per_section`
- Chunking defaults
  - `chunk_size`
  - `min_length_for_chunking`
- Query defaults
  - `rse_params`
  - `vector_search_top_k`

User-provided configs always override profile defaults.

## Usage

```python
from dsrag.knowledge_base import KnowledgeBase

kb = KnowledgeBase(
    kb_id="finance_kb",
    profile="finance_default",
)
```

You can still override any setting:

```python
kb.add_document(
    doc_id="q4_report",
    file_path="/path/to/report.pdf",
    chunking_config={"chunk_size": 1000},  # overrides profile chunk_size
)
```

Query defaults are applied when omitted:

```python
# uses profile rse_params and vector_search_top_k
results = kb.query(["What were the major risk factors?"])
```
