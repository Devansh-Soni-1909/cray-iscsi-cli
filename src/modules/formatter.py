from typing import List, Sequence
from pathlib import Path


def render_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))

    def render_row(values: Sequence[str]) -> str:
        return " | ".join(
            str(value).ljust(widths[index]) for index, value in enumerate(values)
        )

    separator = "-+-".join("-" * width for width in widths)
    lines = [render_row(headers), separator]
    lines.extend(render_row(row) for row in rows)
    return "\n".join(lines)


def emit_output(
    payload: dict | list[dict] | tuple[list[dict], list[dict]],
    formatter=None,
    out_file: str = None,
) -> None:
    text = formatter(payload) if formatter else str(payload)
    if not out_file:
        print(text)
    else:
        with open(out_file, "w") as f:
            f.write(text + "\n")
        print(f"Output saved to {out_file}")


def format_nodes_output(payload: dict) -> str:
    nodes = payload.get("nodes", {})
    lines = [f'Nodes matching {payload.get("label", "selector")}: {len(nodes)}']
    if not nodes:
        lines.append("None")
        return "\n".join(lines)

    headers = [
        "NAME",
        "STATUS",
        "ROLE",
        "ARCH",
        "OS",
        "OS IMAGE",
    ]
    rows = []
    for node in nodes.values():
        node_info = node.get("node_info", {})
        rows.append(
            [
                node.get("name", ""),
                node.get("status", ""),
                node.get("role", ""),
                node_info.get("arch", ""),
                node_info.get("os", ""),
                node_info.get("os_image", ""),
            ]
        )
    lines.append("")
    lines.append(render_table(headers, rows))
    return "\n".join(lines)


def format_target_summary(summaries: list[dict]) -> str:
    sections = []

    for summary in summaries:
        lines = [
            f"Node: {summary.get('node', 'unknown')}",
            "Role: target",
            f"Config file: {summary.get('config_file', 'current configuration')}",
            f"Path: {summary.get('file_path', 'N/A')}",
        ]

        with_metrics = summary.get("with_metrics", False)

        lines.append(f"IQNs: {', '.join(summary.get('iqns', [])) or 'None'}")

        lines.append(
            f"TPGTs: {summary.get('tpgt_count', 0)}, "
            f"LUNs: {summary.get('lun_count', 0)}, "
            f"Images: {summary.get('total_active_images', 0)}"
        )

        if summary.get("errors"):
            lines.append("Warnings:")
            lines.extend(f"- {message}" for message in summary["errors"])

        tpgts = summary.get("tpgts", [])
        if tpgts:
            lines.extend(
                [
                    "",
                    "TPGTs",
                    render_table(
                        [
                            "IQN",
                            "TPGT",
                            "LUNs",
                            "ACLs",
                            "ACL names",
                        ],
                        [
                            [
                                tpgt["iqn"],
                                tpgt["tpgt_name"],
                                str(tpgt["lun_count"]),
                                str(tpgt["acl_count"]),
                                ", ".join(tpgt["acl_names"]) or "None",
                            ]
                            for tpgt in tpgts
                        ],
                    ),
                ]
            )

        images = summary.get("luns", summary.get("images", []))
        if images:
            headers = [
                "IQN",
                "TPGT",
                "LUN",
                "Type",
                "Image",
            ]

            if with_metrics:
                headers.extend(
                    [
                        "Read MBytes",
                        "Read IOPs",
                    ]
                )

            rows = []

            for lun in images:
                tpgt = lun.get("tpgt", {})
                image = lun.get("image", {})

                row = [
                    tpgt.get("iqn", ""),
                    tpgt.get("tpgt_name", ""),
                    str(lun.get("lun_id", "")),
                    image.get("image_type", ""),
                    image.get("image_name", ""),
                ]

                if with_metrics:
                    row.extend(
                        [
                            str(lun.get("read_mbytes", 0)),
                            str(lun.get("read_iops", 0)),
                        ]
                    )

                rows.append(row)

            lines.extend(
                [
                    "",
                    "LUNs and images",
                    render_table(headers, rows),
                ]
            )

        config_versions = summary.get("config_versions", [])
        if config_versions:
            lines.extend(
                [
                    "",
                    "Backup Configurations",
                    render_table(
                        ["DATE", "FILE", "PATH"],
                        [
                            [date, Path(filepath).name, filepath]
                            for filepath, date in config_versions
                        ]
                    ),
                ]
            )

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def format_initiator_summary(summaries: list[dict]) -> str:
    sections = []

    for summary in summaries:
        lines = [
            f"Node: {summary.get('node', 'unknown')}",
            "Role: initiator",
            (
                f"Sessions: {summary.get('sessions', 0)}, "
                f"Total mounts: {summary.get('total', 0)}, "
                f"Mounted: {summary.get('mounted', 0)}, "
                f"Unmounted: {summary.get('unmounted', 0)}"
            ),
        ]

        session_details = summary.get("session_details", [])

        if session_details:
            lines.extend(["", "Session details:"])

            for session in session_details:
                target = session.get("target", "unknown")
                portal = session.get("portal", "unknown")
                state = session.get("session_state", "unknown")
                device_count = len(session.get("devices", []))

                lines.append(
                    f"- {target} | Portal: {portal} | "
                    f"State: {state} | Devices: {device_count}"
                )

        mounts = summary.get("mounts", [])
        if mounts:
            lines.extend(
                [
                    "",
                    "Mount status:",
                    _format_mount_status_table(mounts),
                ]
            )

        if summary.get("errors"):
            lines.extend(["", "Warnings:"])
            lines.extend(f"- {message}" for message in summary["errors"])

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def format_both_summaries(summaries: tuple[list[dict], list[dict]]) -> str:
    target_summary_str = format_target_summary(summaries[0])
    initiator_summary_str = format_initiator_summary(summaries[1])
    return "\n\n".join([target_summary_str, initiator_summary_str])


