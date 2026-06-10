from dataclasses import dataclass


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
