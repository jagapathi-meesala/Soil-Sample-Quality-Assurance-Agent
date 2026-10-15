from __future__ import annotations
import argparse, json
from pathlib import Path
from .qa import build_report

def main() -> int:
    parser = argparse.ArgumentParser(description="Screen soil sample and lab-result records for QA issues.")
    parser.add_argument("input", help="Input JSON file")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = build_report(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
