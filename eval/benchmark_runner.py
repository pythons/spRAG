import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


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


def load_config(path: Path) -> BenchmarkConfig:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    runs = [RunResult(name=r["name"], metrics=r["metrics"]) for r in data["runs"]]
    return BenchmarkConfig(
        name=data["name"],
        baseline=data["baseline"],
        runs=runs,
        lower_is_better=data.get("lower_is_better", []),
    )


def normalize_scores(config: BenchmarkConfig) -> Dict[str, float]:
    metric_names = sorted({m for run in config.runs for m in run.metrics.keys()})
    by_metric = {m: [run.metrics[m] for run in config.runs if m in run.metrics] for m in metric_names}
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
            v = run.metrics[metric]
            if lower_better:
                normalized = (vmax - v) / denom
            else:
                normalized = (v - vmin) / denom
            score_by_run[run.name] += normalized
    return score_by_run


def render_markdown(config: BenchmarkConfig) -> str:
    baseline = next((r for r in config.runs if r.name == config.baseline), None)
    if baseline is None:
        raise ValueError(f"Baseline '{config.baseline}' not found in runs")

    metric_names = sorted({m for run in config.runs for m in run.metrics.keys()})
    scores = normalize_scores(config)
    best_run = max(scores.items(), key=lambda kv: kv[1])[0] if scores else "n/a"

    lines: List[str] = []
    lines.append(f"# Benchmark Report: {config.name}")
    lines.append("")
    lines.append(f"- Baseline: `{config.baseline}`")
    lines.append(f"- Runs: `{len(config.runs)}`")
    lines.append(f"- Metrics: `{', '.join(metric_names)}`")
    lines.append(f"- Aggregate winner: `{best_run}`")
    lines.append("")
    lines.append("## Raw Metrics")
    lines.append("")
    lines.append("| Run | " + " | ".join(metric_names) + " | Score |")
    lines.append("|---|" + "|".join(["---"] * (len(metric_names) + 1)) + "|")
    for run in config.runs:
        vals = [f"{run.metrics.get(m, float('nan')):.6g}" for m in metric_names]
        lines.append(f"| {run.name} | " + " | ".join(vals) + f" | {scores.get(run.name, 0.0):.4f} |")

    lines.append("")
    lines.append("## Delta vs Baseline")
    lines.append("")
    lines.append("| Run | Metric | Delta | Direction |")
    lines.append("|---|---|---:|---|")
    for run in config.runs:
        if run.name == baseline.name:
            continue
        for metric in metric_names:
            if metric not in run.metrics or metric not in baseline.metrics:
                continue
            delta = run.metrics[metric] - baseline.metrics[metric]
            lower_better = metric in config.lower_is_better
            improved = delta < 0 if lower_better else delta > 0
            direction = "improved" if improved else "regressed"
            lines.append(f"| {run.name} | {metric} | {delta:.6g} | {direction} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate benchmark comparison report")
    parser.add_argument("--config", required=True, help="Path to benchmark config JSON")
    parser.add_argument("--output", required=False, help="Optional output markdown file")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    report = render_markdown(config)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
