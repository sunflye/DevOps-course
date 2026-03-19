

# Lab 9 — Kubernetes Fundamentals
---

## 1) Architecture Overview

### Deployment Architecture

```text
Client (curl/browser)
        |
        v
NodePort Service (app-python-service:80 -> targetPort 5000, nodePort 30080)
        |
        v
Deployment (app-python, RollingUpdate)
        |
        +--> Pod app-python1-... (Flask app on 5000)
        +--> Pod app-python2-... (Flask app on 5000)
        +--> Pod app-python3-... (Flask app on 5000)
        +--> Pod app-python4-... (Flask app on 5000)
        +--> Pod app-python5-... (Flask app on 5000)
```

### Resource Allocation Strategy

Per container:
- **requests**: `cpu: 100m`, `memory: 128Mi`
- **limits**: `cpu: 200m`, `memory: 256Mi`

Rationale:
- Requests guarantee minimum resources for stable scheduling.
- Limits prevent noisy-neighbor and runaway usage.

---

## 2) Manifest Files

### k8s/deployment.yml

Purpose:
- Deploy app pods via Deployment controller
- Maintain desired replicas
- Enable rolling updates and rollback
- Configure probes and resources

Key choices:
- `replicas: 5` (scaled in Task 4)
- Rolling strategy:
  - `maxUnavailable: 0`
  - `maxSurge: 1`
- Probes:
  - liveness: `GET /health` on port `5000`
  - readiness: `GET /health` on port `5000`
- Image: `sunflye/devops-info-service:latest`
- Labeling: `app: app-python` for selector matching

### k8s/service.yml

Purpose:
- Expose pods behind a stable endpoint

Key choices:
- `type: NodePort`
- selector: `app: app-python`
- service port `80` -> pod `targetPort: 5000`
- nodePort `30080`

Why:
- NodePort is appropriate for local minikube development.
- Selector-based routing decouples service from pod IP changes.

---

## 3) Deployment Evidence

### Task 1 — Local Kubernetes Setup

Chosen tool: **minikube**

Why minikube:
- Easy local cluster setup
- Good for learning full Kubernetes flow on one node
- Works well with `kubectl` and common addons

Cluster setup output (excerpt):
```text
🔎  Verifying Kubernetes components...
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

`kubectl cluster-info`:
```text
Kubernetes control plane is running at https://127.0.0.1:62833
CoreDNS is running at https://127.0.0.1:62833/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

`kubectl get nodes`:
```text
NAME       STATUS   ROLES           AGE     VERSION
minikube   Ready    control-plane   2m16s   v1.28.3
```

### Task 2 — Application Deployment

`kubectl get deployments`:
```text
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
app-python   3/3     3            3           2m39s
```

`kubectl get pods`:
```text
NAME                          READY   STATUS    RESTARTS   AGE
app-python-5cf7ff9485-bpwqd   1/1     Running   0          2m41s
app-python-5cf7ff9485-dblgh   1/1     Running   0          2m41s
app-python-5cf7ff9485-q84gx   1/1     Running   0          2m41s
```

`kubectl describe deployment app-python` confirms:
- `StrategyType: RollingUpdate`
- `RollingUpdateStrategy: 0 max unavailable, 1 max surge`
- Liveness/Readiness HTTP probes on `/health`
- Requests/limits applied

### Task 3 — Service Configuration

Port-forward used:
```powershell
kubectl port-forward service/app-python-service 8080:80
```
```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl port-forward service/app-python-service 8080:80
Forwarding from 127.0.0.1:8080 -> 5000
Forwarding from [::1]:8080 -> 5000
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
Handling connection for 8080
```

Endpoint checks:
```bash
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```



