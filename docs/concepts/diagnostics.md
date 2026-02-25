# Diagnostics

Use diagnostics to quickly identify common setup/runtime issues.

## Quick Check

```python
from dsrag import run_diagnostics

report = run_diagnostics()
print(report)
```

## What it includes
- Python/runtime information
- Optional dependency availability by feature
- Presence checks for common API key environment variables
- Convenience lists of missing dependencies and env vars

Note:
- Environment checks only report whether a variable is set, not its value.
- Missing dependencies are expected if you are not using that integration.
