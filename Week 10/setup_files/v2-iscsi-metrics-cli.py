from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set
from urllib.error import URLError
from urllib.request import urlopen

from kubernetes import client, config
from kubernetes.client import CoreV1Api
from kubernetes.client.rest import ApiException

DEFAULT_NAMESPACE = "iscsi"
DEFAULT_NODE_LABEL = "node-role.kubernetes.io/iscsi-target=true"
DEFAULT_POD_LABEL = "app=iscsi-target-http"
DEFAULT_STATE_FILE = Path.cwd() / ".cache" / "iscsi-metrics" / "state.json"


class CliError(RuntimeError):
    pass


def build_core_v1() -> CoreV1Api:
    try:
        config.load_kube_config()
    except Exception:
        try:
            config.load_incluster_config()
        except Exception as exc:
            raise CliError("Could not load Kubernetes config.") from exc
    return client.CoreV1Api()


def get_iscsi_target_nodes(v1: CoreV1Api, node_label: str) -> List[str]:
    try:
        payload = v1.list_node(label_selector=node_label)
    except ApiException as exc:
        raise CliError(f"Failed to list nodes: {exc}") from exc
    return sorted(
        item.metadata.name
        for item in payload.items
        if item.metadata and item.metadata.name
    )


def get_daemonset_pods(
    v1: CoreV1Api, namespace: str, pod_label: str
) -> Dict[str, Dict[str, str]]:
    try:
        payload = v1.list_namespaced_pod(namespace=namespace, label_selector=pod_label)
    except ApiException as exc:
        raise CliError(f"Failed to list pods: {exc}") from exc

    mapping: Dict[str, Dict[str, str]] = {}
    for item in payload.items:
        metadata = item.metadata
        spec = item.spec
        status = item.status
        phase = status.phase if status else None
        pod_name = metadata.name if metadata else None
        node_name = spec.node_name if spec else None
        pod_ip = status.pod_ip if status else None
        if pod_name and node_name and phase == "Running" and pod_ip:
            mapping[node_name] = {"pod_name": pod_name, "pod_ip": pod_ip}
    return mapping


def get_metrics_raw_from_pod_ip(pod_ip: str) -> dict:
    url = f"http://{pod_ip}:9000/metrics/raw"
    try:
        with urlopen(url, timeout=12) as resp:
            output = resp.read().decode("utf-8")
    except URLError as exc:
        raise CliError(f"HTTP request failed for {url}: {exc}") from exc
    except Exception as exc:
        raise CliError(f"Unable to query endpoint {url}: {exc}") from exc

    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        raise CliError(f"Endpoint {url} returned non-JSON response")

    if payload.get("status") != "success":
        raise CliError(f"Endpoint {url} error response: {payload}")

    return payload.get("metrics", {})


def choose_workers(all_workers: List[str], node_arg: str) -> List[str]:
    if node_arg.lower() == "all":
        return all_workers
    requested = [n.strip() for n in node_arg.split(",") if n.strip()]
    missing = sorted(set(requested) - set(all_workers))
    if missing:
        raise CliError("Requested node(s) not found: " + ", ".join(missing))
    return sorted(set(requested))


def extract_node_image_set(metrics: dict) -> Set[str]:
    image_ids: Set[str] = set()
    iscsi = metrics.get("iscsi", {})
    if not isinstance(iscsi, dict):
        return image_ids
    for iqn, iqn_data in iscsi.items():
        if not isinstance(iqn_data, dict):
            continue
        tpgt_1 = iqn_data.get("tpgt_1")
        if not isinstance(tpgt_1, dict):
            continue
        lun_root = tpgt_1.get("lun")
        if not isinstance(lun_root, dict):
            continue
        for lun_name, lun_data in lun_root.items():
            if not (isinstance(lun_name, str) and lun_name.startswith("lun_")):
                continue
            identity = None
            if isinstance(lun_data, dict):
                for _, value in lun_data.items():
                    if isinstance(value, str) and value.startswith("symlink ->"):
                        target = value.split("->", 1)[1].strip()
                        if "/target/core/" in target:
                            identity = target.split("/")[-1]
                            break
            if not identity:
                identity = f"{iqn}:{lun_name}"
            image_ids.add(identity)
    return image_ids


def extract_lun_io_stats(metrics: dict) -> Dict[str, Dict]:
    lun_stats = {}
    iscsi = metrics.get("iscsi", {})
    if not isinstance(iscsi, dict):
        return lun_stats
    for iqn, iqn_data in iscsi.items():
        if not isinstance(iqn_data, dict):
            continue
        tpgt_1 = iqn_data.get("tpgt_1")
        if not isinstance(tpgt_1, dict):
            continue
        lun_root = tpgt_1.get("lun")
        if not isinstance(lun_root, dict):
            continue
        for lun_name, lun_data in lun_root.items():
            if not (isinstance(lun_name, str) and lun_name.startswith("lun_")):
                continue
            stats = lun_data.get("statistics", {})
            scsi_tgt = stats.get("scsi_tgt_port", {})
            read_mb = scsi_tgt.get("read_mbytes", 0)
            write_mb = scsi_tgt.get("write_mbytes", 0)
            lun_stats[lun_name] = {
                "read_mbytes": read_mb,
                "write_mbytes": write_mb,
                "num_cmds": read_mb + write_mb,
            }
    return lun_stats


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "nodes": {}}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("version", 1)
                data.setdefault("nodes", {})
                return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"version": 1, "nodes": {}}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def update_deleted_counters(
    state: dict,
    current_node_images: Dict[str, Set[str]],
    workers: List[str],
) -> Dict[str, int]:
    nodes_state = state.setdefault("nodes", {})
    deleted_counts: Dict[str, int] = {}
    for worker in workers:
        prev = nodes_state.get(worker, {})
        prev_images = set(prev.get("images", [])) if isinstance(prev, dict) else set()
        prev_deleted = (
            int(prev.get("deleted_count", 0)) if isinstance(prev, dict) else 0
        )
        current_images = current_node_images.get(worker, set())
        removed = prev_images - current_images
        deleted_count = prev_deleted + len(removed)
        nodes_state[worker] = {
            "images": sorted(current_images),
            "deleted_count": deleted_count,
            "last_seen": datetime.now(timezone.utc).isoformat(),
        }
        deleted_counts[worker] = deleted_count
    return deleted_counts


