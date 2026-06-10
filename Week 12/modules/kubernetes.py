import json
from typing import Tuple, List, Optional, Dict
from .utils import run_command

DEFAULT_TARGET_SELECTOR = "iscsi-target=true"
DEFAULT_INITIATOR_SELECTOR = "iscsi-role=initiator"


def run_kubectl_json(command: str) -> Tuple[dict, Optional[str]]:
    result = run_command(command)
    if result.returncode != 0:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"exit {result.returncode}"
        )
        return {}, message
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as exc:
        return {}, f"invalid JSON output: {exc}"


def get_kubernetes_nodes(node_selector: str) -> Tuple[List[str], Optional[str]]:
    command = (
        "kubectl get nodes "
        f"-l {node_selector} "
        "-o jsonpath='{.items[*].metadata.name}'"
    )
    result = run_command(command)
    if result.returncode != 0:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"exit {result.returncode}"
        )
        return [], message
    output = result.stdout.replace("'", "").strip()
    return [node for node in output.split() if node], None


def get_node_json(node_name: str) -> Tuple[dict, Optional[str]]:
    return run_kubectl_json(f"kubectl get node {node_name} -o json")


def get_node_labels(node_name: str) -> Tuple[Dict[str, str], Optional[str]]:
    payload, error = get_node_json(node_name)
    if error:
        return {}, error
    labels = payload.get("metadata", {}).get("labels", {})
    if not isinstance(labels, dict):
        return {}, f"{node_name}: labels were not a mapping"
    return labels, None


def detect_node_role(labels: Dict[str, str]) -> str:
    target_value = str(labels.get("iscsi-target", "")).lower()
    role_value = str(labels.get("iscsi-role", "")).lower()
    initiator_value = str(labels.get("iscsi-initiator", "")).lower()
    if target_value in {"true", "yes", "1", "enabled"}:
        return "target"
    if role_value == "initiator" or initiator_value in {"true", "yes", "1", "enabled"}:
        return "initiator"
    return "unknown"
