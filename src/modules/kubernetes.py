import json
import yaml
from typing import List, Dict
from pathlib import Path

from .schemas import KubernetesError
from .utils import run_command

DEFAULT_TARGET_SELECTOR_VALUE = "iscsi-role=target"

CLI_CONFIG_PATH = Path("/etc/iscsi/config.yml")
TARGET_SELECTOR_KEY = "target-selector"


def _load_config() -> dict:
    if not CLI_CONFIG_PATH.exists():
        return {}
    try:
        with CLI_CONFIG_PATH.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        raise KubernetesError(f"Failed to read config file '{CLI_CONFIG_PATH}': {exc}")


def _save_config(config: dict) -> None:
    try:
        CLI_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CLI_CONFIG_PATH.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(config, handle, sort_keys=False)
    except Exception as exc:
        raise KubernetesError(f"Failed to write config file '{CLI_CONFIG_PATH}': {exc}")


def _get_config_value(key: str, default: str) -> str:
    config = _load_config()
    return config.get(key, default)


def _set_config_value(key: str, value: str) -> str:
    config = _load_config()
    config[key] = value
    _save_config(config)
    return value


def get_target_node_label() -> str:
    return _get_config_value(TARGET_SELECTOR_KEY, DEFAULT_TARGET_SELECTOR_VALUE)


def set_target_node_label(label: str) -> str:
    return _set_config_value(TARGET_SELECTOR_KEY, label)


def _matches_selector(labels: dict, selector: str) -> bool:
    if not selector:
        return False
    if "=" in selector:
        key, val = selector.split("=", 1)
        return labels.get(key.strip()) == val.strip()
    else:
        return selector.strip() in labels


def run_kubectl_json(command: str) -> dict:
    result = run_command(command)
    if result.returncode != 0:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"exit {result.returncode}"
        )
        raise KubernetesError(f"kubectl command '{command}' failed: {message}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise KubernetesError(f"Invalid JSON from kubectl command '{command}': {exc}")


# revisit: use sat status --filter role=compute
def get_kubernetes_nodes(
    node_selector: str, full_info: bool = False, initiator: bool = False
) -> List[str] | Dict[str, Dict]:
    if initiator:
        command = "kubectl get nodes -o json"
        result = run_command(command)
        if result.returncode != 0:
            message = (
                result.stderr.strip()
                or result.stdout.strip()
                or f"exit {result.returncode}"
            )
            raise KubernetesError(
                f"Failed to retrieve all nodes for initiator check: {message}"
            )
        try:
            data = json.loads(result.stdout)
            if full_info:
                nodes_data = {}
                for item in data.get("items", []):
                    metadata = item.get("metadata", {})
                    labels = metadata.get("labels", {}) or {}
                    if _matches_selector(labels, node_selector):
                        continue
                    status = item.get("status", {})
                    node_info = status.get("nodeInfo", {})
                    ready_condition = next(
                        (
                            condition
                            for condition in status.get("conditions", [])
                            if condition.get("type") == "Ready"
                        ),
                        None,
                    )
                    uid = metadata.get("uid")
                    nodes_data[uid] = {
                        "name": metadata.get("name"),
                        "addresses": status.get("addresses", []),
                        "node_info": {
                            "arch": node_info.get("architecture"),
                            "os": node_info.get("operatingSystem"),
                            "os_image": node_info.get("osImage"),
                        },
                        "status": (
                            "Ready"
                            if ready_condition and ready_condition.get("status") == "True"
                            else "NotReady"
                        ),
                    }
                return nodes_data
            else:
                names = []
                for item in data.get("items", []):
                    metadata = item.get("metadata", {})
                    labels = metadata.get("labels", {}) or {}
                    if _matches_selector(labels, node_selector):
                        continue
                    names.append(metadata.get("name"))
                return [name for name in names if name]
        except json.JSONDecodeError as exc:
            raise KubernetesError(
                f"Failed to parse JSON for all nodes: {exc}"
            )
    else:
        if full_info:
            command = f"kubectl get nodes -l {node_selector}  -o json"
            result = run_command(command)
            if result.returncode != 0:
                message = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or f"exit {result.returncode}"
                )
                raise KubernetesError(
                    f"Failed to retrieve nodes with selector '{node_selector}': {message}"
                )
            try:
                data = json.loads(result.stdout)
                nodes_data = {}
                for item in data.get("items", []):
                    metadata = item.get("metadata", {})
                    status = item.get("status", {})
                    node_info = status.get("nodeInfo", {})
                    ready_condition = next(
                        (
                            condition
                            for condition in status.get("conditions", [])
                            if condition.get("type") == "Ready"
                        ),
                        None,
                    )
                    uid = metadata.get("uid")
                    nodes_data[uid] = {
                        "name": metadata.get("name"),
                        "addresses": status.get("addresses", []),
                        "node_info": {
                            "arch": node_info.get("architecture"),
                            "os": node_info.get("operatingSystem"),
                            "os_image": node_info.get("osImage"),
                        },
                        "status": (
                            "Ready"
                            if ready_condition and ready_condition.get("status") == "True"
                            else "NotReady"
                        ),
                    }
                return nodes_data
            except json.JSONDecodeError as exc:
                raise KubernetesError(
                    f"Failed to parse JSON for nodes with selector '{node_selector}': {exc}"
                )
        else:
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
                raise KubernetesError(
                    f"Failed to list nodes with selector '{node_selector}': {message}"
                )
            output = result.stdout.replace("'", "").strip()
            return [node for node in output.split() if node]


def get_kubernetes_node_json(node_name: str) -> dict:
    return run_kubectl_json(f"kubectl get node {node_name} -o json")


def get_node_labels(node_name: str) -> Dict[str, str]:
    payload = get_kubernetes_node_json(node_name)
    labels = payload.get("metadata", {}).get("labels", {})
    if not isinstance(labels, dict):
        raise KubernetesError(f"Labels for node '{node_name}' are not a mapping")
    return labels


def detect_node_role(labels: Dict[str, str]) -> str:
    target_selector = get_target_node_label()
    if _matches_selector(labels, target_selector):
        return "target"
    else:
        return "initiator"