def format_luns_output(payload: dict) -> str:
    lines = []
    if "node" in payload:
        lines.append(f"Node: {payload['node']}")
        lines.append(f"Role: {payload.get('role', 'target')}")
        luns = payload.get("luns", [])
        image_filter = payload.get("image_type", "all")
        if image_filter != "all":
            lines.append(f"Filter: {image_filter}")
        lines.append(f"LUNs: {payload.get('count', len(luns))}")
        if luns:
            with_metrics = payload.get("with_metrics", False)
            headers = [
                "IQN",
                "TPGT",
                "LUN ID",
                "LUN Name",
                "Type",
                "Image",
                "udev_path",
            ]
            if with_metrics:
                headers.extend(["Read MBytes", "Read IOPs"])
            rows = []
            for lun in luns:
                tpgt = lun.get("tpgt", {})
                image = lun.get("image", {})
                row = [
                    tpgt.get("iqn", ""),
                    tpgt.get("tpgt_name", ""),
                    str(lun.get("lun_id", "")),
                    lun.get("lun_name", ""),
                    image.get("image_type", ""),
                    image.get("image_name", ""),
                    image.get("udev_path", ""),
                ]
                if with_metrics:
                    row.extend(
                        [
                            str(lun.get("read_mbytes", 0)),
                            str(lun.get("read_iops", 0)),
                        ]
                    )
                rows.append(row)
            lines.append(render_table(headers, rows))
        else:
            lines.append("None")
    else:
        for node_summary in payload.get("nodes", []):
            lines.append(format_luns_output(node_summary))
            lines.append("")
    return "\n".join(lines).strip()


def format_tpgts_output(payload: dict) -> str:
    lines = []
    if "node" in payload:
        lines.append(f"Node: {payload['node']}")
        lines.append(f"Role: {payload.get('role', 'target')}")
        tpgts = payload.get("tpgts", [])
        lines.append(f"TPGTs: {payload.get('count', len(tpgts))}")
        if tpgts:
            rows = []
            for tpgt in tpgts:
                rows.append(
                    [
                        tpgt["iqn"],
                        tpgt["tpgt_name"],
                        str(tpgt["lun_count"]),
                        str(tpgt["acl_count"]),
                        ", ".join(tpgt["acl_names"]) or "None",
                    ]
                )
            lines.append(
                render_table(["IQN", "TPGT", "LUNs", "ACLs", "ACL names"], rows)
            )
        else:
            lines.append("None")
    else:
        for node_summary in payload.get("nodes", []):
            lines.append(format_tpgts_output(node_summary))
            lines.append("")
    return "\n".join(lines).strip()


