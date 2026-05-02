# Lab 15 — StatefulSets & Persistent Storage

## 1. StatefulSet Overview

### 1.1 StatefulSet Overview: Why StatefulSet?
StatefulSet is a specialized workload controller used to manage applications that require a persistent "identity" or state. Unlike standard Deployments, which treat pods as completely interchangeable and "cattle," StatefulSets treat them as "pets"—unique instances that must be managed with care.

**StatefulSets provide critical guarantees:**
- **Stable Network ID:** A pod will always have the same hostname (e.g., `app-0`), even after rescheduling.
- **Stable Storage:** Each pod maps to its own Persistent Volume (PV). If a pod is deleted and recreated, it re-attaches to the exact same volume it had before.
- **Ordered Operations:** Pods are started, updated, and deleted in a specific order (0, 1, 2...), which is essential for database clusters that need to establish a quorum.

### 1.2 Comparison: Deployment vs StatefulSet

| Feature | Deployment (Stateless) | StatefulSet (Stateful) |
|:---|:---|:---|
| **Pod Naming** | Random hash suffix (`app-xyz123`) | Fixed ordinal index (`app-0`, `app-1`) |
| **Storage Model** | Shared volume or ephemeral disks | **Dedicated volume per pod instance** |
| **Network Identity**| Dynamic (access via Service IP) | Fixed DNS name for each specific pod |
| **Scaling** | Parallel and immediate | Sequential and ordered (0 -> 1 -> 2) |
| **Best For** | Web APIs, workers, stateless apps | Databases (PostgreSQL), Queues (Kafka) |

### 1.3 Headless Services & DNS
To enable stable networking, StatefulSets require a **Headless Service** (`clusterIP: None`).
- **Function:** Unlike a normal service that load-balances traffic, a Headless Service allows the user (or other pods) to discover the direct IP addresses of all pods in the set.
- **DNS Resolution:** With a Headless Service named `app-headless`, the DNS record for `app-0` becomes `app-0.app-headless.default.svc.cluster.local`. This is how database nodes find each other to synchronize data.

---

## 2. Resource Verification

### Implementation: Convert Deployment to StatefulSet

To transform the application into a stateful workload, the following changes were implemented in the Helm chart:

#### 2.1 StatefulSet Template
Created [`k8s/app-python/templates/statefulset.yaml`](k8s/app-python/templates/statefulset.yaml) which defines:
- `kind: StatefulSet`
- `serviceName`: Points to the headless service for stable DNS.
- `volumeClaimTemplates`: Automatically provisions a unique PersistentVolumeClaim (PVC) for each pod instance.

#### 2.2 Headless Service
Created [`k8s/app-python/templates/service-headless.yaml`](k8s/app-python/templates/service-headless.yaml) with `clusterIP: None`. This service is responsible for the network identity of the pods.

#### 2.3 VolumeClaimTemplates Configuration
Each pod now has independent storage. The configuration is driven by `values.yaml`:
```yaml
persistence:
  enabled: true
  size: 100Mi
```

```
kubectl get po,sts,svc,pvc
```

```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get po,sts,svc,pvc
NAME                                        READY   STATUS    RESTARTS      AGE
pod/app-python-sts-0                        1/1     Running   0             28s
pod/app-python-sts-1                        1/1     Running   0             22s
pod/app-python-sts-2                        1/1     Running   0             18s

NAME                              READY   AGE
statefulset.apps/app-python-sts   3/3     28s

NAME                               TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)           
  AGE
service/app-python-sts             NodePort    10.111.77.34     <none>        80:30090/TCP        28s
service/app-python-sts-headless    ClusterIP   None             <none>        80/TCP            
  28s

NAME                                          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/data-app-python-sts-0   Bound    pvc-f58709a2-c710-441d-88db-dd83c60b404e   100Mi      RWO            standard       28s
persistentvolumeclaim/data-app-python-sts-1   Bound    pvc-c051cb8a-dff1-4464-a025-da09e697b2d4   100Mi      RWO            standard       22s
persistentvolumeclaim/data-app-python-sts-2   Bound    pvc-4b652921-9ef2-425c-8299-8b73d189d13f   100Mi      RWO            standard       18s
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course>

```

## 3. Network Identity
Each pod in the StatefulSet is assigned a stable DNS name following the pattern:
`<pod-name>.<service-name>.<namespace>.svc.cluster.local`

**Evidence:**
```powershell
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec app-python-sts-0 -- getent hosts app-python-sts-1.app-python-sts-headless.default.svc.cluster.local
10.244.1.19     app-python-sts-1.app-python-sts-headless.default.svc.cluster.local

(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec app-python-sts-0 -- getent hosts app-python-sts-2.app-python-sts-headless.default.svc.cluster.local
10.244.1.20     app-python-sts-2.app-python-sts-headless.default.svc.cluster.local
```

## 4. Per-Pod Storage Evidence
By accessing pods individually via port-forwarding, I verified that they maintain unique data on their dedicated volumes.

**Verification:**
1. Accessed `app-python-sts-0` via port-forwarding and refreshed the page 4 times.
2. Accessed `app-python-sts-1` via port-forwarding and refreshed the page 1 time.

```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl port-forward pod/app-python-sts-0 8080:5000        
Forwarding from 127.0.0.1:8080 -> 5000
Forwarding from [::1]:8080 -> 5000
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl port-forward pod/app-python-sts-1 8081:5000
Forwarding from 127.0.0.1:8081 -> 5000
Forwarding from [::1]:8081 -> 5000
Handling connection for 8081
```

**Evidence:**
```powershell
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec app-python-sts-0 -- cat /data/visits
4
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec app-python-sts-1 -- cat /data/visits
1
```
This confirms that `volumeClaimTemplates` correctly provisioned independent storage for each pod ordinal.

## 5. Persistence Test

The goal of this test was to verify that data survives pod deletion and is correctly re-attached because of the stable identity of instances in a StatefulSet.

**Steps and Evidence:**

1. **Check value before deletion**
2. **Delete the pod instance**
3. **Verify pod recreation**
4. **Verify data persistence**:
```
так?
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec app-python-sts-0 -- cat /data/visits
4
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl delete pod app-python-sts-0
pod "app-python-sts-0" deleted
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get po -w 
NAME                                    READY   STATUS        RESTARTS      AGE
app-python-sts-0                        1/1     Terminating   0             13m
app-python-sts-1                        1/1     Running       0             13m
app-python-sts-2                        1/1     Running       0             13m

(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get po -w
NAME                                    READY   STATUS    RESTARTS      AGE
app-python-sts-0                        1/1     Running   0             7s
app-python-sts-1                        1/1     Running   0             13m
app-python-sts-2                        1/1     Running   0             13m
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec app-python-sts-0 -- cat /data/visits
4
```

**Conclusion:**
The test confirms that the PVC `data-app-python-sts-0` is strictly bound to the pod instance index `0`. When the pod was deleted, the storage remained intact and was automatically remounted to the new pod, successfully preserving the application state.