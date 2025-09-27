"""Simple in-process metrics collector.

The real system would push metrics to a monitoring backend. For this
exercise we keep them in memory so the ``/metrics`` endpoint can expose
prometheus-style text as well as structured JSON used by the System
Health widgets.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Deque, Dict


@dataclass
class RequestMetric:
    """Aggregated information for a single request path."""

    count: int = 0
    failures: int = 0
    durations: Deque[float] = field(default_factory=lambda: deque(maxlen=500))


@dataclass
class JobMetric:
    """Stores duration history for nightly jobs."""

    durations: Deque[float] = field(default_factory=lambda: deque(maxlen=30))
    last_success: bool = True
    last_error: str | None = None


class MetricsCollector:
    """Thread-safe metric store used across the app."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: Dict[str, RequestMetric] = defaultdict(RequestMetric)
        self._jobs: Dict[str, JobMetric] = defaultdict(JobMetric)
        self._imap = {"success": 0, "fail": 0}
        self._smtp = {"success": 0, "fail": 0}
        self._open_ticket_count: int = 0

    # ------------------------------------------------------------------
    # Request metrics
    # ------------------------------------------------------------------
    def record_request(self, path: str, duration: float, success: bool) -> None:
        with self._lock:
            metric = self._requests[path]
            metric.count += 1
            if not success:
                metric.failures += 1
            metric.durations.append(duration)

    def _request_snapshot(self) -> Dict[str, Dict[str, float]]:
        snapshot: Dict[str, Dict[str, float]] = {}
        with self._lock:
            for path, metric in self._requests.items():
                durations = list(metric.durations)
                if durations:
                    sorted_durations = sorted(durations)
                    index = max(int(len(sorted_durations) * 0.95) - 1, 0)
                    p95 = sorted_durations[index]
                    avg = sum(sorted_durations) / len(sorted_durations)
                else:
                    p95 = 0.0
                    avg = 0.0
                snapshot[path] = {
                    "count": metric.count,
                    "failures": metric.failures,
                    "p95": p95,
                    "avg": avg,
                }
        return snapshot

    # ------------------------------------------------------------------
    # Job metrics
    # ------------------------------------------------------------------
    def record_job(self, job_name: str, duration: float, success: bool, error: str | None = None) -> None:
        with self._lock:
            metric = self._jobs[job_name]
            metric.durations.append(duration)
            metric.last_success = success
            metric.last_error = error

    def _job_snapshot(self) -> Dict[str, Dict[str, float | bool | str | None]]:
        snapshot: Dict[str, Dict[str, float | bool | str | None]] = {}
        with self._lock:
            for name, metric in self._jobs.items():
                durations = list(metric.durations)
                avg = sum(durations) / len(durations) if durations else 0.0
                snapshot[name] = {
                    "avg_duration": avg,
                    "last_duration": durations[-1] if durations else 0.0,
                    "last_success": metric.last_success,
                    "last_error": metric.last_error,
                }
        return snapshot

    # ------------------------------------------------------------------
    # Email/Ticket helpers
    # ------------------------------------------------------------------
    def record_email_attempt(self, protocol: str, success: bool) -> None:
        target = self._imap if protocol.lower() == "imap" else self._smtp
        key = "success" if success else "fail"
        with self._lock:
            target[key] += 1

    def set_open_ticket_count(self, count: int) -> None:
        with self._lock:
            self._open_ticket_count = count

    # ------------------------------------------------------------------
    # Snapshot / Export
    # ------------------------------------------------------------------
    def snapshot(self) -> Dict[str, object]:
        return {
            "requests": self._request_snapshot(),
            "jobs": self._job_snapshot(),
            "imap": self._imap.copy(),
            "smtp": self._smtp.copy(),
            "open_tickets": self._open_ticket_count,
        }

    def render_prometheus(self) -> str:
        data = self.snapshot()
        lines = ["# HELP http_requests_total Total HTTP requests", "# TYPE http_requests_total counter"]
        for path, info in data["requests"].items():
            lines.append(f'http_requests_total{{path="{path}"}} {info["count"]}')
            lines.append(f'http_requests_failures_total{{path="{path}"}} {info["failures"]}')
            lines.append(f'http_request_duration_seconds_avg{{path="{path}"}} {info["avg"]}')
            lines.append(f'http_request_duration_seconds_p95{{path="{path}"}} {info["p95"]}')
        lines.append("# HELP nightly_job_duration_seconds Average job duration")
        lines.append("# TYPE nightly_job_duration_seconds gauge")
        for job, info in data["jobs"].items():
            lines.append(f'nightly_job_duration_seconds{{job="{job}"}} {info["avg_duration"]}')
            success = 1 if info["last_success"] else 0
            lines.append(f'nightly_job_last_success{{job="{job}"}} {success}')
        lines.append("# HELP email_attempts_total Email send/receive attempts")
        lines.append("# TYPE email_attempts_total counter")
        lines.append(f'email_attempts_total{{protocol="imap",result="success"}} {data["imap"]["success"]}')
        lines.append(f'email_attempts_total{{protocol="imap",result="fail"}} {data["imap"]["fail"]}')
        lines.append(f'email_attempts_total{{protocol="smtp",result="success"}} {data["smtp"]["success"]}')
        lines.append(f'email_attempts_total{{protocol="smtp",result="fail"}} {data["smtp"]["fail"]}')
        lines.append("# HELP open_tickets Number of open tickets")
        lines.append("# TYPE open_tickets gauge")
        lines.append(f'open_tickets {data["open_tickets"]}')
        return "\n".join(lines)


metrics_collector = MetricsCollector()
