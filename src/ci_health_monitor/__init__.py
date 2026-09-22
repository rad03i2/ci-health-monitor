"""Offline CI health analysis."""
from .core import Report, Run, WorkflowStats, analyze_runs, load_runs, parse_run

__all__ = ["Report", "Run", "WorkflowStats", "analyze_runs", "load_runs", "parse_run"]
__version__ = "1.0.0"