def format_images_output(payload: dict) -> str:
    lines = []
    if "node" in payload:
        images = payload.get("images", [])
        lines.append(f"Node: {payload['node']}")
        lines.append(f"Role: {payload.get('role', 'target')}")
        image_filter = payload.get("image_type", "all")
        if image_filter != "all":
            lines.append(f"Filter: {image_filter}")
        lines.append(f"Images: {payload.get('count', len(images))}")
        if images:
            with_metrics = payload.get("with_metrics", False)
            headers = ["Image Name", "Type", "udev_path"]
            if with_metrics:
                headers.extend(["Read MBytes", "Read IOPs"])
            rows = []
            for image in images:
                row = [
                    image.get("image_name", ""),
                    image.get("image_type", ""),
                    image.get("udev_path", ""),
                ]
                if with_metrics:
                    row.extend(
                        [
                            str(image.get("read_mbytes", 0)),
                            str(image.get("read_iops", 0)),
                        ]
                    )
                rows.append(row)
            lines.append(render_table(headers, rows))
        else:
            lines.append("None")
    else:
        for node_summary in payload.get("nodes", []):
            lines.append(format_images_output(node_summary))
            lines.append("")
    return "\n".join(lines).strip()


def _format_initiator_sessions_summary(summary: dict) -> str:
    lines = [
        f"Node: {summary.get('node', 'unknown')}",
        f"Role: {summary.get('role', 'initiator')}",
        "",
    ]
    session_lines = summary.get("session_lines", [])
    if session_lines:
        lines.extend(session_lines)
    else:
        lines.append("No active sessions.")
    if summary.get("errors"):
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {message}" for message in summary["errors"])
    return "\n".join(lines)


def format_sessions_output(payload: dict) -> str:
    if "nodes" in payload:
        lines = []
        for summary in payload["nodes"]:
            lines.append(_format_initiator_sessions_summary(summary))
            lines.append("")
        return "\n".join(lines).strip()
    return _format_initiator_sessions_summary(payload)


def _format_mount_status_table(mounts: List[dict]) -> str:
    headers = ["Device", "Mount Point", "Status"]
    rows = [
        [
            entry.get("device", "-"),
            entry.get("mount_point") or "-",
            entry["status"],
        ]
        for entry in mounts
    ]
    if not rows:
        return "No iSCSI devices found."
    return render_table(headers, rows)


def _format_initiator_mount_status_summary(summary: dict) -> str:
    lines = [
        f"Node: {summary.get('node', 'unknown')}",
        f"Role: {summary.get('role', 'initiator')}",
        "",
        _format_mount_status_table(summary.get("mounts", [])),
    ]
    if summary.get("errors"):
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {message}" for message in summary["errors"])
    return "\n".join(lines)


def format_mount_status_output(payload: dict) -> str:
    if "nodes" in payload:
        nodes = payload["nodes"]
        total_mounted = sum(summary.get("mounted", 0) for summary in nodes)
        total_unmounted = sum(summary.get("unmounted", 0) for summary in nodes)
        lines = [
            f"Mounted: {total_mounted}, Unmounted: {total_unmounted}",
            "",
        ]
        for summary in nodes:
            lines.append(_format_initiator_mount_status_summary(summary))
            lines.append("")
        return "\n".join(lines).strip()
    return _format_initiator_mount_status_summary(payload)


