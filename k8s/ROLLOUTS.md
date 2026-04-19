# Lab 14 — Progressive Delivery with Argo Rollouts

## Task 1 — Argo Rollouts Fundamentals

### 1) Install Argo Rollouts Controller

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl create namespace argo-rollouts
namespace/argo-rollouts created

PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
customresourcedefinition.apiextensions.k8s.io/analysisruns.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/analysistemplates.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/clusteranalysistemplates.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/experiments.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/rollouts.argoproj.io created
serviceaccount/argo-rollouts created
clusterrole.rbac.authorization.k8s.io/argo-rollouts created
clusterrole.rbac.authorization.k8s.io/argo-rollouts-aggregate-to-admin created
clusterrole.rbac.authorization.k8s.io/argo-rollouts-aggregate-to-edit created
clusterrole.rbac.authorization.k8s.io/argo-rollouts-aggregate-to-view created
clusterrolebinding.rbac.authorization.k8s.io/argo-rollouts created
configmap/argo-rollouts-config created
secret/argo-rollouts-notification-secret created
service/argo-rollouts-metrics created
deployment.apps/argo-rollouts created

PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get pods -n argo-rollouts
NAME                            READY   STATUS    RESTARTS   AGE
argo-rollouts-f995555d9-257cj   1/1     Running   0          44s
```

### 2) Install kubectl Plugin

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl argo rollouts version
kubectl-argo-rollouts: v1.9.0+838d4e7
  BuildDate: 2026-03-20T21:15:27Z
  GitCommit: 838d4e792be666ec11bd0c80331e0c5511b5010e
  GitTreeState: clean
  GoVersion: go1.24.13
  Compiler: gc
  Platform: windows/amd64
```

### 3) Install Argo Rollouts Dashboard

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/dashboard-install.yaml
serviceaccount/argo-rollouts-dashboard created
clusterrole.rbac.authorization.k8s.io/argo-rollouts-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/argo-rollouts-dashboard created
service/argo-rollouts-dashboard created
deployment.apps/argo-rollouts-dashboard created

PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get pods -n argo-rollouts 
NAME                                       READY   STATUS    RESTARTS   AGE
argo-rollouts-dashboard-76bcf57589-j9v4g   1/1     Running   0          47s
argo-rollouts-f995555d9-257cj              1/1     Running   0          14m
```

**Dashboard access:**
```powershell
kubectl port-forward svc/argo-rollouts-dashboard -n argo-rollouts 3100:3100
# Open http://localhost:3100
```

### 4) Rollout vs Deployment (Key Differences)

**Rollout CRD (argoproj.io/v1alpha1)** - Additional fields for progressive delivery:

- `spec.strategy.canary` - Canary deployment with traffic shifting
  - `steps[].setWeight` - Define traffic percentage per step
  - `steps[].pause` - Manual or automatic pause between steps
  - `trafficRouting` - Integration with Istio, NGINX, SMI

- `spec.strategy.blueGreen` - Blue-Green deployment
  - `activeService` - Current active service
  - `previewService` - Preview service for testing
  - `autoPromotionEnabled` - Automatic promotion after verification
  - `scaleDownDelaySeconds` - Delay before scaling down old version

- `spec.analysis` - Metrics-based automated rollback
  - `templates[]` - Analysis templates reference
  - `metrics[]` - Custom metrics for success/failure conditions
  - `successfulRunHistoryLimit` / `failureRunHistoryLimit`

- `spec.progressDeadlineSeconds` - Extended deadline that respects pause durations

**Deployment (apps/v1)** - Standard fields only:

- `spec.strategy.rollingUpdate.maxSurge` - Maximum extra pods during update
- `spec.strategy.rollingUpdate.maxUnavailable` - Maximum unavailable pods during update
- No traffic management capabilities
- No automated rollback based on metrics
- No canary or blue-green strategies

**Key Differences Summary:**

| Feature | Rollout | Deployment |
|---------|---------|------------|
| Canary strategy | ✅ Yes | ❌ No |
| Blue-Green strategy | ✅ Yes | ❌ No |
| Traffic shifting (weight-based) | ✅ Yes | ❌ No |
| Automated rollback | ✅ Yes (metrics-based) | ❌ No (manual only) |
| Pause between updates | ✅ Yes | ❌ No |
| Service mesh integration | ✅ Yes (Istio/NGINX) | ❌ No |
| Analysis/verification steps | ✅ Yes | ❌ No |
---

## Task 2 — Canary Deployment

### 1. Strategy Configuration

I converted the standard Kubernetes `Deployment` into an Argo `Rollout` in [`k8s/app-python/templates/rollout.yaml`](k8s/app-python/templates/rollout.yaml). The canary strategy is configured with the following progressive traffic shifting steps:

```yaml
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: {}           # Manual promotion required here
        - setWeight: 40
        - pause: { duration: 30s }
        - setWeight: 60
        - pause: { duration: 30s }
        - setWeight: 80
        - pause: { duration: 30s }
        - setWeight: 100