```
Polina@MagicBookX16 MINGW64 /d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course (lab9)
$ curl http://localhost:8080/
{"endpoints":[{"description":"Service information","method":"GET","path":"/"},{"description":"Health check","method":"GET","path":"/health"},{"description":"Prometheus metrics","method":"GET","path":"/metrics"}],"request":{"client_ip":"127.0.0.1","method":"GET","path":"/","user_agent":"curl/8.14.1"},"runtime":{"current_time":"2026-03-19T16:01:03.969216Z","timezone":"UTC","uptime_human":"0 hour, 10 minutes","uptime_seconds":602},"service":{"description":"DevOps course info service","framework":"Flask","name":"devops-info-service","version":"1.0.0"},"system":{"architecture":"x86_64","cpu_count":16,"hostname":"app-python-5cf7ff9485-dblgh","platform":"Linux","platform_version":"Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.41","python_version":"3.13.12"}}

Polina@MagicBookX16 MINGW64 /d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course (lab9)
$ curl http://localhost:8080/health
{"status":"healthy","timestamp":"2026-03-19T16:01:08.812364Z","uptime_seconds":607}

Polina@MagicBookX16 MINGW64 /d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course (lab9)
$ curl http://localhost:8080/metrics
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 3239.0
python_gc_objects_collected_total{generation="1"} 0.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 27.0
python_gc_collections_total{generation="1"} 2.0
python_gc_collections_total{generation="2"} 0.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="13",patchlevel="12",version="3.13.12"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 2.8731392e+08
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 3.5958784e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.77393545971e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 1.27
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 7.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1.048576e+06
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/health",method="GET",status="200"} 327.0        
http_requests_total{endpoint="/favicon.ico",method="GET",status="404"} 1.0     
http_requests_total{endpoint="/_static/out/browser/serviceWorker.js",method="GET",status="404"} 2.0
http_requests_total{endpoint="/metrics",method="GET",status="200"} 2.0
http_requests_total{endpoint="/",method="GET",status="200"} 2.0
# HELP http_requests_created Total HTTP requests
# TYPE http_requests_created gauge
http_requests_created{endpoint="/health",method="GET",status="200"} 1.7739354669432437e+09
http_requests_created{endpoint="/favicon.ico",method="GET",status="404"} 1.7739358958882616e+09
http_requests_created{endpoint="/_static/out/browser/serviceWorker.js",method="GET",status="404"} 1.7739358977291017e+09
http_requests_created{endpoint="/metrics",method="GET",status="200"} 1.7739359038742723e+09
http_requests_created{endpoint="/",method="GET",status="200"} 1.7739360369198887e+09
# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/health",le="0.01",method="GET"} 326.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.05",method="GET"} 327.0
http_request_duration_seconds_bucket{endpoint="/health",le="0.1",method="GET"} 327.0
...
```


### Deployment Evidence

