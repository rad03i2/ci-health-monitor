from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

SUCCESS = {"success"}
FAILURE = {"failure", "timed_out", "startup_failure", "action_required"}
CANCELLED = {"cancelled", "skipped", "neutral"}

@dataclass(frozen=True)
class Run:
    workflow: str
    status: str
    conclusion: str | None
    created_at: datetime | None
    updated_at: datetime | None
    url: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        if not self.created_at or not self.updated_at:
            return None
        value = (self.updated_at - self.created_at).total_seconds()
        return value if value >= 0 else None

@dataclass(frozen=True)
class WorkflowStats:
    total: int
    success: int
    failed: int
    cancelled: int
    in_progress: int
    success_rate: float | None

@dataclass(frozen=True)
class Report:
    total: int
    success: int
    failed: int
    cancelled: int
    in_progress: int
    success_rate: float | None
    average_duration_seconds: float | None
    p95_duration_seconds: float | None
    consecutive_failures: int
    healthy: bool
    reasons: tuple[str, ...]
    workflows: dict[str, WorkflowStats]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"invalid timestamp: {value!r}") from exc

def _pick(obj: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in obj:
            return obj[name]
    return None

def parse_run(obj: Any) -> Run:
    if not isinstance(obj, dict):
        raise ValueError("each workflow run must be a JSON object")
    workflow = _pick(obj, "workflowName", "workflow_name", "name")
    status = _pick(obj, "status")
    conclusion = _pick(obj, "conclusion")
    if not isinstance(workflow, str) or not workflow.strip():
        raise ValueError("workflow run is missing a workflow name")
    if not isinstance(status, str) or not status.strip():
        raise ValueError(f"workflow {workflow!r} is missing status")
    if conclusion is not None and not isinstance(conclusion, str):
        raise ValueError(f"workflow {workflow!r} has invalid conclusion")
    return Run(
        workflow=workflow.strip(), status=status.strip().lower(),
        conclusion=conclusion.strip().lower() if conclusion else None,
        created_at=_parse_time(_pick(obj, "createdAt", "created_at")),
        updated_at=_parse_time(_pick(obj, "updatedAt", "updated_at")),
        url=_pick(obj, "url", "html_url"),
    )

def load_runs(path: str | Path) -> list[Run]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read input: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc.msg} at line {exc.lineno}") from exc
    if isinstance(payload, dict):
        payload = payload.get("workflow_runs")
    if not isinstance(payload, list):
        raise ValueError("input must be a JSON array or an object containing workflow_runs")
    return [parse_run(item) for item in payload]

def _stats(runs: Iterable[Run]) -> WorkflowStats:
    items = list(runs)
    success = sum(r.conclusion in SUCCESS for r in items)
    failed = sum(r.conclusion in FAILURE for r in items)
    cancelled = sum(r.conclusion in CANCELLED for r in items)
    in_progress = sum(r.conclusion is None for r in items)
    denominator = success + failed
    rate = round(success * 100 / denominator, 2) if denominator else None
    return WorkflowStats(len(items), success, failed, cancelled, in_progress, rate)

def _percentile95(values: list[float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    index = max(0, int((len(values) * 0.95 + 0.999999)) - 1)
    return round(values[min(index, len(values) - 1)], 2)

def analyze_runs(runs: Iterable[Run], *, workflow: str | None = None,
                 min_success_rate: float = 90.0, max_consecutive_failures: int = 2) -> Report:
    if not 0 <= min_success_rate <= 100:
        raise ValueError("min_success_rate must be between 0 and 100")
    if max_consecutive_failures < 0:
        raise ValueError("max_consecutive_failures cannot be negative")
    items = [r for r in runs if workflow is None or r.workflow == workflow]
    overall = _stats(items)
    completed = [r for r in items if r.conclusion is not None]
    completed.sort(key=lambda r: r.created_at or datetime.min, reverse=True)
    consecutive = 0
    for run in completed:
        if run.conclusion in FAILURE:
            consecutive += 1
        else:
            break
    durations = [d for r in completed if (d := r.duration_seconds) is not None]
    reasons: list[str] = []
    if overall.success_rate is not None and overall.success_rate < min_success_rate:
        reasons.append(f"success rate {overall.success_rate:.2f}% is below {min_success_rate:.2f}%")
    if consecutive > max_consecutive_failures:
        reasons.append(f"{consecutive} consecutive failures exceeds limit {max_consecutive_failures}")
    grouped = {name: _stats(r for r in items if r.workflow == name) for name in sorted({r.workflow for r in items})}
    return Report(overall.total, overall.success, overall.failed, overall.cancelled, overall.in_progress,
                  overall.success_rate, round(sum(durations)/len(durations), 2) if durations else None,
                  _percentile95(durations), consecutive, not reasons, tuple(reasons), grouped)
