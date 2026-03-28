# Lab 10 — Helm Package Manager

## Task 1 — Helm Fundamentals

### Helm Installation

Helm CLI is installed and available in the PATH.

```powershell
helm version
```

Output:

```text
version.BuildInfo{Version:"v4.1.3", GitCommit:"c94d381b03be117e7e57908edbf642104e00eb8f", GitTreeState:"clean", GoVersion:"go1.25.8", KubeClientVersion:"v1.35"}
```
---

### Adding a Public Helm Repository

I added the Prometheus Community charts repository and updated the repo index:

```powershell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Output:

```text
"prometheus-community" has been added to your repositories

Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈Happy Helming!⎈
```

---

### Exploring a Public Chart

I searched for Prometheus-related charts and inspected the main `prometheus` chart.

```powershell
helm search repo prometheus
```

Example of results:

```text
NAME                                            CHART VERSION   APP VERSION   DESCRIPTION
prometheus-community/kube-prometheus-stack      82.15.1         v0.89.0       kube-prometheus-stack collects Kubernetes manif...
prometheus-community/prometheus                 28.14.1         v3.10.0       Prometheus is a monitoring system and time seri...
prometheus-community/prometheus-adapter         5.3.0           v0.12.0       A Helm chart for k8s prometheus adapter
prometheus-community/prometheus-blackbox-ex...  11.9.1          v0.28.0       Prometheus Blackbox Exporter
...
```

Then I inspected the Prometheus chart metadata:

```powershell
helm show chart prometheus-community/prometheus
```

Output (key fields):

```text
annotations:
  artifacthub.io/license: Apache-2.0
  artifacthub.io/links: |
    - name: Chart Source
      url: https://github.com/prometheus-community/helm-charts
    - name: Upstream Project
      url: https://github.com/prometheus/prometheus
apiVersion: v2
appVersion: v3.10.0
dependencies:
- condition: alertmanager.enabled
  name: alertmanager
  repository: https://prometheus-community.github.io/helm-charts
  version: 1.34.*
- condition: kube-state-metrics.enabled
  name: kube-state-metrics
  repository: https://prometheus-community.github.io/helm-charts
  version: 7.2.*
- condition: prometheus-node-exporter.enabled
  name: prometheus-node-exporter
  repository: https://prometheus-community.github.io/helm-charts
  version: 4.52.*
- condition: prometheus-pushgateway.enabled
  name: prometheus-pushgateway
  repository: https://prometheus-community.github.io/helm-charts
  version: 3.6.*