def format_target_metrics(summaries: list[dict]) -> str:
    sections = []

    for summary in summaries:
        lines = [
            f"Node: {summary.get('node', 'unknown')}",
            "Role: target",
            "",
            (
                f"TPGTs: {summary.get('tpgt_count', 0)}, "
                f"LUNs: {summary.get('lun_count', 0)}"
            ),
        ]

        lines.append("")
        lines.append("Image Summary")
        lines.append(
            render_table(
                ["Total Images", "RootFS", "PE", "Unknown"],
                [
                    [
                        str(summary.get("total_active_images", 0)),
                        str(summary.get("rootfs_count", 0)),
                        str(summary.get("pe_count", 0)),
                        str(summary.get("unknown_count", 0)),
                    ]
                ],
            )
        )

        lines.append("")
        lines.append("LUN read metrics")

        images = summary.get("luns", summary.get("images", []))
        if images:
            rows = [
                [
                    lun.get("tpgt", {}).get("iqn", ""),
                    lun.get("tpgt", {}).get("tpgt_name", ""),
                    str(lun.get("lun_id", "")),
                    lun.get("image", {}).get("image_name", ""),
                    str(lun.get("read_mbytes", 0)),
                    str(lun.get("read_iops", 0)),
                ]
                for lun in images
            ]

            lines.append(
                render_table(
                    [
                        "IQN",
                        "TPGT",
                        "LUN",
                        "Image",
                        "Read MBytes",
                        "Read IOPs",
                    ],
                    rows,
                )
            )
        else:
            lines.append("No LUN metrics found.")

        deleted_images = summary.get("deleted_images", [])

        lines.append("")
        lines.append("Removed images since backup comparison")

        if deleted_images:
            rows = [
                [
                    row.get("type", "unknown"),
                    row.get("image_name", "-"),
                    row.get("path", "-"),
                ]
                for row in deleted_images
            ]

            lines.append(
                render_table(
                    ["Type", "Image", "Path"],
                    rows,
                )
            )

            comparison_source = summary.get("comparison_source")
            if comparison_source:
                lines.append("")
                lines.append("Comparison source")
                lines.append(comparison_source)
        else:
            lines.append("None")

        comparison_summary = summary.get("comparison_summary")

        if comparison_summary:
            lines.append("")
            lines.append("Snapshot change summary")

            lines.append(
                render_table(
                    [
                        "IQNs +",
                        "IQNs -",
                        "TPGTs +",
                        "TPGTs -",
                        "LUNs +",
                        "LUNs -",
                        "ACLs +",
                        "ACLs -",
                        "Storage +",
                        "Storage -",
                        "Rootfs -",
                        "PE -",
                    ],
                    [
                        [
                            str(comparison_summary.get("iqns_added", 0)),
                            str(comparison_summary.get("iqns_removed", 0)),
                            str(comparison_summary.get("tpgs_added", 0)),
                            str(comparison_summary.get("tpgs_removed", 0)),
                            str(comparison_summary.get("luns_added", 0)),
                            str(comparison_summary.get("luns_removed", 0)),
                            str(comparison_summary.get("acls_added", 0)),
                            str(comparison_summary.get("acls_removed", 0)),
                            str(comparison_summary.get("storage_objects_added", 0)),
                            str(comparison_summary.get("storage_objects_removed", 0)),
                            str(comparison_summary.get("rootfs_deleted", 0)),
                            str(comparison_summary.get("pe_deleted", 0)),
                        ]
                    ],
                )
            )

        if summary.get("errors"):
            lines.append("")
            lines.append("Warnings")
            lines.extend(f"- {error}" for error in summary["errors"])

        sections.append("\n".join(lines))

    return ("\n\n").join(sections)


def format_initiator_metrics(summaries: list[dict]) -> str:
    sections = []
    for summary in summaries:
        lines = [
            f"Node: {summary.get('node', 'unknown')}",
            "Role: initiator",
            "",
            f"Sessions: {summary.get('sessions', 0)}",
            f"Total mounts: {summary.get('total', 0)}",
            f"Mounted: {summary.get('mounted', 0)}",
            f"Unmounted: {summary.get('unmounted', 0)}",
        ]

        session_details = summary.get("session_details", [])
        if session_details:
            lines.extend(["", "Session Details"])

            for session in session_details:
                lines.extend(
                    [
                        "",
                        f"Target: {session.get('target', 'unknown')}",
                        f"  Portal: {session.get('portal', 'unknown')}",
                        f"  SID: {session.get('sid', 'unknown')}",
                        f"  Connection State: {session.get('connection_state', 'unknown')}",
                        f"  Session State: {session.get('session_state', 'unknown')}",
                    ]
                )

                devices = session.get("devices", [])
                if devices:
                    lines.append("  Devices:")

                    for device in devices:
                        lines.append(
                            f"    LUN {device.get('lun', '?')}: {device.get('disk', '?')}"
                        )

        if summary.get("errors"):
            lines.extend(["", "Warnings"])

            for error in summary["errors"]:
                lines.append(f"- {error}")

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def format_both_metrics(summaries: tuple[list[dict], list[dict]]) -> str:
    target_summary = format_target_metrics(summaries[0])
    initiator_summary = format_initiator_metrics(summaries[1])
    return "\n\n".join([target_summary, initiator_summary])


