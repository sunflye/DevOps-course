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