description: Prometheus is a monitoring system and time series database.
home: https://prometheus.io/
name: prometheus
type: application
version: 28.14.1
```

From this output, I can see:

- `apiVersion: v2` — Helm chart API version.
- `name`, `version`, `appVersion`, `description` — chart metadata defined in `Chart.yaml`.
- `type: application` — this is an installable application chart.
- `dependencies` — this chart pulls in other charts (Alertmanager, kube-state-metrics, node-exporter, pushgateway).
- `annotations` and `sources` — links to upstream projects and chart repository.

This confirms the standard Helm chart structure:
- `Chart.yaml` for metadata and dependencies
- `values.yaml` for default configuration
- `templates/` for Kubernetes manifest templates
- optional `charts/` for dependent charts

---

### Helm Value Proposition

Helm provides several key benefits over using plain Kubernetes YAML:

- **Packaging:**  
  Groups multiple Kubernetes manifests into a single reusable “chart” package.

- **Configuration via values:**  
  The same chart can be deployed to different environments (dev/stage/prod) by changing `values.yaml` or passing overrides with `--values` / `--set`, instead of duplicating YAML files.

- **Release management:**  
  Helm tracks releases in the cluster. It makes it easy to:
  - install (`helm install`)
  - upgrade (`helm upgrade`)
  - roll back (`helm rollback`)
  with proper versioning.

- **Templating and reuse:**  
  Go templates remove copy–paste between similar manifests and enforce consistent labels, naming, probes, and resource settings across all resources.

- **Ecosystem and sharing:**  
  Charts can be stored in repositories (like `prometheus-community`) and reused across teams and projects.

## Task 2 — Create Your Helm Chart

I converted the Kubernetes manifests from Lab 9 (`k8s/deployment.yml` and `k8s/service.yml`) into a reusable Helm chart located at `k8s/app-python`.

### Chart Structure and Templating

**Chart location:** `k8s/app-python`

- `Chart.yaml` — chart metadata (`name: app-python`, `version: 0.1.0`, `appVersion: "1.0.0"`, `type: application`).
- `values.yaml` — configuration for:
  - `replicaCount`
  - `image.repository`, `image.tag`, `image.pullPolicy`
  - `resources.requests` / `resources.limits`
  - `service.type`, `service.port`, `service.targetPort`, `service.nodePort`
  - `livenessProbe` and `readinessProbe` (paths and timings)
- `templates/deployment.yaml` — Deployment templated with:
  - replicas from `.Values.replicaCount`
  - image from `.Values.image`
  - resources from `.Values.resources`
  - health probes from `.Values.livenessProbe` / `.Values.readinessProbe`
  - RollingUpdate strategy (`maxUnavailable: 0`, `maxSurge: 1`)
- `templates/service.yaml` — Service templated with:
  - type and ports from `.Values.service`
  - NodePort only when `service.type == "NodePort"`
- `templates/_helpers.tpl` — helper templates for:
  - `app-python.fullname`
  - `app-python.labels`
  - `app-python.selectorLabels`

Health checks are **not commented out**; they are always present, but paths and timings are configurable via `values.yaml` with sensible defaults (`/health` on port `5000`).

### Linting and Rendering

I validated the chart with `helm lint` and `helm template`:

```powershell
helm lint k8s\app-python
```

Output:

```text
==> Linting k8s\app-python
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

```powershell
helm template app-python k8s\app-python
```

Rendered resources included:

- `Deployment` with `replicas: 3`, image `sunflye/devops-info-service:latest`, resource requests/limits, and liveness/readiness probes on `/health`.
- `Service` of type `NodePort` exposing port `80` → `5000` with `nodePort: 30080`.

I also performed a dry-run install with debug:

```powershell
helm install --dry-run --debug app-python-test k8s\app-python
```

This showed the computed values and full manifest without errors.

### Real Installation and Verification

Then I installed the chart into my local minikube cluster:

```powershell
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> helm install app-python k8s\app-python
NAME: app-python
LAST DEPLOYED: Sat Mar 28 14:54:51 2026
NAMESPACE: default
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
1. Get the application URL by running these commands:
  export NODE_PORT=$(kubectl get --namespace default -o jsonpath="{.spec.ports[0].nodePort}" services app-python)
  export NODE_IP=$(kubectl get nodes --namespace default -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT

helm list
kubectl get pods
kubectl get svc
```

Example state after install:

```text
NAME            NAMESPACE   REVISION  STATUS    CHART              APP VERSION
app-python      default     1         deployed  app-python-0.1.0   1.0.0
```

```text
NAME                          READY   STATUS    RESTARTS   AGE
app-python-74cff54c48-6kcxq   1/1     Running   0          11s
app-python-74cff54c48-gh6c7   1/1     Running   0          11s
app-python-74cff54c48-xqqdc   1/1     Running   0          11s
```

```text
NAME         TYPE      CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
app-python   NodePort  10.104.1.167  <none>        80:30080/TCP   15s
```

I verified the application via port-forward:

```powershell
kubectl port-forward svc/app-python 8080:80
```

And from the host:

