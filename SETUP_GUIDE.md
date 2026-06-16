# Complete Setup Guide

This guide details the complete setup steps for the HPC Cluster iSCSI SBPS Management Utility environment. 

---

## VM Naming and Role Convention

| Node Hostname | IP Address (Example) | Role / Type |
| :--- | :--- | :--- |
| `ncn-m001` | `192.168.122.241` | Master / Control Plane |
| `ncn-w001` | `192.168.122.242` | Worker Node / iSCSI Target |
| `ncn-w002` | `192.168.122.243` | Worker Node / iSCSI Target |
| `ncn-w003` | `192.168.122.245` | Worker Node / iSCSI Initiator |

---

## 1. Create VMs

Create 4 VMs running Ubuntu Server 24.04:
- **Control Plane**: 1 Master node named `ncn-m001`
- **iSCSI Targets**: 2 Worker nodes named `ncn-w001` and `ncn-w002`
- **iSCSI Initiator**: 1 Worker node named `ncn-w003`

*Note: Ensure you select/install OpenSSH Server during the Ubuntu server installation.*

---

## 2. DNS and Hostname Setup

Configure local name resolution so all VMs can communicate using their hostnames.

1. On **every VM**, open `/etc/hosts` in a text editor:
   ```bash
   sudo nano /etc/hosts
   ```

2. Add mappings for all nodes in the cluster (adjust IPs according to your virtual network):
   ```text
   192.168.122.241 ncn-m001
   192.168.122.242 ncn-w001
   192.168.122.243 ncn-w002
   192.168.122.245 ncn-w003
   ```

3. Test local hostname resolution:
   ```bash
   ping -c 3 ncn-w001
   ```

---

## 3. Enable Root User Access and Passwordless SSH

The metrics utility executes remote commands on targets and initiators using `pdsh`. This requires passwordless SSH access to the `root` user across all VMs.

### 1. Enable Root Access and SSH Configuration
On **all VMs (`ncn-m001`, `ncn-w001`, `ncn-w002`, `ncn-w003`)**:

1. Set a password for the `root` user:
   ```bash
   sudo passwd root
   ```

2. Configure SSH daemon to permit root login. Edit `/etc/ssh/sshd_config`:
   ```bash
   sudo sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
   ```

3. Restart the SSH service:
   ```bash
   sudo systemctl restart ssh
   ```

### 2. Generate and Distribute SSH Keys
On the **Master Node (`ncn-m001`)**:

1. Switch to the `root` user:
   ```bash
   sudo su -
   ```

2. Generate an SSH keypair (press Enter to accept default path and empty passphrase):
   ```bash
   ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
   ```

3. Copy the master node's public key to all nodes in the cluster (including itself):
   ```bash
   ssh-copy-id root@ncn-m001
   ssh-copy-id root@ncn-w001
   ssh-copy-id root@ncn-w002
   ssh-copy-id root@ncn-w003
   ```

4. Verify that you can log in to each node without being prompted for a password:
   ```bash
   ssh root@ncn-w001 hostname
   ssh root@ncn-w002 hostname
   ssh root@ncn-w003 hostname
   ```

---

## 4. Install and Configure pdsh

`pdsh` (Parallel Distributed Shell) runs shell commands in parallel across multiple target hosts.

1. Install `pdsh` on the **Master Node (`ncn-m001`)**:
   ```bash
   sudo apt-get update && sudo apt-get install -y pdsh
   ```

2. Configure `pdsh` to use SSH as the default remote command wrapper by adding the `PDSH_RCMD_TYPE` environment variable. Open `/root/.bashrc` on `ncn-m001`:
   ```bash
   echo "export PDSH_RCMD_TYPE=ssh" | sudo tee -a /root/.bashrc
   ```

3. Apply the environment variable to your current shell session:
   ```bash
   export PDSH_RCMD_TYPE=ssh
   ```

4. Test `pdsh` parallel execution:
   ```bash
   pdsh -w ncn-w001,ncn-w002,ncn-w003 "uname -a"
   ```

---

## 5. Configure iSCSI Targets and Initiators

### 1. iSCSI Target Configuration
Run the following configuration steps on **both target VMs (`ncn-w001` and `ncn-w002`)**. This creates 10 Fileio backstore images (50MB each) divided into:
- 2 RootFS Images (`image1_rootfs`, `image2_rootfs`)
- 8 PE Images (`image1_pe` to `image8_pe`)

```text
Target Node (ncn-w001 / ncn-w002)
└── TPG1
   ├── lun0 -> image1_rootfs
   ├── lun1 -> image2_rootfs
   ├── ...
   ├── lun9 -> image8_pe
   └── ACLs (allow all initiators)
```

