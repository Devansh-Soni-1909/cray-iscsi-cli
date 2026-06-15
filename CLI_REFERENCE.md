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
├── set
│   └── label
└── describe
    ├── node
    └── config
```

---

## Command Summary

| Command | Category | Description |
| :--- | :--- | :--- |
| [`iscsi get nodes`](#get-nodes) | Nodes | List discovered target and/or initiator nodes |
| [`iscsi get configs`](#get-configs) | Configuration | List target node configuration versions |
| [`iscsi get luns`](#get-luns) | LUNs | List LUNs configured on target nodes |
| [`iscsi get tpgts`](#get-tpgts) | TPGTs | Display Target Portal Groups on target nodes |
| [`iscsi get images`](#get-images) | Images | Show projected RootFS and PE images |
| [`iscsi get metrics`](#get-metrics) | Metrics | Retrieve read metrics/IOPS statistics per LUN |
| [`iscsi get sessions`](#get-sessions) | Sessions | Show detailed initiator session information |
| [`iscsi get mount-status`](#get-mount-status) | Mount Status | Show mount status of disks on initiator nodes |
| [`iscsi get errors`](#get-errors) | Logs & Errors | Scan logs for storage and network errors |
| [`iscsi set label`](#set-label) | Settings | Configure discovery label selectors |
| [`iscsi describe node`](#describe-node) | Description | Show detailed summary of a specific node |
| [`iscsi describe config`](#describe-config) | Description | Show detailed summary of a backup config file |

---

## 1. Node Commands

### get nodes

#### Syntax
```bash
iscsi get nodes [--target] [--initiator] [--out-file OUT_FILE]
```

#### Description
Lists all discovered target and initiator nodes based on the configured Kubernetes label selectors. If neither `--target` nor `--initiator` is specified, it returns both node roles by default.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--target` | Flag | Fetches iSCSI target nodes only | `False` |
| `--initiator`| Flag | Fetches iSCSI initiator nodes only | `False` |
| `--out-file` | String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get nodes
```bash
iscsi get nodes
```
```text
[Output Placeholder]
```

##### iscsi get nodes --target
```bash
iscsi get nodes --target
```
```text
[Output Placeholder]
```

##### iscsi get nodes --initiator
```bash
iscsi get nodes --initiator
```
```text
[Output Placeholder]
```

##### iscsi get nodes --target --initiator
```bash
iscsi get nodes --target --initiator
```
```text
[Output Placeholder]
```

##### iscsi get nodes --out-file <filename>
```bash
iscsi get nodes --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get nodes --target --out-file <filename>
```bash
iscsi get nodes --target --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get nodes --initiator --out-file <filename>
```bash
iscsi get nodes --initiator --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get nodes --target --initiator --out-file <filename>
```bash
iscsi get nodes --target --initiator --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 2. Configuration Commands

### get configs

#### Syntax
```bash
iscsi get configs --name NODE_NAME [--out-file OUT_FILE]
```

#### Description
Lists the target configuration versions (from backups) available on the specified target node.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Target node name to inspect | **Required** |
| `--out-file`| String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get configs --name \<target-node\>
```bash
iscsi get configs --name ncn-w001
```
```text
[Output Placeholder]
```

##### iscsi get configs --name \<target-node\> --out-file \<filename\>
```bash
iscsi get configs --name ncn-w001 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 3. LUN Commands

### get luns

#### Syntax
```bash
iscsi get luns [--name NODE_NAME] [--image-type {all,pe,rootfs}] [--metrics] [--out-file OUT_FILE]
```

#### Description
Lists the configured Logical Unit Numbers (LUNs) across target nodes. Can filter by a specific target node or by image type.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Target node name to inspect | `None` (all target nodes) |
| `--image-type` | Choices | Filter by image type (`all`, `pe`, `rootfs`) | `all` |
| `--metrics` | Flag | Include metrics for each LUN | `False` |
| `--out-file` | String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get luns
```bash
iscsi get luns
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\>
```bash
iscsi get luns --name ncn-w001
```
```text
[Output Placeholder]
```

##### iscsi get luns --image-type all
```bash
iscsi get luns --image-type all
```
```text
[Output Placeholder]
```

##### iscsi get luns --image-type pe
```bash
iscsi get luns --image-type pe
```
```text
[Output Placeholder]
```

##### iscsi get luns --image-type rootfs
```bash
iscsi get luns --image-type rootfs
```
```text
[Output Placeholder]
```

##### iscsi get luns --metrics
```bash
iscsi get luns --metrics
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\> --image-type pe
```bash
iscsi get luns --name ncn-w001 --image-type pe
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\> --image-type rootfs
```bash
iscsi get luns --name ncn-w001 --image-type rootfs
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\> --metrics
```bash
iscsi get luns --name ncn-w001 --metrics
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\> --image-type pe --metrics
```bash
iscsi get luns --name ncn-w001 --image-type pe --metrics
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\> --image-type rootfs --metrics
```bash
iscsi get luns --name ncn-w001 --image-type rootfs --metrics
```
```text
[Output Placeholder]
```

##### iscsi get luns --out-file \<filename\>
```bash
iscsi get luns --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\> --out-file \<filename\>
```bash
iscsi get luns --name ncn-w001 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get luns --name \<target-node\> --image-type pe --metrics --out-file \<filename\>
```bash
iscsi get luns --name ncn-w001 --image-type pe --metrics --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 4. TPGT Commands