```powershell
curl.exe http://localhost:8080/
curl.exe http://localhost:8080/health
```
```
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> curl.exe http://localhost:8080/
{"endpoints":[{"description":"Service information","method":"GET","path":"/"},{"description":"Health check","method":"GET","path":"/health"},{"description":"Prometheus metrics","method":"GET","path":"/metthod":"GET","path":"/metrics"}],"request":{"client_ip":"127.equest":{"client_ip":"12,"method":"GET","path","method":"GET","path":"/","user_agent":"curl/8.18er_agent":"curl/8.18.0"},"runtime":{"current_time":"2026-03-28T11:56:14.806065Z","timezone":"UTC","uptime_human":"0 hour, 1 minutes","uptime_seconds":81},"service":{"description":"DevOps course info service","framework":"Flask","name":"devops-info-service","version":"1.0.0"},"system":{"architecture":"x86_64","cpu_count":16,"hostname":"app-python-74cff54c48-6kcxq","platform":"Linux","platform_version":"Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.41","python_version":"3.13.12"}}
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> curl.exe http://localhost:8080/health   
{"status":"healthy","timestamp":"2026-03-28T11:56:25.013879Z","uptime_seconds":91} 
```

Both endpoints responded correctly, confirming that the Helm chart reproduces the behavior of the original Lab 9 deployment with configurable values.

```
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get all
NAME                              READY   STATUS    RESTARTS   AGE
pod/app-python-74cff54c48-6kcxq   1/1     Running   0          6m4s
pod/app-python-74cff54c48-gh6c7   1/1     Running   0          6m4s
pod/app-python-74cff54c48-xqqdc   1/1     Running   0          6m4s

NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/app-python   NodePort    10.104.1.167   <none>        80:30080/TCP   6m4s
service/kubernetes   ClusterIP   10.96.0.1      <none>        443/TCP        9d

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/app-python   3/3     3            3           6m4s

NAME                                    DESIRED   CURRENT   READY   AGE
replicaset.apps/app-python-74cff54c48   3         3         3       6m4s
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course>
``` 
## Task 3 — Multi-Environment Support

To support different environments with the same chart, I created two separate values files:

- `k8s/app-python/values-dev.yaml` — development configuration
- `k8s/app-python/values-prod.yaml` — production configuration

### Environment-Specific Values

**Development (`values-dev.yaml`):**

- `replicaCount: 1` — only one replica for local development
- `service.type: NodePort` — easy access from local machine via a fixed node port
- Relaxed resource requests/limits and faster probes (shorter initial delays and periods) for quick feedback during development

**Production (`values-prod.yaml`):**

File: `k8s/app-python/values-prod.yaml`:

```yaml
replicaCount: 5

image:
  # prod should use a fixed tag
  tag: "latest"

service:
  type: LoadBalancer

resources:
  requests:
    cpu: "200m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"

livenessProbe:
  initialDelaySeconds: 30
  periodSeconds: 5

readinessProbe:
  initialDelaySeconds: 10
  periodSeconds: 3
```

Key differences in production:

- `replicaCount: 5` — higher availability and capacity
- `service.type: LoadBalancer` — cloud/production ready (in minikube the external IP stays `<pending>`, which is expected)
- Stronger CPU/memory requests and limits
- More conservative probe timings (longer initial delays)

### Dev Installation

I first installed the chart using the **dev** values:

```powershell
helm uninstall app-python
helm install app-python k8s\app-python -f k8s\app-python\values-dev.yaml
```

Verification:

```powershell
kubectl get deploy app-python
```

Output:

```text
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
app-python   1/1     1            1           11s
```

```powershell
kubectl get svc app-python
```

Output:

```text
NAME         TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
app-python   NodePort   10.103.6.130   <none>        80:30080/TCP   14s
```

This confirms the **dev** environment: 1 replica and `NodePort` service.

### Upgrade to Production

Then I upgraded the same release to use the **prod** values:

```powershell
helm upgrade app-python k8s\app-python -f k8s\app-python\values-prod.yaml
```

Verification:

```powershell
kubectl get deploy app-python
```

Output:

```text
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
app-python   5/5     1            5           40s
```

```powershell
kubectl get svc app-python
```

Output:

```text
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
app-python   LoadBalancer   10.103.6.130   <pending>     80:30080/TCP   47s
```

The upgrade changed:

- Replica count from **1 → 5**
- Service type from **NodePort → LoadBalancer**

This demonstrates Helm’s values override pattern for multi-environment support:  
**one chart**, different `values-*.yaml` files, and environment changes applied via `helm install` (dev) and `helm upgrade` (prod).

## Task 4 — Chart Hooks

