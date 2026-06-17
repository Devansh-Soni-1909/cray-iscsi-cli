from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict

from .kubernetes import (
    CLI_CONFIG_PATH,
    get_target_node_label,
    set_target_node_label,
    get_initiator_node_label,
    set_initator_node_label,
    get_kubernetes_nodes,
    get_node_labels,
    detect_node_role,
)
from .iscsi_target import (
    filter_images,
    collect_target_luns,
    collect_target_images,
    collect_target_tpgts,
    build_target_node_summary,
    collect_summaries_concurrently,
    list_config_versions,
    build_backup_config_summary,
)
from .iscsi_initiator import (
    build_initiator_mount_status,
    build_initiator_node_summary,
    collect_initiator_summaries_concurrently,
    collect_initiator_mount_status_concurrently,
)
from .error_collector import (
    collect_error_summary,
    collect_recent_logs_for_nodes,
    scan_logs_for_errors,
    collect_service_errors,
)

from .formatter import (
    format_nodes_output,
    format_configs_output,
    format_tpgts_output,
    format_luns_output,
    format_images_output,
    format_sessions_output,
    format_mount_status_output,
    format_error_summary,
    format_target_summary,
    format_initiator_summary,
    format_both_summaries,
    format_target_metrics,
    format_initiator_metrics,
    format_both_metrics,
    emit_output,
)

from .schemas import (
    CLIParameterError,
    TargetConfigurationError,
)

try:
    DEFAULT_TARGET_SELECTOR = get_target_node_label()
except Exception:
    DEFAULT_TARGET_SELECTOR = "iscsi-role=target"

try:
    DEFAULT_INITIATOR_SELECTOR = get_initiator_node_label()
except Exception:
    DEFAULT_INITIATOR_SELECTOR = "iscsi-role=initiator"


# get commands


def cmd_get_nodes(args) -> None:
    label = None
    if (args.target and args.initiator) or (not args.target and not args.initiator):
        target_nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR, full_info=True)
        for node in target_nodes.keys():
            target_nodes[node]["role"] = "target"

        initiator_nodes = get_kubernetes_nodes(
            DEFAULT_INITIATOR_SELECTOR, full_info=True
        )
        for node in initiator_nodes.keys():
            initiator_nodes[node]["role"] = "initiator"

        label = f"{DEFAULT_INITIATOR_SELECTOR, DEFAULT_TARGET_SELECTOR}"
        nodes = target_nodes | initiator_nodes
    elif args.target:
        label = DEFAULT_TARGET_SELECTOR
        nodes = get_kubernetes_nodes(label, full_info=True)
        for node in nodes.keys():
            nodes[node]["role"] = "target"
    elif args.initiator:
        label = DEFAULT_INITIATOR_SELECTOR
        nodes = get_kubernetes_nodes(label, full_info=True)
        for node in nodes.keys():
            nodes[node]["role"] = "initiator"

    emit_output(
        {"label": label, "nodes": nodes},
        formatter=format_nodes_output,
        out_file=args.out_file,
    )


def cmd_get_configs(args) -> None:
    if args.name:
        labels = get_node_labels(args.name)
        role = detect_node_role(labels=labels)
        if role != "target":
            raise CLIParameterError(
                f"{args.name}: role is '{role}', this command is only valid for target nodes"
            )
        current, versions = list_config_versions(args.name)
        emit_output(
            [{"node": args.name, "current_config": current, "versions": versions}],
            formatter=format_configs_output,
            out_file=args.out_file,
        )
    else:
        nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)

        def collect_node_config(node: str) -> dict:
            current, versions = list_config_versions(node)
            return {
                "node": node,
                "current_config": current,
                "versions": versions,
            }

        with ThreadPoolExecutor(max_workers=min(32, len(nodes))) as executor:
            payload = list(executor.map(collect_node_config, nodes))

        emit_output(
            payload,
            formatter=format_configs_output,
            out_file=args.out_file,
        )


def cmd_get_luns(args) -> None:
    with_metrics = True if args.metrics else False
    if args.name:
        labels = get_node_labels(args.name)
        role = detect_node_role(labels)
        if role != "target":
            raise CLIParameterError(
                f"{args.name}: role is '{role}', this command is only valid for target nodes"
            )
        luns, _, errors = collect_target_luns(args.name, with_metrics)
        luns = filter_images(luns, args.image_type)
        if errors:
            raise TargetConfigurationError(args.name, "; ".join(errors))
        payload = {
            "node": args.name,
            "role": role,
            "luns": [asdict(lun) for lun in luns],
            "count": len(luns),
            "image_type": args.image_type,
            "with_metrics": with_metrics,
        }
    else:
        nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)
        summaries = collect_summaries_concurrently(nodes, with_metrics)
        if args.image_type != "all":
            for summary in summaries:
                summary["luns"] = [
                    lun
                    for lun in summary.get("luns", [])
                    if lun.get("image", {}).get("image_type") == args.image_type
                ]
        payload = {"nodes": summaries, "with_metrics": with_metrics}
    emit_output(payload, formatter=format_luns_output, out_file=args.out_file)