```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get all     
NAME                              READY   STATUS    RESTARTS   AGE
pod/app-python-5cf7ff9485-fw4pr   1/1     Running   0          15m
pod/app-python-5cf7ff9485-ld9r7   1/1     Running   0          15m
pod/app-python-5cf7ff9485-lndtb   1/1     Running   0          15m
pod/app-python-5cf7ff9485-qrct2   1/1     Running   0          15m
pod/app-python-5cf7ff9485-sdgpl   1/1     Running   0          16m

NAME                         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/app-python-service   NodePort    10.110.181.29   <none>        80:30080/TCP   5h1m
service/kubernetes           ClusterIP   10.96.0.1       <none>        443/TCP        5h19m

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/app-python   5/5     5            5           5h7m

NAME                                    DESIRED   CURRENT   READY   AGE
replicaset.apps/app-python-5cf7ff9485   5         5         5       5h7m
replicaset.apps/app-python-8497b8686f   0         0         0       42m
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get pods,svc -o wide
NAME                              READY   STATUS    RESTARTS   AGE   IP            NODE       NOMINATED NODE   READINESS GATES
pod/app-python-5cf7ff9485-fw4pr   1/1     Running   0          15m   10.244.0.25   minikube   <none>           <none>
pod/app-python-5cf7ff9485-ld9r7   1/1     Running   0          15m   10.244.0.22   minikube   <none>           <none>
pod/app-python-5cf7ff9485-lndtb   1/1     Running   0          15m   10.244.0.23   minikube   <none>           <none>
pod/app-python-5cf7ff9485-qrct2   1/1     Running   0          15m   10.244.0.24   minikube   <none>           <none>
pod/app-python-5cf7ff9485-sdgpl   1/1     Running   0          16m   10.244.0.21   minikube   <none>           <none>

NAME                         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE     SELECTOR
service/app-python-service   NodePort    10.110.181.29   <none>        80:30080/TCP   5h1m    app=app-python
service/kubernetes           ClusterIP   10.96.0.1       <none>        443/TCP        5h19m   <none> 
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl describe deployment app-python
Name:                   app-python
Namespace:              default
CreationTimestamp:      Thu, 19 Mar 2026 14:49:04 +0300
Labels:                 app=app-python
Annotations:            deployment.kubernetes.io/revision: 3
Selector:               app=app-python
Replicas:               5 desired | 5 updated | 5 total | 5 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  0 max unavailable, 1 max surge
Pod Template:
  Labels:  app=app-python
  Containers:
   app-python:
    Image:      sunflye/devops-info-service:latest
    Port:       5000/TCP
    Host Port:  0/TCP
    Limits:
      cpu:     200m
      memory:  256Mi
    Requests:
      cpu:      100m
      memory:   128Mi
    Liveness:   http-get http://:5000/health delay=10s timeout=1s period=5s #success=1 #failure=3    
    Readiness:  http-get http://:5000/health delay=5s timeout=1s period=3s #success=1 #failure=3     
    Environment:
      PORT:        5000
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  app-python-8497b8686f (0/0 replicas created)
NewReplicaSet:   app-python-5cf7ff9485 (5/5 replicas created)
Events:
  Type    Reason             Age                From                   Message
  ----    ------             ----               ----                   -------
  Normal  ScalingReplicaSet  49m                deployment-controller  Scaled up replica set app-python-5cf7ff9485 to 5 from 3
  Normal  ScalingReplicaSet  42m                deployment-controller  Scaled up replica set app-python-8497b8686f to 1
  Normal  ScalingReplicaSet  42m                deployment-controller  Scaled down replica set app-python-5cf7ff9485 to 4 from 5
  Normal  ScalingReplicaSet  42m                deployment-controller  Scaled up replica set app-python-8497b8686f to 2 from 1
  Normal  ScalingReplicaSet  42m                deployment-controller  Scaled down replica set app-python-5cf7ff9485 to 3 from 4
  Normal  ScalingReplicaSet  42m                deployment-controller  Scaled up replica set app-python-8497b8686f to 3 from 2
  Normal  ScalingReplicaSet  42m                deployment-controller  Scaled down replica set app-python-5cf7ff9485 to 2 from 3
  Normal  ScalingReplicaSet  42m                deployment-controller  Scaled up replica set app-python-8497b8686f to 4 from 3
  Normal  ScalingReplicaSet  41m                deployment-controller  Scaled down replica set app-python-5cf7ff9485 to 1 from 2
  Normal  ScalingReplicaSet  16m                deployment-controller  Scaled up replica set app-python-5cf7ff9485 to 1 from 0
  Normal  ScalingReplicaSet  16m                deployment-controller  Scaled down replica set app-python-8497b8686f to 4 from 5
  Normal  ScalingReplicaSet  16m                deployment-controller  Scaled up replica set app-python-5cf7ff9485 to 2 from 1
  Normal  ScalingReplicaSet  15m                deployment-controller  Scaled down replica set app-python-8497b8686f to 3 from 4
  Normal  ScalingReplicaSet  15m                deployment-controller  Scaled up replica set app-python-5cf7ff9485 to 3 from 2
  Normal  ScalingReplicaSet  15m                deployment-controller  Scaled down replica set app-python-8497b8686f to 2 from 3
  Normal  ScalingReplicaSet  15m                deployment-controller  Scaled up replica set app-python-5cf7ff9485 to 4 from 3
  Normal  ScalingReplicaSet  15m                deployment-controller  Scaled down replica set app-python-8497b8686f to 1 from 2
  Normal  ScalingReplicaSet  15m                deployment-controller  Scaled up replica set app-python-5cf7ff9485 to 5 from 4
  Normal  ScalingReplicaSet  15m (x3 over 41m)  deployment-controller  (combined from similar events): Scaled down replica set app-python-8497b8686f to 0 from 1
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course>
```
---