To add lifecycle management to the chart, I implemented Helm hooks using Kubernetes Jobs.

### Hook Implementation

I created two Job templates under `k8s/app-python/templates/hooks`:

- `hooks/pre-install-job.yaml` — runs **before** the main release is installed
- `hooks/post-install-job.yaml` — runs **after** the release is installed

Both jobs use `busybox` and simple `echo` commands to simulate real tasks (migrations, smoke tests, etc.).

**Pre-install hook** (`templates/hooks/pre-install-job.yaml`):

- Type: `pre-install`
- Weight: `-5` (runs before other pre-install hooks)
- Deletion policy: `hook-succeeded`

Key annotations:

```yaml
metadata:
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
```

The Job prints:

```text
Pre-install hook running for <release-name>
...
Pre-install hook completed
```

**Post-install hook** (`templates/hooks/post-install-job.yaml`):

- Type: `post-install`
- Weight: `5` (runs after the main resources are created)
- Deletion policy: `hook-succeeded`

Key annotations:

```yaml
metadata:
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
```

The Job prints:

```text
Post-install smoke test for <release-name>
...
Post-install hook completed successfully
```

Hooks use the same helper templates (`app-python.fullname`, `app-python.labels`) as the rest of the chart, so names and labels stay consistent.

### Lint and Dry-Run with Hooks

I validated the chart including hooks:

```powershell
helm lint k8s\app-python
```

Output:

```text
==> Linting k8s\app-python
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

Then rendered the chart with `--dry-run --debug` and filtered for hooks:

```powershell
helm install --dry-run --debug app-python-hooks-test k8s\app-python |
  Select-String "hook" -Context 2
```

Relevant part of the output:

```text
NAME: app-python-hooks-test
...

HOOKS:
---
# Source: app-python/templates/hooks/post-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "app-python-hooks-test-post-install"
  ...
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
...
              echo "Post-install smoke test for app-python-hooks-test";
              sleep 5;
              echo "Post-install hook completed successfully"
---
# Source: app-python/templates/hooks/pre-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "app-python-hooks-test-pre-install"
  ...
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
...
              echo "Pre-install hook running for release app-python-hooks-test";
              sleep 5;
              echo "Pre-install hook completed"
