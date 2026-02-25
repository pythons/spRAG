# Vertical Templates

Vertical templates provide an end-to-end starting point for finance and legal workflows.

Available templates:
- `finance`
- `legal`

## Create a KB from a template

```python
from dsrag import create_kb_from_template

kb = create_kb_from_template(
    "finance",
    kb_id="finance_contracts",
)
```

This applies the template's default `profile` (`finance_default` or `legal_default`).

## Apply ingestion/query defaults

```python
from dsrag import (
    apply_template_to_add_document_kwargs,
    apply_template_to_query_kwargs,
)

add_kwargs = apply_template_to_add_document_kwargs(
    "legal",
    {"chunking_config": {"chunk_size": 1000}},
)
query_kwargs = apply_template_to_query_kwargs(
    "legal",
    {"rse_params": "precise"},
)
```

User values override template defaults.

## Query with template defaults

```python
from dsrag import query_with_template

results = query_with_template(
    kb,
    "finance",
    ["What changed in operating margin year over year?"],
)
```