def format_report(
    workers: List[str],
    projected_per_worker: Dict[str, int],
    total_projected: int,
    deleted_per_worker: Dict[str, int],
    lun_io_per_worker: Dict[str, Dict],
) -> str:
    lines: List[str] = []
    lines.append("iSCSI Utility Metrics")
    lines.append("=" * 70)
    lines.append("1) List of workers configured as iSCSI targets")
    lines.append("   " + (", ".join(workers) if workers else "None"))
    lines.append("")
    lines.append("2) Number of projected rootfs/PE images per worker node")
    if workers:
        for worker in workers:
            lines.append(f"   - {worker}: {projected_per_worker.get(worker, 0)}")
    else:
        lines.append("   None")
    lines.append("")
    lines.append(f"3) Total number of images projected: {total_projected}")
    lines.append("")
    lines.append("4) Number of deleted images per worker node")
    if workers:
        for worker in workers:
            lines.append(f"   - {worker}: {deleted_per_worker.get(worker, 0)}")
    else:
        lines.append("   None")
    lines.append("")
    lines.append("5) LUN I/O Stats per worker node")
    if workers:
        for worker in workers:
            lines.append(f"\n  {worker}:")
            lun_stats = lun_io_per_worker.get(worker, {})
            if not lun_stats:
                lines.append("    No LUN stats available")
            else:
                for lun_name in sorted(lun_stats.keys()):
                    s = lun_stats[lun_name]
                    lines.append(
                        f"    {lun_name}:  "
                        f"read={s['read_mbytes']} MB  "
                        f"write={s['write_mbytes']} MB  "
                        f"num_cmds={s['num_cmds']}"
                    )
    else:
        lines.append("   None")
    lines.append("")
    lines.append(
        "Note: Deleted-image counters are tracked by this CLI state file over time."
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch iSCSI utility metrics from iscsi-target daemonset pods"
    )
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    parser.add_argument("--node-label", default=DEFAULT_NODE_LABEL)
    parser.add_argument("--pod-label", default=DEFAULT_POD_LABEL)
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--node", default="all")
    parser.add_argument("--list-nodes", action="store_true")
    parser.add_argument("--no-state-update", action="store_true")
    parser.add_argument("--reset-state", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    state_path = Path(args.state_file).expanduser()

    if args.reset_state:
        save_state(state_path, {"version": 1, "nodes": {}})
        print(f"State reset: {state_path}")
        return 0

    try:
        v1 = build_core_v1()
        all_workers = get_iscsi_target_nodes(v1, args.node_label)
        pods_by_node = get_daemonset_pods(v1, args.namespace, args.pod_label)

        workers = choose_workers(all_workers, args.node)

        current_node_images: Dict[str, Set[str]] = {}
        lun_io_per_worker: Dict[str, Dict] = {}
        errors: Dict[str, str] = {}

        for worker in workers:
            pod_info = pods_by_node.get(worker)
            if not pod_info:
                errors[worker] = "No running daemonset pod on node"
                current_node_images[worker] = set()
                continue
            pod_ip = pod_info.get("pod_ip")
            if not pod_ip:
                errors[worker] = "Daemonset pod has no pod IP"
                current_node_images[worker] = set()
                continue
            try:
                metrics = get_metrics_raw_from_pod_ip(pod_ip)
                current_node_images[worker] = extract_node_image_set(metrics)
                lun_io_per_worker[worker] = extract_lun_io_stats(metrics)
            except CliError as exc:
                errors[worker] = str(exc)
                current_node_images[worker] = set()

        projected_per_worker = {
            worker: len(current_node_images.get(worker, set())) for worker in workers
        }
        total_projected = sum(projected_per_worker.values())

        state = load_state(state_path)
        if args.no_state_update:
            deleted_per_worker = {
                worker: int(
                    state.get("nodes", {}).get(worker, {}).get("deleted_count", 0)
                )
                for worker in workers
            }
        else:
            deleted_per_worker = update_deleted_counters(
                state, current_node_images, workers
            )
            save_state(state_path, state)

        if args.json:
            report = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "workers_configured_as_iscsi_targets": workers,
                "projected_images_per_worker": projected_per_worker,
                "total_projected_images": total_projected,
                "deleted_images_per_worker": deleted_per_worker,
                "lun_io_stats": {k: v for k, v in lun_io_per_worker.items()},
                "errors": errors,
            }
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(
                format_report(
                    workers,
                    projected_per_worker,
                    total_projected,
                    deleted_per_worker,
                    lun_io_per_worker,
                )
            )
            if errors:
                print("\nWarnings:")
                for node, err in sorted(errors.items()):
                    print(f"- {node}: {err}")
                return 2

        return 0

    except CliError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