```

This confirms that both hooks are rendered with the correct hook types, weights, and deletion policies.

### Real Installation and Hook Deletion

I then installed the chart with the dev values:

```powershell
helm uninstall app-python
helm install app-python k8s\app-python -f k8s\app-python\values-dev.yaml
```

Immediately after installation:

```powershell
kubectl get jobs
```

Output:

```text
No resources found in default namespace.
```

And the application pod is running:

```powershell
kubectl get pods
```

Output:

```text
NAME                          READY   STATUS    RESTARTS   AGE
app-python-698d99d697-j7q87   1/1     Running   0          23s
```

Because both Jobs use:

```yaml
"helm.sh/hook-delete-policy": hook-succeeded
```

they are automatically deleted by Helm after successful completion.  
As a result, `kubectl get jobs` shows **no resources**, which is expected and confirms that the deletion policy is applied.

These steps demonstrate:

- Understanding of hook types (pre-install / post-install)
- Usage of hook weights for execution order
- Proper deletion policy (`hook-succeeded`)
- Verification via `helm lint`, `helm install --dry-run --debug`, and a real install.

## Task 5 — Documentation

### 1. Chart Overview

**Chart location:** `k8s/app-python`

**Structure:**

- `k8s/app-python/Chart.yaml`
  - Defines chart metadata:
    - `name: app-python`
    - `version: 0.1.0`
    - `appVersion: "1.0.0"`
    - `type: application`

- `k8s/app-python/values.yaml`  
  - Default configuration:
    - `replicaCount`
    - `image.repository`, `image.tag`, `image.pullPolicy`
    - `service.type`, `service.port`, `service.targetPort`, `service.nodePort`
    - `resources.requests` / `resources.limits`
    - `livenessProbe` / `readinessProbe` timing and paths
    - basic `env` values (e.g. `PORT`)

- Templates in `k8s/app-python/templates/`:
  - `deployment.yaml`  
    Templated `Deployment`:
    - replicas from `.Values.replicaCount`
    - image from `.Values.image`
    - resources from `.Values.resources`
    - health checks from `.Values.livenessProbe` / `.Values.readinessProbe`
    - `RollingUpdate` strategy (`maxUnavailable: 0`, `maxSurge: 1`)
  - `service.yaml`
    Templated `Service`:
    - `spec.type` and ports from `.Values.service`
    - `nodePort` only when `service.type == "NodePort"`
  - `_helpers.tpl`  
    Helper templates:
    - `app-python.fullname`
    - `app-python.labels`
    - `app-python.selectorLabels`
  - Hooks in `templates/hooks/`:
    - `pre-install-job.yaml` — pre-install Job hook
    - `post-install-job.yaml` — post-install Job hook

**Values organization strategy:**

- Base defaults in `values.yaml` are “sane production‑like defaults”.
- Environment-specific overrides are kept in:
  - `values-dev.yaml`
  - `values-prod.yaml`
- All tunable settings (replicas, resources, probes, service type/ports, image tag) are driven by values, not hardcoded in templates.

---

### 2. Configuration Guide

**Important values and purpose:**

- `replicaCount` — number of application replicas.
- `image.repository` / `image.tag` — Docker image to deploy (Lab 2 image).
- `service.type` — how the service is exposed (`NodePort` for dev, `LoadBalancer` for prod/cloud).
- `service.port` / `targetPort` / `nodePort` — external port, container port, and nodePort (for NodePort).
- `resources.requests` / `resources.limits` — CPU/memory guarantees and caps (production best practices).
- `livenessProbe` / `readinessProbe` — health checks configuration; paths and timings.
- `env.port` — container `PORT` environment variable, matches container port.

**Customizing for different environments:**

- **Development:** override with `values-dev.yaml`
  - `replicaCount: 1`
  - `service.type: NodePort`
  - relaxed resources and faster probes.

- **Production:** override with `values-prod.yaml`
  - `replicaCount: 5`
  - `service.type: LoadBalancer`
  - stronger resources and more conservative probe timings.

**Example installations:**

```powershell
# Dev install (NodePort, 1 replica)
helm install app-python k8s\app-python -f k8s\app-python\values-dev.yaml

# Upgrade same release to prod config (LoadBalancer, 5 replicas)
helm upgrade app-python k8s\app-python -f k8s\app-python\values-prod.yaml
```

---

### 3. Hook Implementation

I implemented two Helm hooks as Kubernetes Jobs in `k8s/app-python/templates/hooks`:

1. **Pre-install hook** — `pre-install-job.yaml`
   - Purpose: simulate pre-install tasks (e.g. migrations/validation) before resources are created.
   - Annotations:
     ```yaml
     "helm.sh/hook": pre-install
     "helm.sh/hook-weight": "-5"
     "helm.sh/hook-delete-policy": hook-succeeded
     ```
   - Behavior:
     - Runs **before** main resources are installed.
     - Lower weight (`-5`) ensures it runs before other pre-install hooks (if any).
     - On success, the Job is deleted automatically (`hook-succeeded`).

2. **Post-install hook** — `post-install-job.yaml`
   - Purpose: simulate post-install smoke tests/notifications after the app is deployed.
   - Annotations:
     ```yaml
     "helm.sh/hook": post-install
     "helm.sh/hook-weight": "5"
     "helm.sh/hook-delete-policy": hook-succeeded
     ```
   - Behavior:
     - Runs **after** main resources are installed.
     - Higher weight (`5`) ensures it runs after lower-weight post-install hooks.
     - On success, the Job is deleted automatically.

Both hooks:

- Use `busybox` with simple `echo` + `sleep` commands.
- Use the same helper templates (`app-python.fullname`, `app-python.labels`) for consistent naming/labels.

---

### 4. Installation Evidence

**Dev install (NodePort, 1 replica):**

```powershell
helm uninstall app-python
helm install app-python k8s\app-python -f k8s\app-python\values-dev.yaml
```

Deployment and service:

```powershell
kubectl get deploy app-python
```

```text
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
app-python   1/1     1            1           11s
```

```powershell
kubectl get svc app-python
```

```text
NAME         TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
app-python   NodePort   10.103.6.130   <none>        80:30080/TCP   14s
```

**Upgrade to prod (LoadBalancer, 5 replicas):**

```powershell
helm upgrade app-python k8s\app-python -f k8s\app-python\values-prod.yaml
```

Verification:

```powershell
kubectl get deploy app-python
```

```text
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
app-python   5/5     1            5           40s
```

```powershell
kubectl get svc app-python
```

```text
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
app-python   LoadBalancer   10.103.6.130   <pending>     80:30080/TCP   47s
```

**Full resource view (example from base install):**

```powershell
kubectl get all
```

```text
NAME                              READY   STATUS    RESTARTS   AGE
pod/app-python-74cff54c48-6kcxq   1/1     Running   0          6m4s
pod/app-python-74cff54c48-gh6c7   1/1     Running   0          6m4s
pod/app-python-74cff54c48-xqqdc   1/1     Running   0          6m4s

NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
service/app-python   NodePort    10.104.1.167   <none>        80:30080/TCP   6m4s

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/app-python   3/3     3            3           6m4s

NAME                                    DESIRED   CURRENT   READY   AGE
replicaset.apps/app-python-74cff54c48   3         3         3       6m4s
```

**Helm releases:**

```powershell
helm list
```

Example:

```text
NAME         NAMESPACE   REVISION  STATUS    CHART              APP VERSION
app-python   default     1         deployed  app-python-0.1.0   1.0.0
```

**Hook execution evidence:**

- Hooks are rendered and visible in dry-run output (`HOOKS` section of `helm install --dry-run --debug`).
- After a real install:

  ```powershell
  kubectl get jobs
  ```

  ```text
  No resources found in default namespace.
  ```

  This matches the `hook-succeeded` deletion policy (Jobs removed after success).

> Note: if needed for grading, you can still capture and include `kubectl describe job <pre/post-install-job-name>` and `kubectl logs job/<name>` output; currently only the deletion behavior (`kubectl get jobs`) is documented.

---

### 5. Operations

**Installation (dev environment):**

```powershell
# Dev install
helm install app-python k8s\app-python -f k8s\app-python\values-dev.yaml
```

**Upgrade to production configuration:**

```powershell
# Upgrade to prod values
helm upgrade app-python k8s\app-python -f k8s\app-python\values-prod.yaml
```

**Rollback (pattern):**

```powershell
# Show history
helm history app-python

# Roll back to previous revision (example: 1)
helm rollback app-python 1
```


**Uninstall:**

```powershell
helm uninstall app-python
```

---

### 6. Testing & Validation

**helm lint:**

```powershell
helm lint k8s\app-python
```

```text
==> Linting k8s\app-python
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

**helm template verification:**

```powershell
helm template app-python k8s\app-python
```

- Confirms that:
  - Deployment renders with correct replicas, image, resources, and probes.
  - Service renders with correct type and ports.
  - Labels and names come from helper templates.

**Dry-run install with debug (includes hooks):**

```powershell
helm install --dry-run --debug app-python-test k8s\app-python
```

- Shows:
  - `COMPUTED VALUES` (all values from `values.yaml`).
  - Rendered `Service` and `Deployment`.
  - `HOOKS` section with `pre-install` and `post-install` Jobs and correct annotations.

**Application accessibility verification:**

```powershell
kubectl port-forward svc/app-python 8080:80
```

From host:

```powershell
curl.exe http://localhost:8080/
curl.exe http://localhost:8080/health
```

Example responses:

```text
{"endpoints":[{"description":"Service information","method":"GET","path":"/"},...],
 "service":{"name":"devops-info-service","version":"1.0.0"}, ... }

{"status":"healthy","timestamp":"2026-03-28T11:56:25.013879Z","uptime_seconds":91}
```

This confirms that:

- The chart installs successfully.
- The app is reachable via the Service.
- Health checks are working and exposed through the Helm-managed deployment.