### get tpgts

#### Syntax
```bash
iscsi get tpgts [--name NODE_NAME] [--out-file OUT_FILE]
```

#### Description
Displays Target Portal Groups (TPGTs) configured on target nodes.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Target node name to inspect | `None` (all target nodes) |
| `--out-file`| String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get tpgts
```bash
iscsi get tpgts
```
```text
[Output Placeholder]
```

##### iscsi get tpgts --name \<target-node\>
```bash
iscsi get tpgts --name ncn-w001
```
```text
[Output Placeholder]
```

##### iscsi get tpgts --out-file \<filename\>
```bash
iscsi get tpgts --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get tpgts --name \<target-node\> --out-file \<filename\>
```bash
iscsi get tpgts --name ncn-w001 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 5. Image Commands

### get images

#### Syntax
```bash
iscsi get images [--name NODE_NAME] [--image-type {all,pe,rootfs}] [--metrics] [--out-file OUT_FILE]
```

#### Description
Lists projected RootFS and PE images attached to target nodes.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Target node name to inspect | `None` (all target nodes) |
| `--image-type` | Choices | Filter by image type (`all`, `pe`, `rootfs`) | `all` |
| `--metrics` | Flag | Include metrics for each image | `False` |
| `--out-file` | String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get images
```bash
iscsi get images
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\>
```bash
iscsi get images --name ncn-w001
```
```text
[Output Placeholder]
```

##### iscsi get images --image-type all
```bash
iscsi get images --image-type all
```
```text
[Output Placeholder]
```

##### iscsi get images --image-type pe
```bash
iscsi get images --image-type pe
```
```text
[Output Placeholder]
```

##### iscsi get images --image-type rootfs
```bash
iscsi get images --image-type rootfs
```
```text
[Output Placeholder]
```

##### iscsi get images --metrics
```bash
iscsi get images --metrics
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\> --image-type pe
```bash
iscsi get images --name ncn-w001 --image-type pe
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\> --image-type rootfs
```bash
iscsi get images --name ncn-w001 --image-type rootfs
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\> --metrics
```bash
iscsi get images --name ncn-w001 --metrics
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\> --image-type pe --metrics
```bash
iscsi get images --name ncn-w001 --image-type pe --metrics
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\> --image-type rootfs --metrics
```bash
iscsi get images --name ncn-w001 --image-type rootfs --metrics
```
```text
[Output Placeholder]
```

