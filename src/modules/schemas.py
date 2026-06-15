from __future__ import annotations
from typing import Optional
from dataclasses import dataclass

# Data Classes


@dataclass
class LunImage:
    node: str
    iqn: str
    tpgt_name: str
    lun_id: str
    lun_name: str
    image_name: str
    image_type: str
    udev_path: str
    object_path: str
    read_mbytes: int
    read_iops: int


@dataclass
class NodeErrorReport:
    node: str
    source: str
    severity: str
    message: str


@dataclass
class TpgtInfo:
    tag: int
    tpgt_name: str


# Error Classes


class ISCSIException(Exception):
    """Base exception for all utility errors."""

    def __init__(
        self, message: str, category: str = "General", node: Optional[str] = None
    ):
        self.message = message
        self.category = category
        self.node = node
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [f"[{self.category}]"]
        if self.node:
            parts.append(f"[Node: {self.node}]")
        parts.append(self.message)
        return " ".join(parts)


class CLIParameterError(ISCSIException):
    def __init__(self, message: str):
        super().__init__(message, category="CLI")


class KubernetesError(ISCSIException):
    def __init__(self, message: str):
        super().__init__(message, category="Kubernetes")


class RemoteCommandError(ISCSIException):
    def __init__(self, node: str, command: str, reason: str):
        message = f"Command failed: '{command}' - {reason}"
        super().__init__(message, category="RemoteCommand", node=node)
        self.command = command
        self.reason = reason


class TargetConfigurationError(ISCSIException):
    def __init__(self, node: str, message: str):
        super().__init__(message, category="TargetConfig", node=node)


class InitiatorConfigurationError(ISCSIException):
    def __init__(self, node: str, message: str):
        super().__init__(message, category="InitiatorConfig", node=node)


class MetricsCollectionError(ISCSIException):
    def __init__(self, node: str, message: str):
        super().__init__(message, category="Metrics", node=node)
