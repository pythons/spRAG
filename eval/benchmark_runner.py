import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class RunResult:
    name: str
    metrics: Dict[str, float]


@dataclass
class BenchmarkConfig:
    name: str
    baseline: str
    runs: List[RunResult]
    lower_is_better: List[str]
    domain: str = "general"
    dataset_version: str = "unknown"
    run_id: str = "unknown"


@dataclass
class ThresholdRule:
    metric: str
    direction: str
    max_regression_pct: float


def load_config(path: Path) -> BenchmarkConfig:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    runs = [RunResult(name=r["name"], metrics=r["metrics"]) for r in data["runs"]]
    return BenchmarkConfig(
        name=data["name"],
        baseline=data["baseline"],
        runs=runs,
        lower_is_better=data.get("lower_is_better", []),
        domain=data.get("domain", "general"),
        dataset_version=data.get("dataset_version", "unknown"),
        run_id=data.get("run_id", "unknown"),
    )


def load_thresholds(path: Path) -> List[ThresholdRule]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [
        ThresholdRule(
            metric=item["metric"],
            direction=item["direction"],
            max_regression_pct=float(item["max_regression_pct"]),
        )
        for item in data.get("thresholds", [])
    ]


def normalize_scores(config: BenchmarkConfig) -> Dict[str, float]:
    metric_names = sorted({m for run in config.runs for m in run.metrics.keys()})
    by_metric = {
        m: [run.metrics[m] for run in config.runs if m in run.metrics]
        for m in metric_names
    }
    score_by_run: Dict[str, float] = {run.name: 0.0 for run in config.runs}

    for metric in metric_names:
        values = by_metric[metric]
        if not values:
            continue
        vmin, vmax = min(values), max(values)
        denom = (vmax - vmin) if vmax != vmin else 1.0
        lower_better = metric in config.lower_is_better
        for run in config.runs:
            if metric not in run.metrics:
                continue
            value = run.metrics[metric]
            normalized = (vmax - value) / denom if lower_better else (value - vmin) / denom
            score_by_run[run.name] += normalized
    return score_by_run


def find_run(config: BenchmarkConfig, run_name: str) -> RunResult:
    run = next((r for r in config.runs if r.name == run_name), None)
    if run is None:
        raise ValueError(f"Run '{run_name}' not found")
    return run


def delta_vs_baseline(
    config: BenchmarkConfig,
    baseline_name: Optional[str] = None,
) -> Dict[str, Dict[str, Dict[str, float | str]]]:
    baseline = find_run(config, baseline_name or config.baseline)
    metric_names = sorted({m for run in config.runs for m in run.metrics.keys()})
    output: Dict[str, Dict[str, Dict[str, float | str]]] = {}

    for run in config.runs:
        if run.name == baseline.name:
            continue
        per_metric: Dict[str, Dict[str, float | str]] = {}
        for metric in metric_names:
            if metric not in run.metrics or metric not in baseline.metrics:
                continue
            base_value = baseline.metrics[metric]
            run_value = run.metrics[metric]
            delta = run_value - base_value
            denom = abs(base_value) if base_value != 0 else 1.0
            delta_pct = (delta / denom) * 100.0
            lower_better = metric in config.lower_is_better
            improved = delta < 0 if lower_better else delta > 0
            per_metric[metric] = {
                "baseline": base_value,
                "value": run_value,
                "delta": delta,
                "delta_pct": delta_pct,
                "direction": "improved" if improved else "regressed",
            }
        output[run.name] = per_metric
    return output


def evaluate_thresholds(
    delta_output: Dict[str, Dict[str, Dict[str, float | str]]],
    rules: List[ThresholdRule],
) -> Tuple[bool, List[dict]]:
    violations: List[dict] = []
    for run_name, metric_map in delta_output.items():
        for rule in rules:
            if rule.metric not in metric_map:
                continue
            metric_delta = metric_map[rule.metric]
            direction = metric_delta["direction"]
            if direction != "regressed":
                continue
            regression_pct = abs(float(metric_delta["delta_pct"]))
            if regression_pct > rule.max_regression_pct:
                violations.append(
                    {
                        "run": run_name,
                        "metric": rule.metric,
                        "direction": rule.direction,
                        "regression_pct": regression_pct,
                        "threshold_pct": rule.max_regression_pct,
                    }
                )
    return (len(violations) == 0, violations)


def compare_versions(
    current_config: BenchmarkConfig,
    previous_config: BenchmarkConfig,
    baseline_name: str,
) -> Dict[str, Dict[str, Dict[str, float | str]]]:
    current_baseline = find_run(current_config, baseline_name)
    previous_baseline = find_run(previous_config, baseline_name)
    shared_metrics = sorted(
        set(current_baseline.metrics.keys()).intersection(previous_baseline.metrics.keys())
    )
    comparison: Dict[str, Dict[str, Dict[str, float | str]]] = {baseline_name: {}}
    for metric in shared_metrics:
        current_value = current_baseline.metrics[metric]
        previous_value = previous_baseline.metrics[metric]
        delta = current_value - previous_value
        denom = abs(previous_value) if previous_value != 0 else 1.0
        delta_pct = (delta / denom) * 100.0
        lower_better = metric in current_config.lower_is_better
        improved = delta < 0 if lower_better else delta > 0
        comparison[baseline_name][metric] = {
            "previous": previous_value,
            "current": current_value,
            "delta": delta,
            "delta_pct": delta_pct,
            "direction": "improved" if improved else "regressed",
        }
    return comparison


