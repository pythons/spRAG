# SDK Facade

`dsrag.sdk` provides a stable v1 interface for managed-style integrations.

## Contract

- Request objects: typed dataclasses (for example `CreateKBRequest`, `QueryRequest`)
- Response envelope:
  - `schema_version`
  - `ok`
  - `data` (success) or `error` (failure)
- Error codes:
  - `INVALID_ARGUMENT`
  - `NOT_FOUND`
  - `INTERNAL_ERROR`

## Example

```python
from dsrag import DSRAGSDK, CreateKBRequest, QueryRequest

sdk = DSRAGSDK()
sdk.create_kb(CreateKBRequest(kb_id="sdk_demo"))
result = sdk.query(QueryRequest(kb_id="sdk_demo", search_queries=["What is this?"]))
print(result)
```
