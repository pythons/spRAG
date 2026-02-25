# Config Schema

dsRAG provides a stable, versioned configuration schema for KB snapshots.

## Goals
- Stable shape for tooling and hosted-readiness interfaces
- Explicit schema versioning
- Sensitive-value boundaries via automatic redaction

## API

```python
from dsrag.knowledge_base import KnowledgeBase

kb = KnowledgeBase(kb_id="my_kb")
config = kb.export_config_schema()  # sensitive values redacted
```

To include sensitive fields explicitly:

```python
config = kb.export_config_schema(include_sensitive=True)
```

Top-level schema fields:
- `schema_version`
- `kb_id`
- `kb`
- `components`

Sensitive keys such as `api_key`, `token`, `password`, and `*_secret` are removed by default.
