from __future__ import annotations
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from typing import List, Optional, Tuple
from .schemas import NodeErrorReport
from .utils import (
    run_pdsh_text_by_node,
    run_pdsh_text,
)

ERROR_PATTERNS = [
    {"pattern": r"connection.*lost", "severity": "warning", "source": "iscsi"},
    {"pattern": r"session.*failure", "severity": "warning", "source": "iscsi"},
    {"pattern": r"iscsi.*timed out", "severity": "warning", "source": "network"},
    {"pattern": r"blocked for more than", "severity": "critical", "source": "kernel"},
    {"pattern": r"I/O error", "severity": "critical", "source": "storage"},
    {
        "pattern": r"rejecting I/O to offline device",
        "severity": "critical",
        "source": "storage",
    },
    {"pattern": r"blk_update_request", "severity": "critical", "source": "storage"},
    {"pattern": r"Buffer I/O error", "severity": "critical", "source": "storage"},
    {"pattern": r"link is down", "severity": "warning", "source": "network"},
    {"pattern": r"task .* hung", "severity": "critical", "source": "kernel"},
    {"pattern": r"multipath.*faulty", "severity": "critical", "source": "multipath"},
]


def collect_recent_logs(node: str, lines: int = 200) -> Tuple[str, Optional[str]]:
    commands = [
        f"journalctl -n {lines} --no-pager 2>/dev/null",
        f"tail -n {lines} /var/log/messages 2>/dev/null",
        f"tail -n {lines} /var/log/syslog 2>/dev/null",
        f"dmesg | tail -n {lines}",
    ]
    for command in commands:
        output, error = run_pdsh_text(f'pdsh -w {node} "{command}"')
        if output:
            return output, None
        if error:
            continue
    return "", f"{node}: unable to collect logs"


def collect_service_errors(
    node: str,
    days: int = 2,
    lines: int = 100,
) -> Tuple[dict, List[str]]:
    services = [
        "sbps-marshal.service",
        "target.service",
    ]

    service_logs = {}
    errors = []

    for service in services:
        command = (
            f"journalctl -u {service} "
            f'--since "{days} days ago" '
            f"-p err "
            f"-n {lines} "
            "--no-pager"
        )

        output, error = run_pdsh_text(f'pdsh -w {node} "{command}"')

        if error:
            errors.append(f"{node}: unable to collect errors for {service}: {error}")
            continue

        service_logs[service] = output

    return service_logs, errors


def collect_recent_logs_for_nodes(
    nodes: List[str], lines: int = 200
) -> Tuple[dict, dict]:
    commands = [
        f"journalctl -n {lines} --no-pager 2>/dev/null",
        f"tail -n {lines} /var/log/messages 2>/dev/null",
        f"tail -n {lines} /var/log/syslog 2>/dev/null",
        f"dmesg | tail -n {lines}",
    ]

    logs_by_node: dict = {}
    remaining = {node for node in nodes if node}

    for command in commands:
        if not remaining:
            break
        outputs, _ = run_pdsh_text_by_node(sorted(remaining), command)
        for node, output in outputs.items():
            if output:
                logs_by_node[node] = output
                remaining.discard(node)

    errors_by_node = {
        node: f"{node}: unable to collect logs" for node in sorted(remaining)
    }
    return logs_by_node, errors_by_node


def scan_logs_for_errors(node: str, log_text: str) -> List[NodeErrorReport]:
    findings: List[NodeErrorReport] = []
    for line in log_text.splitlines():
        lowered = line.lower()
        for entry in ERROR_PATTERNS:
            if re.search(entry["pattern"], lowered, re.IGNORECASE):
                findings.append(
                    NodeErrorReport(
                        node=node,
                        source=entry["source"],
                        severity=entry["severity"],
                        message=line.strip(),
                    )
                )
                break
    return findings


def collect_node_diagnostics(node: str) -> Tuple[List[NodeErrorReport], List[str]]:
    logs, log_error = collect_recent_logs(node)
    if log_error:
        return [], [log_error]
    return scan_logs_for_errors(node, logs), []


def collect_error_summary(node: str, lines: int) -> dict:
    logs, log_error = collect_recent_logs(node, lines)
    diagnostics = scan_logs_for_errors(node, logs) if logs else []

    service_errors, service_error_messages = collect_service_errors(
        node=node,
        days=2,
        lines=100,
    )
    return {
        "node": node,
        "lines": lines,
        "log_error": log_error,
        "logs": logs,
        "service_errors": service_errors,
        "service_error_messages": service_error_messages,
        "diagnostics": [asdict(diagnostic) for diagnostic in diagnostics],
    }