def cmd_get_tpgts(args) -> None:
    with_metrics = False
    if args.name:
        labels = get_node_labels(args.name)
        role = detect_node_role(labels)
        if role != "target":
            raise CLIParameterError(
                f"{args.name}: role is '{role}', this command is only valid for target nodes"
            )
        tpgts, errors = collect_target_tpgts(args.name, with_metrics)
        if errors:
            raise TargetConfigurationError(args.name, "; ".join(errors))
        payload = {"node": args.name, "role": role, "tpgts": tpgts, "count": len(tpgts)}
    else:
        nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)
        payload = {"nodes": collect_summaries_concurrently(nodes, with_metrics)}
    emit_output(payload, formatter=format_tpgts_output, out_file=args.out_file)


def cmd_get_images(args) -> None:
    with_metrics = True if args.metrics else False
    if args.name:
        labels = get_node_labels(args.name)
        role = detect_node_role(labels)
        if role != "target":
            raise CLIParameterError(
                f"{args.name}: role is '{role}', this command is only valid for target nodes"
            )
        images, tpgts, errors = collect_target_images(args.name, with_metrics)
        if args.image_type != "all":
            images = [img for img in images if img.image_type == args.image_type]
        if errors:
            raise TargetConfigurationError(args.name, "; ".join(errors))
        payload = {
            "node": args.name,
            "role": role,
            "images": [asdict(img) for img in images],
            "tpgts": tpgts,
            "count": len(images),
            "image_type": args.image_type,
            "with_metrics": with_metrics,
        }
    else:
        nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)

        def collect_node_images(node: str) -> dict:
            imgs, node_tpgts, node_errors = collect_target_images(node, with_metrics)
            if args.image_type != "all":
                imgs = [img for img in imgs if img.image_type == args.image_type]
            return {
                "node": node,
                "role": "target",
                "images": [asdict(img) for img in imgs],
                "tpgts": node_tpgts,
                "count": len(imgs),
                "image_type": args.image_type,
                "with_metrics": with_metrics,
                "errors": node_errors,
            }

        with ThreadPoolExecutor(max_workers=min(32, max(1, len(nodes)))) as executor:
            summaries = list(executor.map(collect_node_images, nodes))

        payload = {"nodes": summaries, "with_metrics": with_metrics}
    emit_output(payload, formatter=format_images_output, out_file=args.out_file)


def cmd_get_metrics(args) -> None:
    if args.name:
        node_name = args.name
        labels = get_node_labels(node_name)
        role = detect_node_role(labels)
        if role == "initiator":
            summary = build_initiator_node_summary(node_name)
            emit_output([summary], formatter=format_initiator_metrics)
        elif role == "target":
            summary = build_target_node_summary(
                node_name, with_metrics=True, compare_config=args.config_file
            )
            emit_output(
                [summary], formatter=format_target_metrics, out_file=args.out_file
            )
        else:
            raise CLIParameterError(f"{node_name}: unknown role, cannot fetch metrics")
    else:
        target_nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)
        with ThreadPoolExecutor(max_workers=min(32, len(target_nodes))) as executor:
            target_summaries = list(
                executor.map(build_target_node_summary, target_nodes)
            )

        initiator_nodes = get_kubernetes_nodes(DEFAULT_INITIATOR_SELECTOR)
        with ThreadPoolExecutor(max_workers=min(32, len(initiator_nodes))) as executor:
            initiator_summaries = list(
                executor.map(build_initiator_node_summary, initiator_nodes)
            )
        emit_output(
            payload=(target_summaries, initiator_summaries),
            formatter=format_both_metrics,
            out_file=args.out_file,
        )


def cmd_get_sessions(args) -> None:
    if args.name:
        labels = get_node_labels(args.name)
        role = detect_node_role(labels)
        if role != "initiator":
            raise CLIParameterError(
                f"{args.name}: role is '{role}', this command is only valid for initiator nodes"
            )
        payload = build_initiator_node_summary(args.name)
    else:
        nodes = get_kubernetes_nodes(DEFAULT_INITIATOR_SELECTOR)
        payload = {"nodes": collect_initiator_summaries_concurrently(nodes)}
    emit_output(payload, formatter=format_sessions_output, out_file=args.out_file)


def cmd_get_mount_status(args) -> None:
    if args.name:
        labels = get_node_labels(args.name)
        role = detect_node_role(labels)
        if role != "initiator":
            raise CLIParameterError(
                f"{args.name}: role is '{role}', this command is only valid for initiator nodes"
            )
        payload = build_initiator_mount_status(args.name)
    else:
        nodes = get_kubernetes_nodes(DEFAULT_INITIATOR_SELECTOR)
        payload = {"nodes": collect_initiator_mount_status_concurrently(nodes)}
    emit_output(payload, formatter=format_mount_status_output, out_file=args.out_file)


