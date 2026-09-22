from __future__ import annotations
import argparse, json, sys
from .core import analyze_runs, load_runs

VERSION = "1.0.0"

def _duration(value: float | None) -> str:
    if value is None: return "n/a"
    seconds = int(round(value)); minutes, seconds = divmod(seconds, 60); hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes:02d}m {seconds:02d}s" if hours else f"{minutes}m {seconds:02d}s"

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Analyze exported GitHub Actions run history offline.")
    p.add_argument("input", help="JSON file exported from GitHub CLI/API")
    p.add_argument("--workflow", help="analyze only this exact workflow name")
    p.add_argument("--min-success-rate", type=float, default=90.0)
    p.add_argument("--max-consecutive-failures", type=int, default=2)
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument("--version", action="version", version=f"ci-health-monitor {VERSION} — Radwan Abdulhadi Ahmed / @rad03i2")
    return p

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze_runs(load_runs(args.input), workflow=args.workflow,
            min_success_rate=args.min_success_rate, max_consecutive_failures=args.max_consecutive_failures)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        state = "HEALTHY" if report.healthy else "UNHEALTHY"
        print(f"CI Health: {state}")
        print(f"Runs: {report.total} | Success: {report.success} | Failed: {report.failed} | Cancelled: {report.cancelled} | In progress: {report.in_progress}")
        print("Success rate: " + (f"{report.success_rate:.2f}% (completed, non-cancelled)" if report.success_rate is not None else "n/a"))
        print(f"Average duration: {_duration(report.average_duration_seconds)} | P95: {_duration(report.p95_duration_seconds)}")
        print(f"Recent consecutive failures: {report.consecutive_failures}")
        for name, stats in report.workflows.items():
            rate = "n/a" if stats.success_rate is None else f"{stats.success_rate:.2f}%"
            print(f"- {name}: {stats.total} runs, {rate} success")
        for reason in report.reasons: print(f"! {reason}")
    return 0 if report.healthy else 1

if __name__ == "__main__": raise SystemExit(main())