##### iscsi get images --out-file \<filename\>
```bash
iscsi get images --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\> --out-file \<filename\>
```bash
iscsi get images --name ncn-w001 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get images --name \<target-node\> --image-type pe --metrics --out-file \<filename\>
```bash
iscsi get images --name ncn-w001 --image-type pe --metrics --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 6. Metrics Commands

### get metrics

#### Syntax
```bash
iscsi get metrics --name NODE_NAME [--config-file CONFIG_FILE] [--out-file OUT_FILE]
```

#### Description
Retrieves read metrics (Read MBytes, Read IOPS) per LUN on target nodes, or session details on initiator nodes.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Target/Initiator node name to inspect | **Required** |
| `--config-file`| String | Backup configuration file to compare metrics against | `None` (uses current active target config) |
| `--out-file` | String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get metrics --name \<node-name\>
```bash
iscsi get metrics --name ncn-w001
```
```text
[Output Placeholder]
```

##### iscsi get metrics --name \<node-name\> --config-file \<path\>
```bash
iscsi get metrics --name ncn-w001 --config-file /etc/target/saveconfig.json
```
```text
[Output Placeholder]
```

##### iscsi get metrics --name \<node-name\> --out-file \<filename\>
```bash
iscsi get metrics --name ncn-w001 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get metrics --name \<node-name\> --config-file \<path\> --out-file \<filename\>
```bash
iscsi get metrics --name ncn-w001 --config-file /etc/target/saveconfig.json --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 7. Session Commands

### get sessions

#### Syntax
```bash
iscsi get sessions [--name NODE_NAME] [--out-file OUT_FILE]
```

#### Description
Displays detailed active iSCSI session mapping on initiator nodes.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Initiator node name to inspect | `None` (all initiator nodes) |
| `--out-file`| String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get sessions
```bash
iscsi get sessions
```
```text
[Output Placeholder]
```

##### iscsi get sessions --name \<initiator-node\>
```bash
iscsi get sessions --name ncn-w003
```
```text
[Output Placeholder]
```

##### iscsi get sessions --out-file \<filename\>
```bash
iscsi get sessions --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get sessions --name \<initiator-node\> --out-file \<filename\>
```bash
iscsi get sessions --name ncn-w003 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 8. Mount Status Commands

### get mount-status

#### Syntax
```bash
iscsi get mount-status [--name NODE_NAME] [--out-file OUT_FILE]
```

#### Description
Displays local device mounts and state mappings for initiator nodes.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Initiator node name to inspect | `None` (all initiator nodes) |
| `--out-file`| String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get mount-status
```bash
iscsi get mount-status
```
```text
[Output Placeholder]
```

##### iscsi get mount-status --name \<initiator-node\>
```bash
iscsi get mount-status --name ncn-w003
```
```text
[Output Placeholder]
```

##### iscsi get mount-status --out-file \<filename\>
```bash
iscsi get mount-status --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get mount-status --name \<initiator-node\> --out-file \<filename\>
```bash
iscsi get mount-status --name ncn-w003 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 9. Error and Diagnostic Commands

### get errors

#### Syntax
```bash
iscsi get errors [--name NODE_NAME] [--lines LINES] [--out-file OUT_FILE]
```

#### Description
Scans system logs for storage/network errors on targets or initiators.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Node name to inspect | `None` (all nodes) |
| `--lines` | Integer | Number of recent log lines to collect per node | `200` |
| `--out-file`| String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi get errors
```bash
iscsi get errors
```
```text
[Output Placeholder]
```

##### iscsi get errors --name \<node-name\>
```bash
iscsi get errors --name ncn-w001
```
```text
[Output Placeholder]
```

##### iscsi get errors --lines \<number\>
```bash
iscsi get errors --lines 100
```
```text
[Output Placeholder]
```

##### iscsi get errors --name \<node-name\> --lines \<number\>
```bash
iscsi get errors --name ncn-w001 --lines 100
```
```text
[Output Placeholder]
```

##### iscsi get errors --out-file \<filename\>
```bash
iscsi get errors --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi get errors --name \<node-name\> --lines \<number\> --out-file \<filename\>
```bash
iscsi get errors --name ncn-w001 --lines 100 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

## 10. Configuration Settings Commands

### set label

#### Syntax
```bash
iscsi set label [--target TARGET] [--initiator INITIATOR]
```

#### Description
Configures the Kubernetes label selectors stored in the local config file (`/etc/iscsi/config.yml`) used by the discovery mechanisms.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--target` | String | Label selector for identifying target nodes | `None` (does not modify target selector) |
| `--initiator`| String | Label selector for identifying initiator nodes | `None` (does not modify initiator selector) |

#### Command Combinations

##### iscsi set label --target \<selector\>
```bash
iscsi set label --target iscsi-role=target
```
```text
[Output Placeholder]
```

##### iscsi set label --initiator \<selector\>
```bash
iscsi set label --initiator iscsi-role=initiator
```
```text
[Output Placeholder]
```

##### iscsi set label --target \<selector\> --initiator \<selector\>
```bash
iscsi set label --target iscsi-role=target --initiator iscsi-role=initiator
```
```text
[Output Placeholder]
```

---

## 11. Resource Description Commands

### describe node

#### Syntax
```bash
iscsi describe node --name NODE_NAME [--metrics] [--out-file OUT_FILE]
```

#### Description
Shows a detailed summary of the configured iSCSI resources (IQNs, TPGTs, LUNs, and images) on the node.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--name` | String | Node name to inspect | **Required** |
| `--metrics` | Flag | Include storage metrics | `False` |
| `--out-file` | String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi describe node --name \<node-name\>
```bash
iscsi describe node --name ncn-w001
```
```text
[Output Placeholder]
```

##### iscsi describe node --name \<node-name\> --metrics
```bash
iscsi describe node --name ncn-w001 --metrics
```
```text
[Output Placeholder]
```

##### iscsi describe node --name \<node-name\> --out-file \<filename\>
```bash
iscsi describe node --name ncn-w001 --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

##### iscsi describe node --name \<node-name\> --metrics --out-file \<filename\>
```bash
iscsi describe node --name ncn-w001 --metrics --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```

---

### describe config

#### Syntax
```bash
iscsi describe config --node NODE_NAME --file-path FILE_PATH [--out-file OUT_FILE]
```

#### Description
Provides a detailed description summary of a specific backup configuration file stored on the node.

#### Options
| Flag | Type | Description | Default |
| :--- | :--- | :--- | :--- |
| `--node` | String | Target node name where the file is stored | **Required** |
| `--file-path` | String | Path to the backup configuration file | **Required** |
| `--out-file` | String | Save output to specified file path | `None` (writes to stdout) |

#### Command Combinations

##### iscsi describe config --node \<node-name\> --file-path \<path\>
```bash
iscsi describe config --node ncn-w001 --file-path /etc/target/saveconfig.json
```
```text
[Output Placeholder]
```

##### iscsi describe config --node \<node-name\> --file-path \<path\> --out-file \<filename\>
```bash
iscsi describe config --node ncn-w001 --file-path /etc/target/saveconfig.json --out-file iscsi-output.txt
```
```text
[Output Placeholder]
```
