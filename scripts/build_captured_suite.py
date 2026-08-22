#!/usr/bin/env python3
"""Build an offline fixture suite from approved reports that retained raw outputs."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", type=Path)
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    suite = yaml.safe_load(args.suite.read_text(encoding="utf-8"))
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in args.reports]
    captured = copy.deepcopy(suite)
    captured["id"] += "-captured"
    captured["name"] += "（冻结响应）"
    capture_dir = args.output.parent / "captures"
    capture_dir.mkdir(parents=True, exist_ok=True)

    for candidate in captured["candidates"]:
        cases = {}
        for case in captured["cases"]:
            matches = [
                result
                for report in reports
                for report_case in report.get("cases", [])
                if report_case.get("case_id") == case["id"]
                for result in report_case.get("results", [])
                if result.get("candidate_id") == candidate["id"]
                and not result.get("errors")
                and isinstance(result.get("raw_output"), dict)
            ]
            if not matches:
                raise SystemExit(f"no valid captured output for {case['id']}/{candidate['id']}")
            source = matches[0]
            usage = {key: value for key, value in source.get("usage", {}).items() if value is not None}
            cases[case["id"]] = {
                "model_version": candidate["version"],
                "output": source["raw_output"],
                "usage": usage,
                "latency_ms": source["latency_ms"],
            }
        capture_path = capture_dir / f"{candidate['id']}.json"
        capture_path.write_text(json.dumps({"cases": cases}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        candidate["endpoint"] = f"fixture://captures/{capture_path.name}"
        for key in (
            "base_url",
            "api_key_env",
            "model",
            "accepted_observed_models",
            "max_tokens",
            "temperature",
            "response_format",
            "pricing_usd_per_million",
            "timeout_seconds",
        ):
            candidate.pop(key, None)

    args.output.write_text(yaml.safe_dump(captured, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
