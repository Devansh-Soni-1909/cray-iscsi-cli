from __future__ import annotations

import os
import re
from typing import List, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import run_pdsh_lines, run_pdsh_text
from .error_collector import collect_node_diagnostics
from .schemas import InitiatorConfigurationError


def _parse_lsblk_iscsi_lines(output: str) -> List[dict]:
    mounts: List[dict] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 2 or parts[-1] != "iscsi":
            continue
        device_name = parts[0]
        middle = parts[1:-1]
        mount_point = ""
        for part in middle:
            if part.startswith("/"):
                mount_point = part
            break
        if mount_point.startswith("/"):
            image_name = os.path.basename(mount_point.rstrip("/"))
        else:
            last_char = device_name[-1]
            lun_number = ord(last_char) - ord("a")
            image_name = f"lun{lun_number}"
        status = "mounted" if mount_point.startswith("/") else "unmounted"
        if not mount_point:
            mount_point = "-"
        mounts.append(
            {
                "device": f"/dev/{device_name}",
                "image_name": image_name,
                "mount_point": mount_point,
                "status": status,
            }
        )
    mounts.sort(key=lambda entry: entry["device"])
    return mounts


def collect_initiator_metrics(node: str) -> dict:
    try:
        output = run_pdsh_text(
            f'pdsh -w {node} "lsblk -o MOUNTPOINT,TRAN --noheadings | grep iscsi || true"'
        )
    except Exception as error:
        raise InitiatorConfigurationError(
            node, f"Unable to collect initiator metrics: {error}"
        )

    lines = [line for line in output.splitlines() if line.strip()]
    total = len(lines)
    mounted = sum(1 for line in lines if line.strip().startswith("/"))
    unmounted = total - mounted

    try:
        session_lines = run_pdsh_lines(
            f'pdsh -w {node} "sudo iscsiadm -m session 2>/dev/null || true"'
        )
    except Exception as sessions_error:
        raise InitiatorConfigurationError(
            node, f"Unable to collect active sessions: {sessions_error}"
        )

    sessions = len([line for line in session_lines if line.strip()])

    try:
        details_output = run_pdsh_text(
            f'pdsh -w {node} "sudo iscsiadm -m session -P 3 2>/dev/null || true"'
        )
    except Exception as session_details_error:
        raise InitiatorConfigurationError(
            node, f"Unable to collect session details: {session_details_error}"
        )

    session_details = []

    current = None
    current_lun = None

    for line in details_output.splitlines():
        line = line.strip()

        if line.startswith("Target:"):
            if current:
                current["lun_count"] = len(current["devices"])
                session_details.append(current)

            target = line[len("Target:") :].split(" (")[0].strip()

            current = {
                "target": target,
                "portal": "",
                "sid": "",
                "connection_state": "",
                "session_state": "",
                "host": "",
                "devices": [],
            }
            current_lun = None

        elif current is None:
            continue

        elif line.startswith("Current Portal:"):
            current["portal"] = line.split(":", 1)[1].strip()

        elif line.startswith("SID:"):
            current["sid"] = line.split(":", 1)[1].strip()

        elif line.startswith("iSCSI Connection State:"):
            current["connection_state"] = line.split(":", 1)[1].strip()

        elif line.startswith("iSCSI Session State:"):
            current["session_state"] = line.split(":", 1)[1].strip()

        elif "Lun:" in line:
            match = re.search(r"Lun:\s*(\d+)", line)
            if match:
                current_lun = int(match.group(1))

        elif "Attached scsi disk" in line:
            match = re.search(r"Attached scsi disk\s+(\S+)", line)
            if match:
                current["devices"].append(
                    {
                        "lun": current_lun,
                        "disk": match.group(1),
                    }
                )

    if current:
        current["lun_count"] = len(current["devices"])
        session_details.append(current)

    return {
        "total": total,
        "mounted": mounted,
        "unmounted": unmounted,
        "sessions": sessions,
        "session_lines": [line for line in session_lines if line.strip()],
        "session_details": session_details,
    }


def collect_initiator_mount_entries(node: str) -> List[dict]:
    try:
        output = run_pdsh_text(
            f'pdsh -w {node} "lsblk -o NAME,LABEL,MOUNTPOINT,TRAN --noheadings 2>/dev/null | grep iscsi || true"'
        )
        return _parse_lsblk_iscsi_lines(output)
    except Exception as error:
        raise InitiatorConfigurationError(
            node, f"Unable to collect mount status: {error}"
        )


def build_initiator_node_summary(node: str) -> dict:
    errors: List[str] = []
    stats = {}
    try:
        stats = collect_initiator_metrics(node)
    except Exception as exc:
        errors.append(str(exc))

    diagnostics = []
    try:
        diagnostics, diagnostic_errors = collect_node_diagnostics(node)
        errors.extend(diagnostic_errors)
    except Exception as exc:
        errors.append(str(exc))

    return {
        "node": node,
        "role": "initiator",
        "sessions": stats.get("sessions", 0),
        "total": stats.get("total", 0),
        "mounted": stats.get("mounted", 0),
        "unmounted": stats.get("unmounted", 0),
        "session_lines": stats.get("session_lines", []),
        "session_details": stats.get("session_details", []),
        "diagnostics": [diagnostic.__dict__ for diagnostic in diagnostics],
        "errors": errors,
    }


def build_initiator_mount_status(node: str) -> dict:
    errors: List[str] = []
    mounts = []
    try:
        mounts = collect_initiator_mount_entries(node)
    except Exception as exc:
        errors.append(str(exc))

    mounted = sum(1 for entry in mounts if entry["status"] == "mounted")
    unmounted = sum(1 for entry in mounts if entry["status"] == "unmounted")
    return {
        "node": node,
        "role": "initiator",
        "mounted": mounted,
        "unmounted": unmounted,
        "mounts": mounts,
        "errors": errors,
    }


def collect_initiator_summaries_concurrently(nodes: Sequence[str]) -> List[dict]:
    if not nodes:
        return []
    results: List[dict] = []
    with ThreadPoolExecutor(max_workers=min(32, len(nodes))) as executor:
        futures = {
            executor.submit(build_initiator_node_summary, node): node for node in nodes
        }
        for future in as_completed(futures):
            results.append(future.result())
    order = {node: index for index, node in enumerate(nodes)}
    results.sort(key=lambda item: order.get(item.get("node", ""), 0))
    return results


def collect_initiator_mount_status_concurrently(nodes: Sequence[str]) -> List[dict]:
    if not nodes:
        return []
    results: List[dict] = []
    with ThreadPoolExecutor(max_workers=min(32, len(nodes))) as executor:
        futures = {
            executor.submit(build_initiator_mount_status, node): node for node in nodes
        }
        for future in as_completed(futures):
            results.append(future.result())
    order = {node: index for index, node in enumerate(nodes)}
    results.sort(key=lambda item: order.get(item.get("node", ""), 0))
    return results