1. Create a setup script file:
   ```bash
   nano iscsi-target-setup.sh
   ```

2. Copy the script below into the file:
   ```bash
   #!/bin/bash
   set -e

   BASE_DIR="/var/lib/cps-local/boot-images"
   PORTAL_IP="0.0.0.0"
   PORTAL_PORT="3260"

   # Extract current node hostname to customize target IQN
   HOSTNAME=$(hostname)
   TARGET_IQN="iqn.2026-04.lab.local:lab.${HOSTNAME}"

   echo "[+] Installing targetcli"
   apt-get update
   apt-get install -y targetcli-fb

   echo "[+] Creating disk directory"
   mkdir -p ${BASE_DIR}

   echo "[+] Cleaning old disk images"
   rm -f ${BASE_DIR}/*

   echo "[+] Resetting existing target configuration"
   targetcli clearconfig confirm=True || true

   echo "[+] Creating rootfs disks (2)"
   for i in $(seq 1 2); do
      targetcli /backstores/fileio create \
         image${i}_rootfs \
         ${BASE_DIR}/image${i}_rootfs \
         50M
   done

   echo "[+] Creating PE disks (8)"
   for i in $(seq 1 8); do
      targetcli /backstores/fileio create \
         image${i}_pe \
         ${BASE_DIR}/image${i}_pe \
         50M
   done

   echo "[+] Creating iSCSI target"
   targetcli /iscsi create ${TARGET_IQN}

   echo "[+] Creating portal"
   targetcli /iscsi/${TARGET_IQN}/tpg1/portals create \
   ${PORTAL_IP} ${PORTAL_PORT} || true

   echo "[+] Disabling authentication (no CHAP)"
   targetcli /iscsi/${TARGET_IQN}/tpg1 set attribute authentication=0

   echo "[+] Enabling dynamic ACLs (allow all initiators)"
   targetcli /iscsi/${TARGET_IQN}/tpg1 set attribute generate_node_acls=1

   echo "[+] Mapping rootfs disks as LUNs"
   for i in $(seq 1 2); do
      targetcli /iscsi/${TARGET_IQN}/tpg1/luns create \
         /backstores/fileio/image${i}_rootfs
   done

   echo "[+] Mapping PE disks as LUNs"
   for i in $(seq 1 8); do
      targetcli /iscsi/${TARGET_IQN}/tpg1/luns create \
         /backstores/fileio/image${i}_pe
   done

   echo "[+] Saving configuration"
   targetcli saveconfig

   echo "[+] Enabling target service"
   systemctl enable rtslib-fb-targetctl

   echo "[+] Setup complete"
   ```

3. Make the script executable:
   ```bash
   chmod +x iscsi-target-setup.sh
   ```

4. Run the script with root privileges:
   ```bash
   sudo ./iscsi-target-setup.sh
   ```

5. Verify target configuration:
   ```bash
   sudo targetcli ls
   ```

---

### 2. iSCSI Initiator Configuration
Run the following steps on the **initiator VM (`ncn-w003`)** to discover and log in to the configured targets on `ncn-w001` and `ncn-w002`.

1. Create the client setup script:
   ```bash
   nano iscsi-initiator-setup.sh
   ```

2. Copy the following code into the script:
   ```bash
   #!/bin/bash
   set -e

   # Portals for targets
   PORTAL_1="192.168.122.242:3260"
   PORTAL_2="192.168.122.243:3260"

   HOSTNAME=$(hostname)
   CLIENT_IQN="iqn.2026-04.lab.local:${HOSTNAME}.initiator"

   echo "[+] Cleaning previous iSCSI client configuration"
   systemctl stop open-iscsi || true
   systemctl stop iscsid || true
   iscsiadm -m node --logout || true
   iscsiadm -m node -o delete || true
   rm -rf /etc/iscsi/nodes/*
   rm -rf /etc/iscsi/send_targets/*
   apt purge open-iscsi -y

   echo "[+] Installing open-iscsi"
   apt-get update -y
   apt-get install -y open-iscsi

   echo "[+] Setting initiator IQN"
   sed -i "s|^InitiatorName=.*|InitiatorName=${CLIENT_IQN}|" /etc/iscsi/initiatorname.iscsi

   echo "[+] Restarting services"
   systemctl restart iscsid
   systemctl restart open-iscsi

   echo "[+] Discovering targets from Portal 1 (ncn-w001)"
   iscsiadm -m discovery -t sendtargets -p ${PORTAL_1}

   echo "[+] Discovering targets from Portal 2 (ncn-w002)"
   iscsiadm -m discovery -t sendtargets -p ${PORTAL_2}

   echo "[+] Logging into discovered targets"
   iscsiadm -m node --login || true

   echo "[+] Enabling auto-login on boot"
   iscsiadm -m node -o update -n node.startup -v automatic

   echo "[+] Verifying active sessions"
   iscsiadm -m session

   echo "[+] Checking mapped block devices"
   lsblk

   echo "[+] iSCSI client setup complete"
   ```