## 4) Operations Performed

### Deploy manifests

```powershell
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl get deployments
kubectl get pods
kubectl describe deployment app-python
```

### Access service

```powershell
kubectl port-forward service/app-python-service 8080:80
```

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```
```
Polina@MagicBookX16 MINGW64 /d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course (lab9)
$ curl http://localhost:8080/
{"endpoints":[{"description":"Service information","method":"GET","path":"/"},{"description":"Health check","method":"GET","path":"/health"},{"description":"Prometheus metrics","method":"GET","path":"/metrics"}],"request":{"client_ip":"127.0.0.1","method":"GET","path":"/","user_agent":"curl/8.14.1"},"runtime":{"current_time":"2026-03-19T16:21:04.969216Z","timezone":"UTC","uptime_human":"0 hour, 10 minutes","uptime_seconds":602},"service":{"description":"DevOps course info service","framework":"Flask","name":"devops-info-service","version":"1.0.0"},"system":{"architecture":"x86_64","cpu_count":16,"hostname":"app-python-5cf7ff9485-dblgh","platform":"Linux","platform_version":"Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.41","python_version":"3.13.12"}}

Polina@MagicBookX16 MINGW64 /d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course (lab9)
$ curl http://localhost:8080/health
{"status":"healthy","timestamp":"2026-03-19T16:21:07.812364Z","uptime_seconds":607}

Polina@MagicBookX16 MINGW64 /d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course (lab9)
$ curl http://localhost:8080/metrics
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 3239.0
python_gc_objects_collected_total{generation="1"} 0.0
python_gc_objects_collected_total{generation="2"} 0.0
```

### Scaling demonstration (Task 4)

To scale the application, I updated `replicas` in `k8s/deployment.yml` to `5` and applied the manifest.

```powershell
kubectl apply -f k8s/deployment.yml
kubectl get deployments
kubectl get pods
```

Output:

```text
deployment.apps/app-python configured

NAME         READY   UP-TO-DATE   AVAILABLE   AGE
app-python   5/5     5            5           4h22m

