from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmark import BenchmarkError, BenchmarkRunner


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="docbench",
        description="Compare document-analysis models and pipelines on a locked, evidence-grounded corpus.",
    )
    parser.add_argument("suite", type=Path, help="Path to benchmark suite YAML")
    parser.add_argument("--output", type=Path, help="Write the redacted JSON report to this path")
    parser.add_argument(
        "--include-outputs",
        action="store_true",
        help="Include raw model JSON in the report; use only for approved, non-sensitive corpora",
    )
    parser.add_argument(
        "--rescore-report",
        type=Path,
        help="Reapply deterministic scoring to a prior report created with --include-outputs",
    )
    args = parser.parse_args()
    try:
        runner = BenchmarkRunner()
        if args.rescore_report:
            source_report = json.loads(args.rescore_report.read_text(encoding="utf-8"))
            report = runner.rescore(args.suite, source_report, include_outputs=args.include_outputs)
        else:
            report = runner.run(
                args.suite,
                include_outputs=args.include_outputs,
                progress=lambda message: print(message, file=sys.stderr, flush=True),
            )
    except (BenchmarkError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0 if report.get("quality_leaders") else 1