def format_error_summary(payload: dict) -> str:
    if "nodes" in payload:
        lines = [
            f"Label: {payload.get('label', '-')}",
            f"Lines: {payload.get('lines', '-')}",
            "",
            "Node summaries",
        ]

        node_rows = [
            [
                item.get("node", "-"),
                str(len(item.get("diagnostics", []))),
                item.get("log_error") or "ok",
            ]
            for item in payload.get("nodes", [])
        ]

        if node_rows:
            lines.append(
                render_table(
                    ["Node", "Findings", "Log status"],
                    node_rows,
                )
            )
        else:
            lines.append("None")

        # Recent Service Errors
        lines.append("")
        lines.append("Recent Service Errors")

        for item in payload.get("nodes", []):
            service_errors = item.get("service_errors", {})

            lines.append("")
            lines.append(f"Node: {item.get('node', '-')}")

            if not service_errors:
                lines.append("No recent service errors found.")
                continue

            for service, output in service_errors.items():
                lines.append("")
                lines.append(f"Service: {service}")

                if output and output.strip():
                    lines.append(output)
                else:
                    lines.append("No recent errors found.")

        # Detected Errors
        diagnostic_rows = []

        for item in payload.get("nodes", []):
            for diagnostic in item.get("diagnostics", []):
                diagnostic_rows.append(
                    [
                        diagnostic.get("node", "-"),
                        diagnostic.get("severity", "-"),
                        diagnostic.get("source", "-"),
                        diagnostic.get("message", "-")[:120],
                    ]
                )

        lines.append("")
        lines.append("Detected errors")

        if diagnostic_rows:
            lines.append(
                render_table(
                    ["Node", "Severity", "Source", "Message"],
                    diagnostic_rows,
                )
            )
        else:
            lines.append("None")

        return "\n".join(lines)

    # Single-node mode
    lines = [
        f"Node: {payload.get('node', '-')}",
        f"Lines: {payload.get('lines', '-')}",
    ]

    if payload.get("log_error"):
        lines.append(f"Log error: {payload['log_error']}")

    service_errors = payload.get("service_errors", {})

    if service_errors:
        lines.append("")
        lines.append("Recent Service Errors")

        for service, output in service_errors.items():
            lines.append("")
            lines.append(service)

            if output and output.strip():
                lines.append(output)
            else:
                lines.append("No recent errors found.")

    diagnostics = payload.get("diagnostics", [])

    lines.append("")
    lines.append("Detected errors")

    if diagnostics:
        rows = [
            [
                diagnostic.get("severity", "-"),
                diagnostic.get("source", "-"),
                diagnostic.get("message", "-")[:120],
            ]
            for diagnostic in diagnostics
        ]

        lines.append(
            render_table(
                ["Severity", "Source", "Message"],
                rows,
            )
        )
    else:
        lines.append("None")

    if payload.get("logs"):
        lines.append("")
        lines.append("Recent logs")
        lines.append(payload["logs"])

    return "\n".join(lines)


def format_configs_output(payloads: list[dict]) -> str:
    separator = "\n\n"
    sections = []

    for payload in payloads:
        node = payload.get("node", "")
        current_config = payload.get("current_config")
        versions = payload.get("versions", [])

        lines = [
            f"Node: {node}",
            "",
            "Current Configuration",
            "---------------------",
        ]

        if current_config:
            current_path = Path(current_config)
            lines.append(f"{current_path.name} ({current_path})")
        else:
            lines.append("None")

        lines.extend(
            [
                "",
                "Backup Configurations",
                "---------------------",
            ]
        )

        if versions:
            headers = ["DATE", "FILE", "PATH"]
            rows = [
                [date, Path(filepath).name, filepath] for filepath, date in versions
            ]
            lines.append(render_table(headers, rows))
        else:
            lines.append("None")

        sections.append("\n".join(lines))

    return separator.join(sections)