def render_markdown(
    config: BenchmarkConfig,
    baseline_name: Optional[str] = None,
    version_compare: Optional[Dict[str, Dict[str, Dict[str, float | str]]]] = None,
) -> str:
    selected_baseline = baseline_name or config.baseline
    baseline = find_run(config, selected_baseline)
    metric_names = sorted({m for run in config.runs for m in run.metrics.keys()})
    scores = normalize_scores(config)
    best_run = max(scores.items(), key=lambda kv: kv[1])[0] if scores else "n/a"
    delta_output = delta_vs_baseline(config, selected_baseline)

    lines: List[str] = []
    lines.append(f"# Benchmark Report: {config.name}")
    lines.append("")
    lines.append(f"- Baseline: `{selected_baseline}`")
    lines.append(f"- Domain: `{config.domain}`")
    lines.append(f"- Dataset version: `{config.dataset_version}`")
    lines.append(f"- Run ID: `{config.run_id}`")
    lines.append(f"- Runs: `{len(config.runs)}`")
    lines.append(f"- Metrics: `{', '.join(metric_names)}`")
    lines.append(f"- Aggregate winner: `{best_run}`")
    lines.append("")
    lines.append("## Raw Metrics")
    lines.append("")
    lines.append("| Run | " + " | ".join(metric_names) + " | Score |")
    lines.append("|---|" + "|".join(["---"] * (len(metric_names) + 1)) + "|")
    for run in config.runs:
        values = [f"{run.metrics.get(m, float('nan')):.6g}" for m in metric_names]
        lines.append(f"| {run.name} | " + " | ".join(values) + f" | {scores.get(run.name, 0.0):.4f} |")

    lines.append("")
    lines.append("## Delta vs Baseline")
    lines.append("")
    lines.append("| Run | Metric | Delta | Delta % | Direction |")
    lines.append("|---|---|---:|---:|---|")
    for run_name, metric_map in delta_output.items():
        for metric, values in metric_map.items():
            lines.append(
                f"| {run_name} | {metric} | {values['delta']:.6g} | {values['delta_pct']:.3f}% | {values['direction']} |"
            )

    if version_compare:
        lines.append("")
        lines.append("## Version Compare (Current vs Previous)")
        lines.append("")
        lines.append("| Run | Metric | Previous | Current | Delta | Delta % | Direction |")
        lines.append("|---|---|---:|---:|---:|---:|---|")
        for run_name, metric_map in version_compare.items():
            for metric, values in metric_map.items():
                lines.append(
                    f"| {run_name} | {metric} | {values['previous']:.6g} | {values['current']:.6g} | {values['delta']:.6g} | {values['delta_pct']:.3f}% | {values['direction']} |"
                )

    lines.append("")
    return "\n".join(lines)


def build_summary(
    config: BenchmarkConfig,
    baseline_name: str,
    delta_output: Dict[str, Dict[str, Dict[str, float | str]]],
    threshold_result: Optional[Tuple[bool, List[dict]]] = None,
    version_compare: Optional[Dict[str, Dict[str, Dict[str, float | str]]]] = None,
) -> dict:
    passed = True
    violations: List[dict] = []
    if threshold_result is not None:
        passed, violations = threshold_result
    return {
        "name": config.name,
        "domain": config.domain,
        "dataset_version": config.dataset_version,
        "run_id": config.run_id,
        "baseline": baseline_name,
        "delta_vs_baseline": delta_output,
        "version_compare": version_compare or {},
        "gate": {
            "passed": passed,
            "violations": violations,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate benchmark comparison report")
    parser.add_argument("--config", required=True, help="Path to benchmark config JSON")
    parser.add_argument("--output", required=False, help="Optional output markdown file")
    parser.add_argument("--baseline-run", required=False, help="Override baseline run name")
    parser.add_argument(
        "--compare-with",
        required=False,
        help="Optional previous benchmark config JSON for version compare",
    )
    parser.add_argument(
        "--output-json",
        required=False,
        help="Optional summary JSON output path (for CI gates)",
    )
    parser.add_argument(
        "--threshold-config",
        required=False,
        help="Optional threshold rules JSON config path",
    )
    parser.add_argument(
        "--enforce-thresholds",
        action="store_true",
        help="Exit non-zero if threshold checks fail",
    )
    args = parser.parse_args()

    config = load_config(Path(args.config))
    baseline_name = args.baseline_run or config.baseline
    find_run(config, baseline_name)

    version_compare = None
    if args.compare_with:
        previous = load_config(Path(args.compare_with))
        version_compare = compare_versions(config, previous, baseline_name)

    delta_output = delta_vs_baseline(config, baseline_name)

    threshold_result = None
    if args.threshold_config:
        rules = load_thresholds(Path(args.threshold_config))
        threshold_result = evaluate_thresholds(delta_output, rules)

    report = render_markdown(config, baseline_name=baseline_name, version_compare=version_compare)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
    else:
        print(report)

    if args.output_json:
        summary = build_summary(
            config=config,
            baseline_name=baseline_name,
            delta_output=delta_output,
            threshold_result=threshold_result,
            version_compare=version_compare,
        )
        out_json = Path(args.output_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.enforce_thresholds and threshold_result is not None:
        passed, _ = threshold_result
        if not passed:
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