def cmd_get_errors(args) -> None:
    if args.name:
        payload = collect_error_summary(args.name, args.lines)
    else:
        target_nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)
        initiator_nodes = get_kubernetes_nodes(DEFAULT_INITIATOR_SELECTOR)
        nodes = target_nodes + initiator_nodes
        logs_by_node, errors_by_node = collect_recent_logs_for_nodes(nodes, args.lines)
        payload = {
            "label": f"{DEFAULT_INITIATOR_SELECTOR, DEFAULT_TARGET_SELECTOR}",
            "lines": args.lines,
            "nodes": [],
        }
        with ThreadPoolExecutor() as executor:
            future_map = {
                executor.submit(
                    scan_logs_for_errors, node, logs_by_node.get(node, "")
                ): node
                for node in nodes
            }
            for future in as_completed(future_map):
                node = future_map[future]
                diagnostics = [asdict(item) for item in future.result()]
                service_errors, service_error_messages = collect_service_errors(
                    node=node,
                    days=2,
                    lines=100,
                )
                payload["nodes"].append(
                    {
                        "node": node,
                        "lines": args.lines,
                        "log_error": errors_by_node.get(node),
                        "logs": logs_by_node.get(node, ""),
                        "service_errors": service_errors,
                        "service_error_messages": service_error_messages,
                        "diagnostics": diagnostics,
                    }
                )

    emit_output(payload, formatter=format_error_summary, out_file=args.out_file)


# set commands
def cmd_set_label(args) -> None:
    if args.target:
        set_target_node_label(args.target)
    if args.initiator:
        set_initator_node_label(args.initiator)
    if not args.target and not args.initiator:
        raise CLIParameterError("Provide target/initiator labels")
    print(f"Config saved at {CLI_CONFIG_PATH}")


# describe commands
def cmd_describe_node(args) -> None:
    if args.name:
        node_name = args.name
        labels = get_node_labels(node_name)
        role = detect_node_role(labels)
        if role == "initiator":
            summary = build_initiator_node_summary(node_name)
            emit_output(
                [summary], formatter=format_initiator_summary, out_file=args.out_file
            )
        elif role == "target":
            summary = build_target_node_summary(node_name, with_metrics=False)
            emit_output(
                [summary], formatter=format_target_summary, out_file=args.out_file
            )
        else:
            raise CLIParameterError(f"{node_name}: unknown role, cannot describe")
    else:
        target_nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)
        with ThreadPoolExecutor(max_workers=min(32, len(target_nodes))) as executor:
            target_summaries = list(
                executor.map(build_target_node_summary, target_nodes)
            )

        initiator_nodes = get_kubernetes_nodes(DEFAULT_INITIATOR_SELECTOR)
        with ThreadPoolExecutor(max_workers=min(32, len(initiator_nodes))) as executor:
            initiator_summaries = list(
                executor.map(build_initiator_node_summary, initiator_nodes)
            )
        emit_output(
            payload=(target_summaries, initiator_summaries),
            formatter=format_both_summaries,
            out_file=args.out_file,
        )


def cmd_describe_config(args) -> None:
    if args.node:
        if args.file_path:
            payload, error = build_backup_config_summary(args.node, args.file_path)
            if error:
                raise TargetConfigurationError(
                    args.node, f"Error describing config {args.file_path}: {error}"
                )
            emit_output(
                [payload], formatter=format_target_summary, out_file=args.out_file
            )
        else:
            current, versions = list_config_versions(args.node)
            version_paths = [version[0] for version in versions]
            version_paths.append(current)
            print(version_paths)
            with ThreadPoolExecutor(max_workers=min(32, len(versions))) as executor:
                results = list(
                    executor.map(
                        build_backup_config_summary,
                        [args.node] * len(version_paths),
                        version_paths,
                    )
                )
            config_summaries = []
            for summary, error in results:
                if error:
                    raise TargetConfigurationError(
                        args.node, f"Error describing config: {error}"
                    )
                config_summaries.append(summary)
            emit_output(
                config_summaries,
                formatter=format_target_summary,
                out_file=args.out_file,
            )
    elif args.file_path:
        raise CLIParameterError("Please provide the node name with --node flag")
    else:
        nodes = get_kubernetes_nodes(DEFAULT_TARGET_SELECTOR)
        jobs = []
        for node in nodes:
            current, versions = list_config_versions(node)
            version_paths = [version[0] for version in versions]
            version_paths.append(current)
            jobs.extend((node, path) for path in version_paths)

        with ThreadPoolExecutor(max_workers=min(32, len(jobs))) as executor:
            results = list(
                executor.map(
                    lambda job: build_backup_config_summary(*job),
                    jobs,
                )
            )

        config_summaries = []
        for summary, error in results:
            if error:
                raise TargetConfigurationError(
                    summary.get("node", "unknown") if summary else "unknown",
                    f"Error describing config: {error}",
                )

            config_summaries.append(summary)
        emit_output(
            config_summaries,
            formatter=format_target_summary,
            out_file=args.out_file,
        )
