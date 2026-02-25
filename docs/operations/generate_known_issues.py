import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def load_source(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_markdown(data: Dict[str, Any]) -> str:
    statuses: List[Dict[str, str]] = data.get("status_definitions", [])
    items: List[Dict[str, str]] = data.get("items", [])

    lines: List[str] = []
    lines.append("# Known Issues Matrix")
    lines.append("")
    lines.append("## Purpose")
    lines.append("Track high-signal compatibility and reliability issues in one place for users and maintainers.")
    lines.append("")
    lines.append("## Status Definitions")
    for status in statuses:
        lines.append(f"- {status['name']}: {status['description']}")
    lines.append("")
    lines.append("## Matrix")
    lines.append("| Area | Component | Symptom | Workaround | Status |")
    lines.append("|---|---|---|---|---|")
    for item in items:
        lines.append(
            f"| {item['area']} | {item['component']} | {item['symptom']} | {item['workaround']} | {item['status']} |"
        )
    lines.append("")
    lines.append("## Update Policy")
    lines.append("- Refresh at every bi-weekly release")
    lines.append("- Link each row to issue IDs and release notes in PR descriptions")
    lines.append("- Remove rows only after one stable release cycle with no regressions")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate known issues markdown from source data")
    parser.add_argument(
        "--source",
        default="docs/operations/known-issues.yaml",
        help="Path to source data file (JSON-compatible YAML)",
    )
    parser.add_argument(
        "--output",
        default="docs/operations/known-issues-matrix.md",
        help="Markdown output path",
    )
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    data = load_source(source)
    md = render_markdown(data)
    output.write_text(md, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
