#!/usr/bin/env python3
import argparse
from pathlib import Path


REQUIRED_HEADINGS = [
    "## SDK Contract Compatibility",
    "## Schema and Telemetry Compatibility",
]


def check_release_notes_template(template_path: str) -> list[str]:
    content = Path(template_path).read_text(encoding="utf-8")
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in content]
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate release notes template compatibility sections."
    )
    parser.add_argument(
        "--template",
        default="docs/operations/release-notes-template.md",
        help="Path to the release notes template markdown file.",
    )
    args = parser.parse_args()

    missing = check_release_notes_template(args.template)
    if missing:
        print("Release notes gate failed. Missing required headings:")
        for heading in missing:
            print(f"- {heading}")
        return 1
    print("Release notes gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