```

- **Objective:** Minimize risk by exposing the new version to only 20% of users initially.
- **Manual Gate:** The first step requires a manual `promote` command to proceed, allowing for human verification.
- **Automatic Progression:** Subsequent steps (40% to 100%) happen automatically with 30-second pauses to monitor stability.

---

### 2. Step-by-Step Rollout Progression

I triggered the rollout by updating the image tag in `values.yaml` from `latest` to `2026.04.19`.

#### Step 1: Initial Canary (20% Traffic)
Argo Rollouts created a new ReplicaSet and scaled it to 20% of the desired replicas (1 pod out of 5). The rollout then entered a `Paused` state.

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl argo rollouts get rollout app-python-canary -n default
Name:            app-python-canary
Status:          ॥ Paused
Message:         CanaryPauseStep
Strategy:        Canary
  Step:          1/9
  SetWeight:     20
  ActualWeight:  20

NAME                                           KIND        STATUS        AGE    INFO
⟳ app-python-canary                            Rollout     ॥ Paused      33m    
├──# revision:5
│  └──⧉ app-python-canary-7b6b84dd67           ReplicaSet  ✔ Healthy     32s    canary
│     └──□ app-python-canary-7b6b84dd67-7m5lz  Pod         ✔ Running     32s    ready:1/1
└──# revision:1
   └──⧉ app-python-canary-6759b96fc7           ReplicaSet  ✔ Healthy     33m    stable
```
![](../app_python/docs/screenshots/20.jpg)
#### Step 2: Manual Promotion
I manually promoted the rollout to proceed past the first step:
```powershell
kubectl argo rollouts promote app-python-canary -n default
```

#### Step 3: Automatic Progression to 100%
The controller automatically shifted traffic through 40%, 60%, and 80% steps, waiting 30 seconds at each stage, until reaching the final state.

![](../app_python/docs/screenshots/21.jpg)
**Final Successful State:**
```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl argo rollouts get rollout app-python-canary -n default
Status:          ✔ Healthy
Strategy:        Canary
  Step:          9/9
  SetWeight:     100
  ActualWeight:  100
Images:          sunflye/devops-info-service:2026.04.19 (stable)

NAME                                           KIND        STATUS         AGE   INFO
⟳ app-python-canary                            Rollout     ✔ Healthy      47m   
├──# revision:5
│  └──⧉ app-python-canary-7b6b84dd67           ReplicaSet  ✔ Healthy      13m   stable
│     ├──□ app-python-canary-7b6b84dd67-7m5lz  Pod         ✔ Running      13m   ready:1/1
│     ├──□ app-python-canary-7b6b84dd67-7fqfw  Pod         ✔ Running      2m1s  ready:1/1
│     ├──□ app-python-canary-7b6b84dd67-xnvdz  Pod         ✔ Running      84s   ready:1/1
│     ├──□ app-python-canary-7b6b84dd67-4zgtk  Pod         ✔ Running      48s   ready:1/1
│     └──□ app-python-canary-7b6b84dd67-7b7h6  Pod         ✔ Running      12s   ready:1/1
```

![](../app_python/docs/screenshots/22.jpg)
---

### 3. Abort & Rollback Demonstration

During one of the deployment attempts (Revision 6), I demonstrated the ability to instantly abort the rollout and return to the stable version.

**Abort Command:**
```powershell
kubectl argo rollouts abort app-python-canary -n default
```

**Result:** Argo Rollouts immediately scaled down the faulty canary ReplicaSet (Revision 6) and restored 100% of the traffic to the previous `stable` revision (Revision 5).

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl argo rollouts get rollout app-python-canary -n default
Name:            app-python-canary
Status:          ✖ Degraded
Message:         RolloutAborted: Rollout aborted update to revision 6
Strategy:        Canary
  Step:          0/9
  SetWeight:     0
  ActualWeight:  0
Images:          sunflye/devops-info-service:2026.04.19 (stable)

NAME                                           KIND        STATUS        AGE    INFO
⟳ app-python-canary                            Rollout     ✖ Degraded    54m        
├──# revision:6
│  └──⧉ app-python-canary-788fd4bb64           ReplicaSet  • ScaledDown  4m2s   canary
└──# revision:5
   └──⧉ app-python-canary-7b6b84dd67           ReplicaSet  ✔ Healthy     20m    stable
      ├──□ app-python-canary-7b6b84dd67-7m5lz  Pod         ✔ Running     20m    ready:1/1
      ├──□ app-python-canary-7b6b84dd67-7fqfw  Pod         ✔ Running     9m9s   ready:1/1
      ├──□ app-python-canary-7b6b84dd67-xnvdz  Pod         ✔ Running     8m32s  ready:1/1
      ├──□ app-python-canary-7b6b84dd67-s448m  Pod         ✔ Running     2m54s  ready:1/1
      └──□ app-python-canary-7b6b84dd67-zfcz6  Pod         ✔ Running     2m54s  ready:1/1
```

The status `Degraded` with the message `RolloutAborted` confirms that the controller stopped the progression and ensured that the stable production environment (Revision 5) remained available with 100% traffic weight.
![](../app_python/docs/screenshots/23.png)