3. Make the script executable:
   ```bash
   chmod +x iscsi-initiator-setup.sh
   ```

4. Run the script with root privileges:
   ```bash
   sudo ./iscsi-initiator-setup.sh
   ```

5. Verify the session details:
   ```bash
   sudo iscsiadm -m session -P 3
   ```

6. Perform write and read test operations on the mapped disks (e.g. `/dev/sdb`):
   ```bash
   # Write IO Test
   sudo dd if=/dev/zero of=/dev/sdb bs=1M count=10 status=progress

   # Read IO Test
   sudo dd if=/dev/sdb of=/dev/null bs=1M count=10 status=progress
   ```

---

## 6. Install Kubernetes in All VMs

Perform containerd and Kubernetes installation across all VMs (`ncn-m001`, `ncn-w001`, `ncn-w002`, `ncn-w003`).

### 1. Containerd Setup

1. Enable IPv4 packet forwarding on all VMs:
   ```bash
   cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
   net.ipv4.ip_forward = 1
   EOF

   sudo sysctl --system
   ```

2. Download and install Containerd (e.g. version 2.3.0):
   ```bash
   wget https://github.com/containerd/containerd/releases/download/v2.3.0/containerd-2.3.0-linux-amd64.tar.gz
   sudo tar Cxzvf /usr/local containerd-2.3.0-linux-amd64.tar.gz
   ```

3. Configure systemd unit file for Containerd:
   ```bash
   wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
   sudo mkdir -p /usr/local/lib/systemd/system
   sudo mv containerd.service /usr/local/lib/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now containerd
   ```

4. Install `runc`:
   ```bash
   wget https://github.com/opencontainers/runc/releases/download/v1.4.2/runc.amd64
   sudo install -m 755 runc.amd64 /usr/local/sbin/runc
   ```

5. Install CNI Plugins:
   ```bash
   wget https://github.com/containernetworking/plugins/releases/download/v1.9.1/cni-plugins-linux-amd64-v1.9.1.tgz
   sudo mkdir -p /opt/cni/bin
   sudo tar Cxzvf /opt/cni/bin cni-plugins-linux-amd64-v1.9.1.tgz
   ```

6. Generate default config and configure systemd cgroup driver:
   ```bash
   sudo mkdir -p /etc/containerd
   containerd config default | sudo tee /etc/containerd/config.toml
   ```
   Open `/etc/containerd/config.toml` and verify or set:
   ```toml
   [plugins."io.containerd.cri.v1.runtime".containerd.runtimes.runc.options]
     SystemdCgroup = true
   ```
   Restart containerd:
   ```bash
   sudo systemctl restart containerd
   ```

---

### 2. Install Kubernetes Components
Run these commands on **all VMs**:

1. Turn off swap memory:
   ```bash
   sudo swapoff -a
   # Make it permanent by commenting out swap entries in /etc/fstab
   sudo sed -i '/swap/s/^/#/' /etc/fstab
   ```

2. Configure repository keyring and sources:
   ```bash
   sudo apt-get update
   sudo apt-get install -y apt-transport-https ca-certificates curl gpg
   sudo mkdir -p -m 755 /etc/apt/keyrings
   curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.35/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
   echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.35/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
   ```

3. Install packages:
   ```bash
   sudo apt-get update
   sudo apt-get install -y kubelet kubeadm kubectl
   sudo apt-mark hold kubelet kubeadm kubectl
   sudo systemctl enable --now kubelet
   ```

---

### 3. Initialize Control Plane (Master Node)
On the **Master Node (`ncn-m001`)**:

1. Initialize kubeadm:
   ```bash
   sudo kubeadm init --apiserver-advertise-address=192.168.122.241 --pod-network-cidr=10.244.0.0/16
   ```

2. Set up local kubeconfig credentials:
   ```bash
   mkdir -p $HOME/.kube
   sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
   sudo chown $(id -u):$(id -g) $HOME/.kube/config
   ```

3. Install Flannel CNI:
   ```bash
   kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
   ```

---

### 4. Join Worker Nodes to Cluster
On **all worker VMs (`ncn-w001`, `ncn-w002`, `ncn-w003`)**:

1. Execute the join command printed during the control plane initialization. For example:
   ```bash
   sudo kubeadm join 192.168.122.241:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
   ```

---

### 5. Label Cluster Nodes
Assign proper roles to the nodes using Kubernetes labels so the management tool can discover them. Run these on the **Master Node (`ncn-m001`)**:

1. Label target nodes:
   ```bash
   kubectl label node ncn-w001 iscsi-role=target iscsi-target=true
   kubectl label node ncn-w002 iscsi-role=target iscsi-target=true
   ```

2. Label initiator node:
   ```bash
   kubectl label node ncn-w003 iscsi-role=initiator iscsi-initiator=true
   ```

3. Verify labels:
   ```bash
   kubectl get nodes --show-labels
   ```

---

### 6. Flannel Network Troubleshooting
If Flannel fails with a missing `br_netfilter` interface error:

1. Enable necessary kernel modules on worker nodes:
   ```bash
   sudo modprobe br_netfilter bridge vxlan overlay
   printf "overlay\nbr_netfilter\nvxlan\n" | sudo tee -a /etc/modules
   ```

2. Set required sysctl parameters:
   ```bash
   cat <<EOF | sudo tee /etc/sysctl.d/k8s-net.conf
   net.bridge.bridge-nf-call-iptables=1
   net.bridge.bridge-nf-call-ip6tables=1
   net.ipv4.ip_forward=1
   EOF
   sudo sysctl --system
   ```

3. Restart daemon services:
   ```bash
   sudo systemctl restart containerd
   sudo systemctl restart kubelet
   ```

4. Force CNI pods restart from the Master node:
   ```bash
   kubectl delete pods -n kube-flannel --all
   kubectl get pods -n kube-flannel -w
   ```

---

## 7. Run and Test the CLI Utility

After completing the configurations, switch to the master node `ncn-m001` and verify the execution of the management script.

1. Navigate to the utility directory:
   ```bash
   cd /path/to/cray-iscsi-cli
   ```

2. Test target node discovery:
   ```bash
   python3 src/main.py get nodes
   ```

3. View configured target LUNs:
   ```bash
   python3 src/main.py get luns
   ```

4. Check active sessions on the initiator nodes:
   ```bash
   python3 src/main.py get sessions
   ```

5. Fetch LUN read statistics:
   ```bash
   python3 src/main.py get metrics --name ncn-w001
   ```

---

## 8. Configure a CLI Alias

To simplify command execution, create a wrapper script that exposes the utility as a system-wide command named `cray`.

1. Create the executable wrapper:

   ```bash
   sudo nano /usr/local/bin/cray
   ```

2. Add the following content:

   ```bash
   #!/bin/bash
   python3 /home/iscsi/python-cli/src/main.py "$@"
   ```

   > Replace `/home/iscsi/python-cli/src/main.py` with the actual path to the CLI entry point if it differs in your environment.

3. Make the wrapper executable:

   ```bash
   sudo chmod +x /usr/local/bin/cray
   ```

4. Verify the command is available:

   ```bash
   which cray
   ```

   Expected output:

   ```bash
   /usr/local/bin/cray
   ```

5. Run the CLI using the new command:

   ```bash
   cray get nodes
   ```

   ```bash
   cray get luns
   ```

   ```bash
   cray get sessions
   ```

   ```bash
   cray get metrics --name ncn-w001
   ```

This wrapper forwards all arguments directly to the Python CLI, allowing the utility to be invoked as a native command from any location on the system.

One small correction: if your entry point is `src/main.py`, the wrapper should point to that file:

```bash
#!/bin/bash
python3 /home/iscsi/python-cli/src/main.py "$@"
````
rather than:

```bash
python3 /home/iscsi/python-cli/main.py "$@"
```
unless `main.py` is actually located at the project root.


## 9. Operating Assumptions and Limitations

### Assumptions
- **Kubernetes Access**: The cluster APIs are reachable, and target/initiator nodes are labeled appropriately inside the K8s cluster.
- **SSH Connectivity**: `pdsh` is installed on `ncn-m001` and is configured to run parallel remote ssh commands as `root` without passwords.
- **Directory Structures**:
  - Targets: The iSCSI targets config exists at `/sys/kernel/config/target/iscsi`.
  - Initiators: Active mounts and session nodes map back to `/dev/sd*` disk blocks.
- **LUN metrics**: The system log interface and udev paths (`udev_path`) are stable across restarts.

### Limitations
- **Node availability**: Unreachable target or initiator VMs will result in missing fields or error logs for that host during metric collections.