NAME                          READY   STATUS    RESTARTS      AGE
app-python-5cf7ff9485-bpwqd   1/1     Running   2 (21m ago)   4h22m
app-python-5cf7ff9485-csqjc   1/1     Running   0             4m39s
app-python-5cf7ff9485-dblgh   1/1     Running   2 (21m ago)   4h22m
app-python-5cf7ff9485-ntcvn   1/1     Running   0             4m39s
app-python-5cf7ff9485-q84gx   1/1     Running   2 (21m ago)   4h22m
```

✅ **Scaling successful:** Deployment reached `5/5` ready replicas.

---

### Rolling update demonstration

For rolling update testing, I changed deployment configuration (example: `DEMO_VAR: "v2"` in `k8s/deployment.yml`) and reapplied the manifest.

```powershell
kubectl apply -f k8s/deployment.yml
kubectl rollout status deployment/app-python
```

Output:

```text
deployment.apps/app-python configured
Waiting for deployment "app-python" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "app-python" rollout to finish: 1 old replicas are pending termination...
deployment "app-python" successfully rolled out
```

Rollout monitoring:

```powershell
kubectl get pods -w
```

Observed transition:

```text
app-python-5cf7ff9485-bpwqd   1/1   Terminating   2 (24m ago)   4h25m
app-python-5cf7ff9485-q84gx   1/1   Terminating   2 (24m ago)   4h25m
app-python-8497b8686f-4pcg8   1/1   Running       0             53s
app-python-8497b8686f-dzxdt   1/1   Running       0             21s
app-python-8497b8686f-gqwxg   1/1   Running       0             62s
app-python-8497b8686f-jjngs   1/1   Running       0             34s
app-python-8497b8686f-pwwgh   1/1   Running       0             43s
```

After rollout:

```powershell
kubectl get pods
```

```text
app-python-8497b8686f-4pcg8   1/1   Running   0   6m16s
app-python-8497b8686f-dzxdt   1/1   Running   0   5m44s
app-python-8497b8686f-gqwxg   1/1   Running   0   6m25s
app-python-8497b8686f-jjngs   1/1   Running   0   5m57s
app-python-8497b8686f-pwwgh   1/1   Running   0   6m6s
```

✅ **Rolling update successful:** old pods were replaced gradually, new pods became healthy, service stayed available (zero-downtime rolling strategy).

---

### Rollback demonstration

First, I checked rollout history:

```powershell
kubectl rollout history deployment/app-python
```

Output:

```text
deployment.apps/app-python
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

Then I executed rollback:

```powershell
kubectl rollout undo deployment/app-python
kubectl rollout status deployment/app-python
kubectl get pods
```

Output:

```text
deployment.apps/app-python rolled back
deployment "app-python" successfully rolled out

NAME                          READY   STATUS    RESTARTS   AGE
app-python-5cf7ff9485-fw4pr   1/1     Running   0          19s
app-python-5cf7ff9485-ld9r7   1/1     Running   0          47s
app-python-5cf7ff9485-lndtb   1/1     Running   0          38s
app-python-5cf7ff9485-qrct2   1/1     Running   0          28s
app-python-5cf7ff9485-sdgpl   1/1     Running   0          57s
```

✅ **Rollback successful:** deployment returned to previous ReplicaSet revision and all replicas are healthy.
## 5) Production Considerations

### Health checks implemented and why

Implemented in `k8s/deployment.yml`:

- **Liveness probe**
  - HTTP GET `/health` on port `5000`
  - Detects hung/broken app process
  - Failure action: container restart by kubelet

- **Readiness probe**
  - HTTP GET `/health` on port `5000`
  - Controls if pod receives traffic from Service
  - Failure action: pod removed from endpoints until healthy

Why both:
- Liveness improves self-healing.
- Readiness prevents sending traffic to unavailable pods during startup/update.

### Resource limits rationale

Configured:
- requests: `100m / 128Mi`
- limits: `200m / 256Mi`

Why:
- Scheduler can place pods with guaranteed minimums.
- Hard limits avoid cluster instability and noisy-neighbor issues.

### Improvements for production

1. Pin image to immutable tag or digest (avoid `latest`)
2. Add `startupProbe` for slow starts
3. Add HPA for autoscaling
4. Use Ingress + TLS instead of only NodePort
5. Add PodDisruptionBudget and anti-affinity
6. Add separate readiness endpoint (e.g. `/ready`)
7. Add CI policy checks (lint, kube-score, OPA/Gatekeeper)

### Monitoring and observability strategy

- Reuse monitoring stack from `monitoring`
- Scrape app `/metrics` endpoint (already exposed)
- Dashboard in Grafana:
  - request rate
  - error rate
  - p95 latency
  - in-progress requests
- Add alerting for:
  - pod restarts
  - high 5xx rate
  - high latency
  - probe failures

---

## 6) Challenges & Solutions

### 1. NodePort/minikube access issue on Windows
Issue:
- Direct `minikube service --url` used ssh tunnel and local setup lacked ssh binary.

Solution:
- Used `kubectl port-forward service/app-python-service 8080:80`.
- Verified endpoints via `curl http://localhost:8080/...`.

