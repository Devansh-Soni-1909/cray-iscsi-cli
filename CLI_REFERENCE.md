# iSCSI CLI Reference

Centralized management utility for retrieving and managing iSCSI target, initiator, image, and metrics information from the HPC cluster.

---

## Command Hierarchy

```text
iscsi
├── get
│   ├── nodes
│   ├── configs
│   ├── luns
│   ├── tpgts
│   ├── images
│   ├── metrics
│   ├── sessions
│   ├── mount-status
│   └── errors
└── describe
    └── node
```

---

## Command Summary

| Command                                       | Category             | Description                                   |
| :-------------------------------------------- | :------------------- | :-------------------------------------------- |
| [`iscsi get nodes`](#get-nodes)               | Nodes                | List discovered target and/or initiator nodes |
| [`iscsi get luns`](#get-luns)                 | LUNs                 | List LUNs configured on target nodes          |
| [`iscsi get tpgts`](#get-tpgts)               | TPGTs                | Display Target Portal Groups on target nodes  |
| [`iscsi get images`](#get-images)             | Images               | Show projected RootFS and PE images           |
| [`iscsi get metrics`](#get-metrics)           | Metrics              | Retrieve read metrics/IOPS statistics per LUN |
| [`iscsi get sessions`](#get-sessions)         | Sessions             | Show detailed initiator session information   |
| [`iscsi get mount-status`](#get-mount-status) | Mount Status         | Show mount status of disks on initiator nodes |
| [`iscsi get errors`](#get-errors)             | Logs & Errors        | Scan logs for storage and network errors      |
| [`iscsi get configs`](#get-configs)           | Target Configuration | List target node configuration versions       |               |
| [`iscsi describe node`](#describe-node)       | Description          | Show detailed summary of a specific node      |

---

## 1. Node Commands

### get nodes

#### Syntax

```bash
iscsi get nodes  [--initiator] [--out-file OUT_FILE]
```

#### Description

Lists all discovered target and initiator nodes based on the configured Kubernetes label selector. If `--initiator` is not specified, it returns target node roles by default.

#### Options

| Flag          | Type   | Description                        | Default             |
| :------------ | :----- | :--------------------------------- | :------------------ |
| `--initiator` | Flag   | Fetches iSCSI initiator nodes only | `False`             |
| `--out-file`  | String | Save output to specified file path | `iscsi-output.text` |

#### Command Combinations

##### iscsi get nodes

```bash
iscsi get nodes
```

```text
Nodes matching iscsi-role=target: 2

NAME     | STATUS | ROLE   | ARCH  | OS    | OS IMAGE
---------+--------+--------+-------+-------+-------------------
ncn-w001 | Ready  | target | amd64 | linux | Ubuntu 24.04.4 LTS
ncn-w002 | Ready  | target | amd64 | linux | Ubuntu 24.04.4 LTS

```

##### iscsi get nodes --initiator

```bash
iscsi get nodes --initiator
```

```text
Nodes matching not iscsi-role=target: 1

NAME     | STATUS | ROLE      | ARCH  | OS    | OS IMAGE
---------+--------+-----------+-------+-------+-------------------
ncn-w003 | Ready  | initiator | amd64 | linux | Ubuntu 24.04.4 LTS
```

##### iscsi get nodes --out-file <filename>

```bash
iscsi get nodes --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get nodes --out-file <filename>

```bash
iscsi get nodes --target --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get nodes --initiator --out-file <filename>

```bash
iscsi get nodes --initiator --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 2. LUN Commands

### get luns

#### Syntax

```bash
iscsi get luns [--node NODE_NAME] [--image-type {all,pe,rootfs}] [--metrics] [--out-file OUT_FILE]
```

#### Description

Lists the configured Logical Unit Numbers (LUNs) across target nodes. Can filter by a specific target node or by image type.

#### Options

| Flag           | Type    | Description                                  | Default                   |
| :------------- | :------ | :------------------------------------------- | :------------------------ |
| `--node`       | String  | Target node name to inspect                  | `None` (all target nodes) |
| `--image-type` | Choices | Filter by image type (`all`, `pe`, `rootfs`) | `all`                     |
| `--metrics`    | Flag    | Include metrics for each LUN                 | `False`                   |
| `--out-file`   | String  | Save output to specified file path           | `iscsi-output.txt`        |

#### Command Combinations

##### iscsi get luns

```bash
iscsi get luns
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe

Node: ncn-w002
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w002
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe
```

##### iscsi get luns --node \<target-node\>

```bash
iscsi get luns --node ncn-w001
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe

```

##### iscsi get luns --image-type all

```bash
iscsi get luns --image-type all
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe

Node: ncn-w002
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w002
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe
```

##### iscsi get luns --image-type pe

```bash
iscsi get luns --image-type pe
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUNs: 8
LUN ID | Mapped Image
-------+-----------------------------------------
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe

Node: ncn-w002
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w002
TPGT: tpgt_1
LUNs: 8
LUN ID | Mapped Image
-------+-----------------------------------------
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe

```

##### iscsi get luns --image-type rootfs

```bash
iscsi get luns --image-type rootfs
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUNs: 2
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs

Node: ncn-w002
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w002
TPGT: tpgt_1
LUNs: 2
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs

```

##### iscsi get luns --metrics

```bash
iscsi get luns --metrics
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image                                 | Read MBytes | Read IOPs
-------+----------------------------------------------+-------------+----------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs | 0           | 164
lun1   | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
lun2   | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
lun3   | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
lun4   | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
lun5   | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
lun6   | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
lun7   | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
lun8   | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
lun9   | /var/lib/cps-local/boot-images/image8_pe     | 1           | 232

Node: ncn-w002
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w002
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image                                 | Read MBytes | Read IOPs
-------+----------------------------------------------+-------------+----------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234
lun1   | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
lun2   | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
lun3   | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
lun4   | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
lun5   | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
lun6   | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
lun7   | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
lun8   | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
lun9   | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162

```

##### iscsi get luns --node \<target-node\> --image-type pe

```bash
iscsi get luns --node ncn-w001 --image-type pe
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
Filter: pe
LUNs: 8
LUN ID | Mapped Image
-------+-----------------------------------------
lun2   | /var/lib/cps-local/boot-images/image1_pe
lun3   | /var/lib/cps-local/boot-images/image2_pe
lun4   | /var/lib/cps-local/boot-images/image3_pe
lun5   | /var/lib/cps-local/boot-images/image4_pe
lun6   | /var/lib/cps-local/boot-images/image5_pe
lun7   | /var/lib/cps-local/boot-images/image6_pe
lun8   | /var/lib/cps-local/boot-images/image7_pe
lun9   | /var/lib/cps-local/boot-images/image8_pe

```

##### iscsi get luns --node \<target-node\> --image-type rootfs

```bash
iscsi get luns --node ncn-w001 --image-type rootfs
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
Filter: rootfs
LUNs: 2
LUN ID | Mapped Image
-------+---------------------------------------------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs
lun1   | /var/lib/cps-local/boot-images/image2_rootfs
```

##### iscsi get luns --node \<target-node\> --metrics

```bash
iscsi get luns --node ncn-w001 --metrics
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUNs: 10
LUN ID | Mapped Image                                 | Read MBytes | Read IOPs
-------+----------------------------------------------+-------------+----------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs | 0           | 164
lun1   | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
lun2   | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
lun3   | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
lun4   | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
lun5   | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
lun6   | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
lun7   | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
lun8   | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
lun9   | /var/lib/cps-local/boot-images/image8_pe     | 1           | 232
```

##### iscsi get luns --node \<target-node\> --image-type pe --metrics

```bash
iscsi get luns --node ncn-w001 --image-type pe --metrics
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
Filter: pe
LUNs: 8
LUN ID | Mapped Image                             | Read MBytes | Read IOPs
-------+------------------------------------------+-------------+----------
lun2   | /var/lib/cps-local/boot-images/image1_pe | 1           | 232
lun3   | /var/lib/cps-local/boot-images/image2_pe | 1           | 232
lun4   | /var/lib/cps-local/boot-images/image3_pe | 1           | 232
lun5   | /var/lib/cps-local/boot-images/image4_pe | 1           | 232
lun6   | /var/lib/cps-local/boot-images/image5_pe | 1           | 232
lun7   | /var/lib/cps-local/boot-images/image6_pe | 1           | 232
lun8   | /var/lib/cps-local/boot-images/image7_pe | 1           | 232
lun9   | /var/lib/cps-local/boot-images/image8_pe | 1           | 232
```

##### iscsi get luns --node \<target-node\> --image-type rootfs --metrics

```bash
iscsi get luns --node ncn-w001 --image-type rootfs --metrics
```

```text
Node: ncn-w001
Role: target
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
Filter: rootfs
LUNs: 2
LUN ID | Mapped Image                                 | Read MBytes | Read IOPs
-------+----------------------------------------------+-------------+----------
lun0   | /var/lib/cps-local/boot-images/image1_rootfs | 0           | 164
lun1   | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
```

##### iscsi get luns --out-file \<filename\>

```bash
iscsi get luns --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get luns --node \<target-node\> --out-file \<filename\>

```bash
iscsi get luns --node ncn-w001 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get luns --node \<target-node\> --image-type pe --metrics --out-file \<filename\>

```bash
iscsi get luns --node ncn-w001 --image-type pe --metrics --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 3. TPGT Commands

### get tpgts

#### Syntax

```bash
iscsi get tpgts [--node NODE_NAME] [--out-file OUT_FILE]
```

#### Description

Displays Target Portal Groups (TPGTs) configured on target nodes.

#### Options

| Flag         | Type   | Description                        | Default                   |
| :----------- | :----- | :--------------------------------- | :------------------------ |
| `--node`     | String | Target node name to inspect        | `None` (all target nodes) |
| `--out-file` | String | Save output to specified file path | `iscsi-output.txt`        |

#### Command Combinations

##### iscsi get tpgts

```bash
iscsi get tpgts
```

```text
Node: ncn-w001
Role: target
TPGTs: 1
IQN                                | TPGT   | LUNs
-----------------------------------+--------+-----
iqn.2026-04.lab.local:lab.ncn-w001 | tpgt_1 | 10

Node: ncn-w002
Role: target
TPGTs: 1
IQN                                | TPGT   | LUNs
-----------------------------------+--------+-----
iqn.2026-04.lab.local:lab.ncn-w002 | tpgt_1 | 10
```

##### iscsi get tpgts --node \<target-node\>

```bash
iscsi get tpgts --node ncn-w001
```

```text
Node: ncn-w001
Role: target
TPGTs: 1
IQN                                | TPGT   | LUNs
-----------------------------------+--------+-----
iqn.2026-04.lab.local:lab.ncn-w001 | tpgt_1 | 10
```

##### iscsi get tpgts --out-file \<filename\>

```bash
iscsi get tpgts --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get tpgts --node \<target-node\> --out-file \<filename\>

```bash
iscsi get tpgts --node ncn-w001 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 4. Image Commands

### get images

#### Syntax

```bash
iscsi get images [--node NODE_NAME] [--image-type {all,pe,rootfs}] [--metrics] [--out-file OUT_FILE]
```

#### Description

Lists projected RootFS and PE images attached to target nodes.

#### Options

| Flag           | Type    | Description                                  | Default                   |
| :------------- | :------ | :------------------------------------------- | :------------------------ |
| `--node`       | String  | Target node name to inspect                  | `None` (all target nodes) |
| `--image-type` | Choices | Filter by image type (`all`, `pe`, `rootfs`) | `all`                     |
| `--metrics`    | Flag    | Include metrics for each image               | `False`                   |
| `--out-file`   | String  | Save output to specified file path           | `iscsi-output.txt`        |

#### Command Combinations

##### iscsi get images

```bash
iscsi get images
```

```text
Node: ncn-w001
Role: target
Images: 10
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe

Node: ncn-w002
Role: target
Images: 10
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs

```

##### iscsi get images --node \<target-node\>

```bash
iscsi get images --node ncn-w001
```

```text
Node: ncn-w001
Role: target
Images: 10
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe

```

##### iscsi get images --image-type all

```bash
iscsi get images --image-type all
```

```text
Node: ncn-w001
Role: target
Images: 10
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe

Node: ncn-w002
Role: target
Images: 10
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs

```

##### iscsi get images --image-type pe

```bash
iscsi get images --image-type pe
```

```text
Node: ncn-w001
Role: target
Filter: pe
Images: 8
Image Name | Type | Image Path
-----------+------+-----------------------------------------
image1_pe  | pe   | /var/lib/cps-local/boot-images/image1_pe
image2_pe  | pe   | /var/lib/cps-local/boot-images/image2_pe
image3_pe  | pe   | /var/lib/cps-local/boot-images/image3_pe
image4_pe  | pe   | /var/lib/cps-local/boot-images/image4_pe
image5_pe  | pe   | /var/lib/cps-local/boot-images/image5_pe
image6_pe  | pe   | /var/lib/cps-local/boot-images/image6_pe
image7_pe  | pe   | /var/lib/cps-local/boot-images/image7_pe
image8_pe  | pe   | /var/lib/cps-local/boot-images/image8_pe

Node: ncn-w002
Role: target
Filter: pe
Images: 8
Image Name | Type | Image Path
-----------+------+-----------------------------------------
image8_pe  | pe   | /var/lib/cps-local/boot-images/image8_pe
image7_pe  | pe   | /var/lib/cps-local/boot-images/image7_pe
image6_pe  | pe   | /var/lib/cps-local/boot-images/image6_pe
image5_pe  | pe   | /var/lib/cps-local/boot-images/image5_pe
image4_pe  | pe   | /var/lib/cps-local/boot-images/image4_pe
image3_pe  | pe   | /var/lib/cps-local/boot-images/image3_pe
image2_pe  | pe   | /var/lib/cps-local/boot-images/image2_pe
image1_pe  | pe   | /var/lib/cps-local/boot-images/image1_pe

```

##### iscsi get images --image-type rootfs

```bash
iscsi get images --image-type rootfs
```

```text
Node: ncn-w001
Role: target
Filter: rootfs
Images: 2
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs

Node: ncn-w002
Role: target
Filter: rootfs
Images: 2
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs

```

##### iscsi get images --metrics

```bash
iscsi get images --metrics
```

```text
Node: ncn-w001
Role: target
Images: 10
Image Name    | Type   | Image Path                                    | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234

Node: ncn-w002
Role: target
Images: 10
Image Name    | Type   | Image Path                                    | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234

```

##### iscsi get images --node \<target-node\> --image-type pe

```bash
iscsi get images --node ncn-w001 --image-type pe
```

```text
Node: ncn-w001
Role: target
Filter: pe
Images: 8
Image Name | Type | Image Path
-----------+------+-----------------------------------------
image8_pe  | pe   | /var/lib/cps-local/boot-images/image8_pe
image7_pe  | pe   | /var/lib/cps-local/boot-images/image7_pe
image6_pe  | pe   | /var/lib/cps-local/boot-images/image6_pe
image5_pe  | pe   | /var/lib/cps-local/boot-images/image5_pe
image4_pe  | pe   | /var/lib/cps-local/boot-images/image4_pe
image3_pe  | pe   | /var/lib/cps-local/boot-images/image3_pe
image2_pe  | pe   | /var/lib/cps-local/boot-images/image2_pe
image1_pe  | pe   | /var/lib/cps-local/boot-images/image1_pe


```

##### iscsi get images --node \<target-node\> --image-type rootfs

```bash
iscsi get images --node ncn-w001 --image-type rootfs
```

```text
Node: ncn-w001
Role: target
Filter: rootfs
Images: 2
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs


```

##### iscsi get images --node \<target-node\> --metrics

```bash
iscsi get images --node ncn-w001 --metrics
```

```text
Node: ncn-w001
Role: target
Images: 10
Image Name    | Type   | Image Path                                    | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234

```

##### iscsi get images --node \<target-node\> --image-type pe --metrics

```bash
iscsi get images --node ncn-w001 --image-type pe --metrics
```

```text
Node: ncn-w001
Role: target
Filter: pe
Images: 8
Image Name | Type | Image Path                                | Read MBytes | Read IOPs
-----------+------+------------------------------------------+-------------+----------
image8_pe  | pe   | /var/lib/cps-local/boot-images/image8_pe | 0           | 162
image7_pe  | pe   | /var/lib/cps-local/boot-images/image7_pe | 1           | 232
image6_pe  | pe   | /var/lib/cps-local/boot-images/image6_pe | 1           | 232
image5_pe  | pe   | /var/lib/cps-local/boot-images/image5_pe | 1           | 232
image4_pe  | pe   | /var/lib/cps-local/boot-images/image4_pe | 1           | 232
image3_pe  | pe   | /var/lib/cps-local/boot-images/image3_pe | 1           | 232
image2_pe  | pe   | /var/lib/cps-local/boot-images/image2_pe | 1           | 232
image1_pe  | pe   | /var/lib/cps-local/boot-images/image1_pe | 1           | 232

```

##### iscsi get images --node \<target-node\> --image-type rootfs --metrics

```bash
iscsi get images --node ncn-w001 --image-type rootfs --metrics
```

```text
Node: ncn-w001
Role: target
Filter: rootfs
Images: 2
Image Name    | Type   | Image Path                                    | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234

```

##### iscsi get images --out-file \<filename\>

```bash
iscsi get images --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get images --node \<target-node\> --out-file \<filename\>

```bash
iscsi get images --node ncn-w001 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get images --node \<target-node\> --image-type pe --metrics --out-file \<filename\>

```bash
iscsi get images --node ncn-w001 --image-type pe --metrics --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 5. Metrics Commands

### get metrics

#### Syntax

```bash
iscsi get metrics [--node NODE_NAME] [--out-file OUT_FILE]
```

#### Description

Retrieves read metrics (Read MBytes, Read IOPS) per LUN and per image on target nodes.

#### Options

| Flag         | Type   | Description                        | Default                   |
| :----------- | :----- | :--------------------------------- | :------------------------ |
| `--node`     | String | Target node name to inspect        | `None` (all target nodes) |
| `--out-file` | String | Save output to specified file path | `iscsi-output.txt`        |

#### Command Combinations

##### iscsi get metrics

```bash
iscsi get metrics
```

```text
Node: ncn-w001
Role: target

TPGTs: 1, LUNs: 10

Image Summary
Total Images | RootFS | PE
-------------+--------+---
10           | 2      | 8

LUN read metrics
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUN  | Mapped Image                                 | Read MBytes | Read IOPs
-----+----------------------------------------------+-------------+----------
lun0 | /var/lib/cps-local/boot-images/image1_rootfs | 0           | 164
lun1 | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
lun2 | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
lun3 | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
lun4 | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
lun5 | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
lun6 | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
lun7 | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
lun8 | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
lun9 | /var/lib/cps-local/boot-images/image8_pe     | 1           | 232

Image read metrics
Image Name    | Type   | Image Path                                   | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 0           | 164
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe     | 1           | 232

Removed images (wrt previous configuration)
None

Total Deleted | Deleted rootfs Images | Deleted pe Images
--------------+-----------------------+------------------
0             | 0                     | 0

Node: ncn-w002
Role: target

TPGTs: 1, LUNs: 10

Image Summary
Total Images | RootFS | PE
-------------+--------+----
10           | 2      | 8

LUN read metrics
IQN: iqn.2026-04.lab.local:lab.ncn-w002
TPGT: tpgt_1
LUN  | Mapped Image                                 | Read MBytes | Read IOPs
-----+----------------------------------------------+-------------+----------
lun0 | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234
lun1 | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
lun2 | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
lun3 | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
lun4 | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
lun5 | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
lun6 | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
lun7 | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
lun8 | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
lun9 | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162

Image read metrics
Image Name    | Type   | Image Path                                   | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234

Removed images (wrt previous configuration)
Type   | Image         | Path
-------+---------------+---------------------------------------------
rootfs | image1_rootfs | /var/lib/cps-local/boot_images/image1_rootfs
rootfs | image2_rootfs | /var/lib/cps-local/boot_images/image2_rootfs
pe     | image1_pe     | /var/lib/cps-local/boot_images/image1_pe.img
pe     | image2_pe     | /var/lib/cps-local/boot_images/image2_pe.img
pe     | image3_pe     | /var/lib/cps-local/boot_images/image3_pe.img
pe     | image4_pe     | /var/lib/cps-local/boot_images/image4_pe.img
pe     | image5_pe     | /var/lib/cps-local/boot_images/image5_pe.img
pe     | image6_pe     | /var/lib/cps-local/boot_images/image6_pe.img
pe     | image7_pe     | /var/lib/cps-local/boot_images/image7_pe.img
pe     | image8_pe     | /var/lib/cps-local/boot_images/image8_pe.img

Total Deleted | Deleted rootfs Images | Deleted pe Images
--------------+-----------------------+------------------
10            | 2                     | 8
```

##### iscsi get metrics --node \<node-name\>

```bash
iscsi get metrics --node ncn-w001
```

```text
Node: ncn-w001
Role: target

TPGTs: 1, LUNs: 10

Image Summary
Total Images | RootFS | PE
-------------+--------+----
10           | 2      | 8

LUN read metrics
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUN  | Mapped Image                                 | Read MBytes | Read IOPs
-----+----------------------------------------------+-------------+----------
lun0 | /var/lib/cps-local/boot-images/image1_rootfs | 0           | 164
lun1 | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
lun2 | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
lun3 | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
lun4 | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
lun5 | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
lun6 | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
lun7 | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
lun8 | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
lun9 | /var/lib/cps-local/boot-images/image8_pe     | 1           | 232

Image read metrics
Image Name    | Type   | Image Path                                   | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 0           | 164
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe     | 1           | 232

Removed images (wrt previous configuration)
None

Total Deleted | Deleted rootfs Images | Deleted pe Images
--------------+-----------------------+------------------
0             | 0                     | 0

```

##### iscsi get metrics --node \<node-name\> --out-file \<filename\>

```bash
iscsi get metrics --node ncn-w001 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 6. Session Commands

### get sessions

#### Syntax

```bash
iscsi get sessions [--node NODE_NAME] [--out-file OUT_FILE]
```

#### Description

Displays detailed active iSCSI session mapping on initiator nodes.

#### Options

| Flag         | Type   | Description                        | Default                      |
| :----------- | :----- | :--------------------------------- | :--------------------------- |
| `--node`     | String | Initiator node name to inspect     | `None` (all initiator nodes) |
| `--out-file` | String | Save output to specified file path | `iscsi-output.txt`           |

#### Command Combinations

##### iscsi get sessions

```bash
iscsi get sessions
```

```text
Node: ncn-w003
Role: initiator

tcp: [2] 192.168.122.49:3260,1 iqn.2026-04.lab.local:lab.ncn-w001 (non-flash)
tcp: [3] 192.168.122.66:3260,1 iqn.2026-04.lab.local:lab.ncn-w002 (non-flash)

Node: ncn-w004
Role: initiator

tcp: [1] 192.168.122.49:3260,1 iqn.2026-04.lab.local:lab.ncn-w001 (non-flash)
tcp: [2] 192.168.122.66:3260,1 iqn.2026-04.lab.local:lab.ncn-w002 (non-flash)
```

##### iscsi get sessions --node \<initiator-node\>

```bash
iscsi get sessions --node ncn-w003
```

```text
Node: ncn-w003
Role: initiator

tcp: [2] 192.168.122.49:3260,1 iqn.2026-04.lab.local:lab.ncn-w001 (non-flash)
tcp: [3] 192.168.122.66:3260,1 iqn.2026-04.lab.local:lab.ncn-w002 (non-flash)

```

##### iscsi get sessions --out-file \<filename\>

```bash
iscsi get sessions --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get sessions --node \<initiator-node\> --out-file \<filename\>

```bash
iscsi get sessions --node ncn-w003 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 7. Mount Status Commands

### get mount-status

#### Syntax

```bash
iscsi get mount-status [--node NODE_NAME] [--out-file OUT_FILE]
```

#### Description

Displays local device mounts and state mappings for initiator nodes.

#### Options

| Flag         | Type   | Description                        | Default                      |
| :----------- | :----- | :--------------------------------- | :--------------------------- |
| `--node`     | String | Initiator node name to inspect     | `None` (all initiator nodes) |
| `--out-file` | String | Save output to specified file path | `iscsi-output.txt`           |

#### Command Combinations

##### iscsi get mount-status

```bash
iscsi get mount-status
```

```text
Total Mounted: 4
Total Unmounted: 36

Node: ncn-w003
Role: initiator
Mounted: 2
Unmounted: 18

Device   | Mount Point | Status   
---------+-------------+----------
/dev/sda | -           | unmounted
/dev/sdb | /mnt/rootfs | mounted  
/dev/sdc | -           | unmounted
/dev/sdd | -           | unmounted
/dev/sde | -           | unmounted
/dev/sdf | -           | unmounted
/dev/sdg | -           | unmounted
/dev/sdh | -           | unmounted
/dev/sdi | -           | unmounted
/dev/sdj | -           | unmounted
/dev/sdk | -           | unmounted
/dev/sdl | -           | unmounted
/dev/sdm | -           | unmounted
/dev/sdn | -           | unmounted
/dev/sdo | -           | unmounted
/dev/sdp | /mnt/pe     | mounted  
/dev/sdq | -           | unmounted
/dev/sdr | -           | unmounted
/dev/sds | -           | unmounted
/dev/sdt | -           | unmounted

Node: ncn-w004
Role: initiator
Mounted: 2
Unmounted: 18

Device   | Mount Point | Status   
---------+-------------+----------
/dev/sda | /mnt/rootfs | mounted  
/dev/sdb | -           | unmounted
/dev/sdc | -           | unmounted
/dev/sdd | -           | unmounted
/dev/sde | -           | unmounted
/dev/sdf | -           | unmounted
/dev/sdg | -           | unmounted
/dev/sdh | -           | unmounted
/dev/sdi | -           | unmounted
/dev/sdj | -           | unmounted
/dev/sdk | -           | unmounted
/dev/sdl | -           | unmounted
/dev/sdm | -           | unmounted
/dev/sdn | -           | unmounted
/dev/sdo | -           | unmounted
/dev/sdp | -           | unmounted
/dev/sdq | /mnt/pe     | mounted  
/dev/sdr | -           | unmounted
/dev/sds | -           | unmounted
/dev/sdt | -           | unmounted

```

##### iscsi get mount-status --node \<initiator-node\>

```bash
iscsi get mount-status --node ncn-w003
```

```text
Node: ncn-w003
Role: initiator
Mounted: 2
Unmounted: 18

Device   | Mount Point | Status   
---------+-------------+----------
/dev/sda | -           | unmounted
/dev/sdb | /mnt/rootfs | mounted  
/dev/sdc | -           | unmounted
/dev/sdd | -           | unmounted
/dev/sde | -           | unmounted
/dev/sdf | -           | unmounted
/dev/sdg | -           | unmounted
/dev/sdh | -           | unmounted
/dev/sdi | -           | unmounted
/dev/sdj | -           | unmounted
/dev/sdk | -           | unmounted
/dev/sdl | -           | unmounted
/dev/sdm | -           | unmounted
/dev/sdn | -           | unmounted
/dev/sdo | -           | unmounted
/dev/sdp | /mnt/pe     | mounted  
/dev/sdq | -           | unmounted
/dev/sdr | -           | unmounted
/dev/sds | -           | unmounted
/dev/sdt | -           | unmounted

```

##### iscsi get mount-status --out-file \<filename\>

```bash
iscsi get mount-status --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get mount-status --node \<initiator-node\> --out-file \<filename\>

```bash
iscsi get mount-status --node ncn-w003 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 8. Error and Diagnostic Commands

### get errors

#### Syntax

```bash
iscsi get errors [--node NODE_NAME] [--lines LINES] [--out-file OUT_FILE]
```

#### Description

Scans system logs for storage/network errors on targets or initiators.

#### Options

| Flag         | Type    | Description                                    | Default            |
| :----------- | :------ | :--------------------------------------------- | :----------------- |
| `--node`     | String  | Node name to inspect                           | `None` (all nodes) |
| `--lines`    | Integer | Number of recent log lines to collect per node | `200`              |
| `--out-file` | String  | Save output to specified file path             | `iscsi-output.txt` |

#### Command Combinations

##### iscsi get errors

```bash
iscsi get errors
```

```text
None of the nodes have errors in journalctl, /var/log/messages, /var/log/syslog, dmesg, sbps-marshal.service, target.service, or rtslib-fb-targetctl.service
```

##### iscsi get errors --node \<node-name\>

```bash
iscsi get errors --node ncn-w001
```

```text
None of the nodes have errors in journalctl, /var/log/messages, /var/log/syslog, dmesg, sbps-marshal.service, target.service, or rtslib-fb-targetctl.service
```

##### iscsi get errors --lines \<number\>

```bash
iscsi get errors --lines 100
```

```text
None of the nodes have errors in journalctl, /var/log/messages, /var/log/syslog, dmesg, sbps-marshal.service, target.service, or rtslib-fb-targetctl.service
```

##### iscsi get errors --node \<node-name\> --lines \<number\>

```bash
iscsi get errors --node ncn-w001 --lines 10
```

```text
None of the nodes have errors in journalctl, /var/log/messages, /var/log/syslog, dmesg, sbps-marshal.service, target.service, or rtslib-fb-targetctl.service
```

##### iscsi get errors --out-file \<filename\>

```bash
iscsi get errors --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi get errors --node \<node-name\> --lines \<number\> --out-file \<filename\>

```bash
iscsi get errors --node ncn-w001 --lines 100 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---

## 9. Configuration Commands

### get configs

#### Syntax

```bash
iscsi get configs [--node NODE_NAME] [--out-file OUT_FILE]
```

#### Description

Retrieves the target configuration versions (current and backups) and stores them locally on the master node.

#### Options

| Flag         | Type   | Description                        | Default                   |
| :----------- | :----- | :--------------------------------- | :------------------------ |
| `--node`     | String | Target node name to inspect        | `None` (all target nodes) |
| `--out-file` | String | Save output to specified file path | `iscsi-output.txt`        |

#### Command Combinations

##### iscsi get configs

```bash
iscsi get configs
```

```text
Node: ncn-w001

TYPE    | DATE                    | FILE                                 | LOCAL PATH
--------+-------------------------+--------------------------------------+------------------------------------------------------------------
Current | -                       | saveconfig.json                      | /etc/iscsi/configs/ncn-w001/saveconfig.json
Backup  | 16 Jun 2026 01:56:56 PM | saveconfig-20260616-13:56:56-json.gz | /etc/iscsi/configs/ncn-w001/saveconfig-20260616-13:56:56-json.gz

Node: ncn-w002

TYPE    | DATE                    | FILE                                 | LOCAL PATH
--------+-------------------------+--------------------------------------+------------------------------------------------------------------
Current | -                       | saveconfig.json                      | /etc/iscsi/configs/ncn-w002/saveconfig.json
Backup  | 16 Jun 2026 01:57:58 PM | saveconfig-20260616-13:57:58-json.gz | /etc/iscsi/configs/ncn-w002/saveconfig-20260616-13:57:58-json.gz

```

##### iscsi get configs --node \<target-node\>

```bash
iscsi get configs --node ncn-w001
```

```text
Node: ncn-w001

TYPE    | DATE                    | FILE                                 | LOCAL PATH
--------+-------------------------+--------------------------------------+------------------------------------------------------------------
Current | -                       | saveconfig.json                      | /etc/iscsi/configs/ncn-w001/saveconfig.json
Backup  | 16 Jun 2026 01:56:56 PM | saveconfig-20260616-13:56:56-json.gz | /etc/iscsi/configs/ncn-w001/saveconfig-20260616-13:56:56-json.gz
```

##### iscsi get configs --node \<target-node\> --out-file \<filename\>

```bash
iscsi get configs --node ncn-w001 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

---


## 10. Resource Description Commands

### describe node

#### Syntax

```bash
iscsi describe node [NODE_NAME] [--metrics] [--out-file OUT_FILE]
```

#### Description

Displays a detailed summary of the configured iSCSI resources on one or more nodes.

* If `NODE_NAME` is specified, displays the summary for that node.
* If omitted, displays summaries for all target and initiator nodes.

#### Arguments

| Argument    | Type   | Description                                                                            |
| :---------- | :----- | :------------------------------------------------------------------------------------- |
| `NODE_NAME` | String | Name of the node to inspect. If omitted, all target and initiator nodes are described. |

#### Options

| Flag         | Type   | Description                            | Default            |
| :----------- | :----- | :------------------------------------- | :----------------- |
| `--metrics`  | Flag   | Include LUN metrics for target nodes   | `False`            |
| `--out-file` | String | Save output to the specified file path | `iscsi-output.txt` |

#### Command Combinations

##### iscsi describe node

```bash
iscsi describe node
```

```text
Node: ncn-w001
Role: target
Config file: saveconfig.json
Path: /etc/iscsi/configs/ncn-w001/saveconfig.json
IQNs: iqn.2026-04.lab.local:lab.ncn-w001
TPGTs: 1, LUNs: 10, Images: 10

TPGTs
IQN                                | TPGT   | LUNs
-----------------------------------+--------+-----
iqn.2026-04.lab.local:lab.ncn-w001 | tpgt_1 | 10  

LUNs
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUN  | Mapped Image                                
-----+---------------------------------------------
lun0 | /var/lib/cps-local/boot-images/image1_rootfs
lun1 | /var/lib/cps-local/boot-images/image2_rootfs
lun2 | /var/lib/cps-local/boot-images/image1_pe    
lun3 | /var/lib/cps-local/boot-images/image2_pe    
lun4 | /var/lib/cps-local/boot-images/image3_pe    
lun5 | /var/lib/cps-local/boot-images/image4_pe    
lun6 | /var/lib/cps-local/boot-images/image5_pe    
lun7 | /var/lib/cps-local/boot-images/image6_pe    
lun8 | /var/lib/cps-local/boot-images/image7_pe    
lun9 | /var/lib/cps-local/boot-images/image8_pe    

Images
Image Name    | Type   | Image Path                                  
--------------+--------+---------------------------------------------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe    
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe    
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe    
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe    
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe    
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe    
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe    
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe    
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs

Node: ncn-w002
Role: target
Config file: saveconfig.json
Path: /etc/iscsi/configs/ncn-w002/saveconfig.json
IQNs: iqn.2026-04.lab.local:lab.ncn-w002
TPGTs: 1, LUNs: 10, Images: 10

TPGTs
IQN                                | TPGT   | LUNs
-----------------------------------+--------+-----
iqn.2026-04.lab.local:lab.ncn-w002 | tpgt_1 | 10  

LUNs
IQN: iqn.2026-04.lab.local:lab.ncn-w002
TPGT: tpgt_1
LUN  | Mapped Image                                
-----+---------------------------------------------
lun0 | /var/lib/cps-local/boot-images/image1_rootfs
lun1 | /var/lib/cps-local/boot-images/image2_rootfs
lun2 | /var/lib/cps-local/boot-images/image1_pe    
lun3 | /var/lib/cps-local/boot-images/image2_pe    
lun4 | /var/lib/cps-local/boot-images/image3_pe    
lun5 | /var/lib/cps-local/boot-images/image4_pe    
lun6 | /var/lib/cps-local/boot-images/image5_pe    
lun7 | /var/lib/cps-local/boot-images/image6_pe    
lun8 | /var/lib/cps-local/boot-images/image7_pe    
lun9 | /var/lib/cps-local/boot-images/image8_pe    

Images
Image Name    | Type   | Image Path                                  
--------------+--------+---------------------------------------------
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe    
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe    
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe    
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe    
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe    
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe    
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe    
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe    
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs

Node: ncn-w003
Role: initiator
Sessions: 2, Total mounts: 20, Mounted: 2, Unmounted: 18

Session details:
- iqn.2026-04.lab.local:lab.ncn-w001 | Portal: 192.168.122.49:3260,1 | State: LOGGED_IN | Devices: 10
- iqn.2026-04.lab.local:lab.ncn-w002 | Portal: 192.168.122.66:3260,1 | State: LOGGED_IN | Devices: 10

Mount status:
Device   | Mount Point | Status   
---------+-------------+----------
/dev/sda | -           | unmounted
/dev/sdb | /mnt/rootfs | mounted  
/dev/sdc | -           | unmounted
/dev/sdd | -           | unmounted
/dev/sde | -           | unmounted
/dev/sdf | -           | unmounted
/dev/sdg | -           | unmounted
/dev/sdh | -           | unmounted
/dev/sdi | -           | unmounted
/dev/sdj | -           | unmounted
/dev/sdk | -           | unmounted
/dev/sdl | -           | unmounted
/dev/sdm | -           | unmounted
/dev/sdn | -           | unmounted
/dev/sdo | -           | unmounted
/dev/sdp | /mnt/pe     | mounted  
/dev/sdq | -           | unmounted
/dev/sdr | -           | unmounted
/dev/sds | -           | unmounted
/dev/sdt | -           | unmounted

Node: ncn-w004
Role: initiator
Sessions: 2, Total mounts: 20, Mounted: 2, Unmounted: 18

Session details:
- iqn.2026-04.lab.local:lab.ncn-w001 | Portal: 192.168.122.49:3260,1 | State: LOGGED_IN | Devices: 10
- iqn.2026-04.lab.local:lab.ncn-w002 | Portal: 192.168.122.66:3260,1 | State: LOGGED_IN | Devices: 10

Mount status:
Device   | Mount Point | Status   
---------+-------------+----------
/dev/sda | /mnt/rootfs | mounted  
/dev/sdb | -           | unmounted
/dev/sdc | -           | unmounted
/dev/sdd | -           | unmounted
/dev/sde | -           | unmounted
/dev/sdf | -           | unmounted
/dev/sdg | -           | unmounted
/dev/sdh | -           | unmounted
/dev/sdi | -           | unmounted
/dev/sdj | -           | unmounted
/dev/sdk | -           | unmounted
/dev/sdl | -           | unmounted
/dev/sdm | -           | unmounted
/dev/sdn | -           | unmounted
/dev/sdo | -           | unmounted
/dev/sdp | -           | unmounted
/dev/sdq | /mnt/pe     | mounted  
/dev/sdr | -           | unmounted
/dev/sds | -           | unmounted
/dev/sdt | -           | unmounted

```

##### iscsi describe node \<node-name\>

```bash
iscsi describe node ncn-w001
```

```text
Node: ncn-w001
Role: target
Config file: saveconfig.json
Path: /etc/rtslib-fb-target/saveconfig.json
IQNs: iqn.2026-04.lab.local:lab.ncn-w001
TPGTs: 1, LUNs: 10, Images: 10

TPGTs
IQN                                | TPGT   | LUNs
-----------------------------------+--------+-----
iqn.2026-04.lab.local:lab.ncn-w001 | tpgt_1 | 10

LUNs
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUN   | Mapped Image
------+---------------------------------------------
lun0  | /var/lib/cps-local/boot-images/image1_rootfs
lun1  | /var/lib/cps-local/boot-images/image2_rootfs
lun2  | /var/lib/cps-local/boot-images/image1_pe
lun3  | /var/lib/cps-local/boot-images/image2_pe
lun4  | /var/lib/cps-local/boot-images/image3_pe
lun5  | /var/lib/cps-local/boot-images/image4_pe
lun6  | /var/lib/cps-local/boot-images/image5_pe
lun7  | /var/lib/cps-local/boot-images/image6_pe
lun8  | /var/lib/cps-local/boot-images/image7_pe
lun9  | /var/lib/cps-local/boot-images/image8_pe

Images
Image Name    | Type   | Image Path
--------------+--------+---------------------------------------------
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe

```

##### iscsi describe node \<node-name\> --metrics

```bash
iscsi describe node ncn-w001 --metrics
```

```text
Node: ncn-w001
Role: target
Config file: saveconfig.json
Path: /etc/rtslib-fb-target/saveconfig.json
IQNs: iqn.2026-04.lab.local:lab.ncn-w001
TPGTs: 1, LUNs: 10, Images: 10

TPGTs
IQN                                | TPGT   | LUNs
-----------------------------------+--------+-----
iqn.2026-04.lab.local:lab.ncn-w001 | tpgt_1 | 10

LUNs
IQN: iqn.2026-04.lab.local:lab.ncn-w001
TPGT: tpgt_1
LUN   | Mapped Image                                 | Read MBytes | Read IOPs
------+----------------------------------------------+-------------+----------
lun0  | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234
lun1  | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
lun2  | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
lun3  | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
lun4  | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
lun5  | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
lun6  | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
lun7  | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
lun8  | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
lun9  | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162

Images
Image Name    | Type   | Image Path                                    | Read MBytes | Read IOPs
--------------+--------+----------------------------------------------+-------------+----------
image1_rootfs | rootfs | /var/lib/cps-local/boot-images/image1_rootfs | 1           | 234
image2_rootfs | rootfs | /var/lib/cps-local/boot-images/image2_rootfs | 1           | 232
image1_pe     | pe     | /var/lib/cps-local/boot-images/image1_pe     | 1           | 232
image2_pe     | pe     | /var/lib/cps-local/boot-images/image2_pe     | 1           | 232
image3_pe     | pe     | /var/lib/cps-local/boot-images/image3_pe     | 1           | 232
image4_pe     | pe     | /var/lib/cps-local/boot-images/image4_pe     | 1           | 232
image5_pe     | pe     | /var/lib/cps-local/boot-images/image5_pe     | 1           | 232
image6_pe     | pe     | /var/lib/cps-local/boot-images/image6_pe     | 1           | 232
image7_pe     | pe     | /var/lib/cps-local/boot-images/image7_pe     | 1           | 232
image8_pe     | pe     | /var/lib/cps-local/boot-images/image8_pe     | 0           | 162

```

##### iscsi describe node \<node-name\> --out-file \<filename\>

```bash
iscsi describe node ncn-w001 --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```

##### iscsi describe node \<node-name\> --metrics --out-file \<filename\>

```bash
iscsi describe node ncn-w001 --metrics --out-file iscsi-output.txt
```

```text
Output saved to iscsi-output.txt
```
