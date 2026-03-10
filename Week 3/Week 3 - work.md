# Configuring iSCSI in a Kubernetes Cluster

Goal:

- Configure 5 nodes -> 1 master node + 4 worker nodes
- Configure 4 worker nodes -> 2 iscsi target + 2 iscsi client
- Gather data from all these nodes from the master node

## Base Image: Rocky Linux 8

Rocky Linux 8 was chosen as the base image for the virtual machines because it provides a stable environment with native support for iSCSI tools such as targetcli and Open-iSCSI. These tools are required for configuring iSCSI targets and initiators in the cluster.

Although openSUSE Leap was also considered, the development system had limited disk space (approximately 20 GB available) while running two virtual machines simultaneously. Rocky Linux was selected because its minimal installation requires less disk space and system resources, allowing multiple VMs to run comfortably within the available storage.

## Kubernetes Platform: k3s

SUSE also has a enterprise-grade kubernetes management platform called Rancher .
I needed a open source alternative to it, upon searching found k3s, which was actually developed by the rancher team.

## Configuring iSCSI

1. Create 2 VMs with Rocky Linux 8 Minimal ISO Image
2. Name them as iscsi-client and iscsi-target
3. Before installing any packages set the ethernet connection up, Run:

```
nmcli connection show

nmcli connection up <name>

# Example: nmcli connection up enp1s0
```

4. Follow the docs and setup client and target vms

- Link: https://reintech.io/blog/configuring-iscsi-initiator-target-rocky-linux-9

## Configuring Kubernetes

1 Master Node + 2 Worker Nodes ( iSCSI Client + iSCSI Target )

### 1. Prepare the machines

- You need three machines:

```
control-plane  (host machine)
iscsi-target   (VM)
iscsi-client   (VM)
```

- Verify connectivity:

```
ping <vm-ip>
ssh root@<vm-ip>
```

- Example in my setup:

```
192.168.122.33   iscsi-client
192.168.122.103  iscsi-target
```


### 2. Install K3s control plane

- Run on the **host machine**:

```
curl -sfL https://get.k3s.io | sh -
```

- Verify cluster:

```
sudo k3s kubectl get nodes -o wide
```

- Expected:

```
sasank-v-loq-15aph8   control-plane <internal-ip>
```

- Get the node join token:

```
sudo cat /var/lib/rancher/k3s/server/node-token
```

- Change the token if needed

```
sudo nano /var/lib/rancher/k3s/server/node-token

# change the last set of characters in my case
K1094021a81659f84eceb2a52c42a62381df6f5a826cff402cfb9c8b56d9fc15f4e::server:mycluster123
```



### 3. Join worker nodes

Run this on **both VMs**.

- Turn on the ethernet connection

```
nmcli connection show

# Replace <name> with the actual name shown before

nmcli connection up <name>

# Example: nmcli connection up enp1s0
```

- Install k3s

```
curl -sfL https://get.k3s.io | \
K3S_URL=https://<control-plane-ip>:6443 \
K3S_TOKEN=<node-token> \
sh -
```

- Set the node name

```
nano /etc/systemd/system/k3s-agent.service

# Add this line to the ExecStart
--node-name iscsi-node-name

# Example
ExecStart=/usr/local/bin/k3s agent /
--node-name iscsi-node-name
```

- To change the env variables (K3S_TOKEN / K3S_URL)

```
nano /etc/systemd/system/k3s-agent.service.env

# Modify and press Ctrl + X -> y -> Enter
```

- After any modifications reload the system daemon

```
systemctl daemon-reload
systemctl restart k3s-agent
```

- Verify cluster:

```
sudo k3s kubectl get nodes
```

- Expected:

```
iscsi-client
iscsi-target
sasank-v-loq-15aph8
```



### 4. Label the nodes

- This prevents the DaemonSet from running on the control plane.

```
sudo k3s kubectl label node iscsi-client storage-node=true
sudo k3s kubectl label node iscsi-target storage-node=true
```

- Verify:

```
sudo k3s kubectl get nodes --show-labels
```



### 5. Build the daemon container

- Example Dockerfile:

```
FROM rockylinux:8

RUN dnf install -y iscsi-initiator-utils targetcli procps iproute && \
    dnf clean all

COPY collect.sh /collect.sh
RUN chmod +x /collect.sh

CMD ["/collect.sh"]
```

- Example collector script:

```
#!/bin/bash

while true
do
    echo "Node: $(hostname)"

    echo "Active iSCSI sessions"
    iscsiadm -m session || true

    echo "Configured targets"
    targetcli ls || true

    sleep 60
done
```

- Build the image:

```
docker build -t iscsi-monitor:latest .
```



### 6. Export the image

Because **containerd** is used by K3s instead of Docker.

```
docker save iscsi-monitor:latest -o iscsi-monitor.tar
```



### 7. Copy image to worker nodes

```
scp iscsi-monitor.tar root@192.168.122.33:/tmp
scp iscsi-monitor.tar root@192.168.122.103:/tmp
```


### 8. Import image into containerd

- On **each worker node**:

```
k3s ctr images import /tmp/iscsi-monitor.tar
```

- Verify:

```
k3s ctr images ls
```

- You should see:

```
docker.io/library/iscsi-monitor:latest
```



### 9. Create the DaemonSet

`iscsi-daemonset.yaml`

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: iscsi-monitor
spec:
  selector:
    matchLabels:
      app: iscsi-monitor
  template:
    metadata:
      labels:
        app: iscsi-monitor
    spec:
      nodeSelector:
        storage-node: true
    spec:
      containers:
      - name: iscsi-monitor
        image: iscsi-monitor:latest
        imagePullPolicy: Never
        securityContext:
          privileged: true
        volumeMounts:
        - name: host-dev
          mountPath: /dev
        - name: host-run
          mountPath: /run
        - name: host-proc
          mountPath: /hostproc
      volumes:
      - name: host-dev
        hostPath:
          path: /dev
      - name: host-run
        hostPath:
          path: /run
      - name: host-proc
        hostPath:
          path: /proc
```

---

### 10. Deploy the DaemonSet

```
sudo k3s kubectl apply -f iscsi-daemonset.yaml
```



### 11. Verify pods

```
sudo k3s kubectl get pods -o wide
```

- Expected:

```
iscsi-monitor-xxxxx   Running   iscsi-client
iscsi-monitor-yyyyy   Running   iscsi-target
```

Exactly **one pod per node**.


# 12. View collected data

```
kubectl logs <pod-name>
```

- Example:

```
kubectl logs iscsi-monitor-xxxxx
```

- You will see:

```
Node: iscsi-target
Active iSCSI sessions
...
Configured targets
...
```

---

### Final architecture

```
                   Kubernetes Control Plane
                        (Host OS)
                           |
                           |
        --------------------------------------------
        |                                          |
   iscsi-target VM                          iscsi-client VM
        |                                          |
   daemonset pod                             daemonset pod
        |                                          |
   collect iSCSI data                        collect iSCSI data
```

# References:

- Rancher: https://www.rancher.com/about
- k3s Docs: https://docs.k3s.io/
- k3s Installation: https://docs.k3s.io/installation/configuration
- Kubernetes: https://kubernetes.io/docs/home/
- Kubernetes DaemonSet: https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/
- iSCSI Configuration in Rocky Linux: https://reintech.io/blog/configuring-iscsi-initiator-target-rocky-linux-9
