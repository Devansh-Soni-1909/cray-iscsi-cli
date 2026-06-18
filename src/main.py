from __future__ import annotations

import argparse

from modules import (
    get_target_node_label,
    get_initiator_node_label,
    cmd_get_nodes,
    cmd_get_configs,
    cmd_get_tpgts,
    cmd_get_luns,
    cmd_get_images,
    cmd_get_metrics,
    cmd_get_sessions,
    cmd_get_mount_status,
    cmd_get_errors,
    cmd_set_label,
    cmd_describe_node,
    cmd_describe_config,
    ISCSIException,
)

DEFAULT_TARGET_SELECTOR = None
DEFAULT_INITIATOR_SELECTOR = None
DEFAULT_OUT_FILE = "iscsi-output.txt"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cray", description="Cray iSCSI CLI")
    root_subparsers = parser.add_subparsers(dest="resource", required=True)
    iscsi_parser = root_subparsers.add_parser("iscsi", help="iSCSI management commands")
    subparsers = iscsi_parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get", help="Read-only iSCSI commands")
    get_subparsers = get_parser.add_subparsers(dest="get_command", required=True)

    # --out-file flag
    out_file_parent = argparse.ArgumentParser(add_help=False)
    out_file_parent.add_argument(
        "--out-file",
        nargs="?",
        const=DEFAULT_OUT_FILE,
        default=None,
        help="Save output to file (default: iscsi-output.txt)",
    )

    # cmd: get nodes
    nodes_parser = get_subparsers.add_parser(
        "nodes", parents=[out_file_parent], help="List iSCSI target nodes"
    )
    nodes_parser.add_argument(
        "--initiator",
        action="store_true",
        default=False,
        help="Fetches iSCSI initiator nodes",
    )
    nodes_parser.set_defaults(func=cmd_get_nodes)

    # cmd: get luns
    luns_parser = get_subparsers.add_parser(
        "luns", parents=[out_file_parent], help="List LUNs for one or more target nodes"
    )
    luns_parser.add_argument(
        "--node",
        default=None,
        help="Target node name; if omitted, all target nodes are queried",
    )
    luns_parser.add_argument(
        "--image-type",
        choices=["all", "pe", "rootfs"],
        default="all",
        help="Limit output to PE or rootfs LUNs",
    )
    luns_parser.add_argument(
        "--metrics", action="store_true", default=False, help="Include LUN metrics"
    )

    luns_parser.set_defaults(func=cmd_get_luns)

    # cmd: get tpgts
    tpgts_parser = get_subparsers.add_parser(
        "tpgts",
        parents=[out_file_parent],
        help="List TPGTs for one or more target nodes",
    )
    tpgts_parser.add_argument(
        "--node",
        default=None,
        help="Target node name; if omitted, all target nodes are queried",
    )

    tpgts_parser.set_defaults(func=cmd_get_tpgts)

    # cmd: get images
    images_parser = get_subparsers.add_parser(
        "images", parents=[out_file_parent], help="List projected images"
    )
    images_parser.add_argument(
        "--node",
        default=None,
        help="Target node name; if omitted, all target nodes are queried",
    )
    images_parser.add_argument(
        "--image-type",
        choices=["all", "pe", "rootfs"],
        default="all",
        help="Limit output to PE or rootfs images",
    )
    images_parser.add_argument(
        "--metrics", action="store_true", default=False, help="Include LUN metrics"
    )

    images_parser.set_defaults(func=cmd_get_images)

    # cmd: get metrics
    metrics_parser = get_subparsers.add_parser(
        "metrics", parents=[out_file_parent], help="Show iSCSI metrics"
    )
    metrics_parser.add_argument(
        "--node",
        default=None,
        help="Target node name; if omitted, all target nodes are queried",
    )
    metrics_parser.add_argument(
        "--config-file",
        default=None,
        help="Backup config file path to compare against; defaults to the latest backup version",
    )

    metrics_parser.set_defaults(func=cmd_get_metrics)

    # cmd: get sessions
    sessions_parser = get_subparsers.add_parser(
        "sessions", parents=[out_file_parent], help="Show initiator mount/session state"
    )
    sessions_parser.add_argument(
        "--node",
        default=None,
        help="Initiator node name; if omitted, all initiator nodes are queried",
    )
    sessions_parser.set_defaults(func=cmd_get_sessions)

    # cmd: get mount-status
    mount_status_parser = get_subparsers.add_parser(
        "mount-status", parents=[out_file_parent], help="Show initiator mount status"
    )
    mount_status_parser.add_argument(
        "--node",
        default=None,
        help="Initiator node name; if omitted, all initiator nodes are queried",
    )

    mount_status_parser.set_defaults(func=cmd_get_mount_status)

    # cmd: get configs
    configs_parser = get_subparsers.add_parser(
        "configs",
        parents=[out_file_parent],
        help="List all the target node configuration versions",
    )
    configs_parser.add_argument(
        "--node",
        default=None,
        help="Target node name; if omitted, all target nodes are queried",
    )
    configs_parser.set_defaults(func=cmd_get_configs)

    # cmd: get errors
    errors_parser = get_subparsers.add_parser(
        "errors",
        parents=[out_file_parent],
        help="Scan recent logs for storage and network errors",
    )
    errors_parser.add_argument(
        "--node",
        default=None,
        help="Node name to inspect; if omitted, all discovered nodes are inspected",
    )
    errors_parser.add_argument(
        "--lines",
        type=int,
        default=200,
        help="Number of recent log lines to collect per node",
    )

    errors_parser.set_defaults(func=cmd_get_errors)

    set_parser = subparsers.add_parser(
        "set", help="Set label for target/initiator nodes"
    )
    set_subparsers = set_parser.add_subparsers(dest="set_command", required=True)

    # cmd: set label
    label_parser = set_subparsers.add_parser(
        "label",
        help="Configure label selectors used to discover target and initiator nodes",
    )
    label_parser.add_argument(
        "--target",
        default=DEFAULT_TARGET_SELECTOR,
        help="Label selector used to identify target nodes",
    )
    label_parser.add_argument(
        "--initiator",
        default=DEFAULT_INITIATOR_SELECTOR,
        help="Label selector used to identify initiator nodes",
    )
    label_parser.set_defaults(func=cmd_set_label)

    describe_parser = subparsers.add_parser(
        "describe", help="Detailed iSCSI resource descriptions"
    )
    describe_subparsers = describe_parser.add_subparsers(
        dest="describe_command", required=True
    )
    # cmd: describe node
    node_parser = describe_subparsers.add_parser(
        "node",
        parents=[out_file_parent],
        help="Show a detailed iSCSI summary for one node",
    )
    node_parser.add_argument("--node", default=None, help="Node name to inspect")
    node_parser.add_argument(
        "--metrics", action="store_true", default=False, help="Include LUN metrics"
    )

    node_parser.set_defaults(func=cmd_describe_node)

    # cmd: describe config
    # config_parser = describe_subparsers.add_parser(
    #     "config",
    #     parents=[out_file_parent],
    #     help="Show a detailed summary of the mentioned node",
    # )
    # config_parser.add_argument("--node", default=None, help="None name to inspect")
    # config_parser.add_argument(
    #     "--file-path", default=None, help="Path of the configuration file to describe"
    # )

    # config_parser.set_defaults(func=cmd_describe_config)

    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        global DEFAULT_TARGET_SELECTOR, DEFAULT_INITIATOR_SELECTOR
        DEFAULT_TARGET_SELECTOR = get_target_node_label()
        DEFAULT_INITIATOR_SELECTOR = get_initiator_node_label()

        parser = build_parser()
        args = parser.parse_args(argv)
        args.func(args)
        return 0
    except ISCSIException as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:
        print(f"Unexpected Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
