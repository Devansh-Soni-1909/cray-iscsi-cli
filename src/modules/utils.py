from __future__ import annotations

import re
import subprocess
from typing import Dict, List, Optional, Sequence, Tuple


def run_command(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(command, shell=True, capture_output=True, text=True)


def _clean_pdsh_output(output: str) -> List[str]:
    lines: List[str] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ": " in line:
            line = line.split(": ", 1)[1].strip()
        if line:
            lines.append(line)
    return lines


def run_pdsh_lines(command: str) -> Tuple[List[str], Optional[str]]:
    result = run_command(command)
    if result.returncode != 0:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"exit {result.returncode}"
        )
        return [], message
    return _clean_pdsh_output(result.stdout), None


def run_pdsh_text(command: str) -> Tuple[str, Optional[str]]:
    lines, error = run_pdsh_lines(command)
    if error:
        return "", error
    return "\n".join(lines).strip(), None


def _parse_pdsh_output_by_node(
    output: str, expected_nodes: Optional[Sequence[str]] = None
) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    expected = set(expected_nodes) if expected_nodes else None
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        if not line or ": " not in line:
            continue
        node, text = line.split(": ", 1)
        node = node.strip()
        if expected is not None and node not in expected:
            continue
        grouped.setdefault(node, []).append(text.strip())
    return grouped


def run_pdsh_text_by_node(
    nodes: Sequence[str], remote_command: str
) -> Tuple[Dict[str, str], Optional[str]]:
    normalized = [node.strip() for node in nodes if node and node.strip()]
    if not normalized:
        return {}, None

    node_expr = ",".join(sorted(set(normalized)))
    result = run_command(f'pdsh -w {node_expr} "{remote_command}"')
    grouped = _parse_pdsh_output_by_node(result.stdout, normalized)
    payload = {
        node: "\n".join(lines).strip()
        for node, lines in grouped.items()
        if "\n".join(lines).strip()
    }

    if result.returncode != 0 and not payload:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"exit {result.returncode}"
        )
        return {}, message

    return payload, None


def parse_metric_value(raw_output: str) -> int:
    if not raw_output:
        return 0
    match = re.search(r"(-?\d+)\s*$", raw_output)
    if not match:
        return 0
    try:
        return int(match.group(1))
    except ValueError:
        return 0
