# Lab 13 — GitOps with ArgoCD

## Task 1 — ArgoCD Installation & Setup

### 1.1 ArgoCD Setup

#### Installation Steps

```powershell
# Step 1: Add Helm repository
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> helm repo add argo https://argoproj.github.io/argo-helm
"argo" has been added to your repositories

PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "hashicorp" chart repository
...Successfully got an update from the "prometheus-community" chart repository
...Successfully got an update from the "argo" chart repository
Update Complete. ⎈Happy Helming!⎈

# Step 2: Create dedicated namespace
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl create namespace argocd
namespace/argocd created

# Step 3: Install ArgoCD
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> helm install argocd argo/argo-cd --namespace argocd
NAME: argocd
LAST DEPLOYED: Sun Apr 19 11:47:00 2026
NAMESPACE: argocd
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
```

#### Verification

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get pods -n argocd
NAME                                                READY   STATUS    RESTARTS   AGE
argocd-application-controller-0                     1/1     Running   0          113s
argocd-applicationset-controller-764f6cb5b6-fgqp4   1/1     Running   0          113s
argocd-dex-server-75584bc88d-gjg8w                  1/1     Running   0          113s
argocd-notifications-controller-5c7987d768-ktw88    1/1     Running   0          113s
argocd-redis-545df96696-qbm2m                       1/1     Running   0          113s
argocd-repo-server-9db6859b8-lxlqs                  1/1     Running   0          113s
argocd-server-ff9c49d6b-6fpxw                       1/1     Running   0          113s
```

**All components running successfully ✅**

---

### 1.2 Access ArgoCD UI

#### UI Access Method

**Step 1: Port Forwarding (keep in separate terminal)**

```powershell
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl port-forward svc/argocd-server -n argocd 8080:443
Forwarding from 127.0.0.1:8080 -> 8080
Forwarding from [::1]:8080 -> 8080
Handling connection for 8080
```

**Step 2: Retrieve Admin Password**

```powershell
Polina@MagicBookX16 MINGW64 /d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course (lab13)
$ kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
xQI7Sl56Zd9BiS53
```

**Step 3: Access Web Interface**

- **URL:** https://localhost:8080
- **Username:** admin
- **Password:** xQI7Sl56Zd9BiS53
![](../app_python/docs/screenshots/09-CLI.jpg)

#### UI Features Explored

- Application list (currently empty, will deploy in Task 2)
- Application details and status
- Sync status and health indicators
- Settings and user management
- Notifications and logs

---

### 1.3 Install ArgoCD CLI

#### Installation

```powershell
# Download latest ArgoCD CLI for Windows
$ProgressPreference = 'SilentlyContinue'
$url = "https://github.com/argoproj/argo-cd/releases/latest/download/argocd-windows-amd64.exe"
$output = "$env:TEMP\argocd.exe"
Invoke-WebRequest -Uri $url -OutFile $output

# Copy to System32 (adds to PATH)
Copy-Item -Path $output -Destination "C:\Windows\System32\argocd.exe" -Force

# Verify installation
argocd version
```

#### Version Check

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> argocd version
argocd: v3.3.7+035e855
  BuildDate: 2026-04-16T15:58:07Z
  GitCommit: 035e8556c451196e203078160a5c01f43afdb92f
  GitTreeState: clean
  GoVersion: go1.25.5
  Compiler: gc
  Platform: windows/amd64
{"level":"fatal","msg":"Argo CD server address unspecified","time":"2026-04-19T11:57:48+03:00"}
```

#### CLI Login

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> argocd login localhost:8080 --insecure --usd "xQI7Sl56Zd9BiS53"
'admin:login' logged in successfully
Context 'localhost:8080' updated
```

#### Connection Verification

```powershell
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> argocd account list
NAME   ENABLED  CAPABILITIES
admin  true     login
PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course>
```

**Connection verified ✅**

---


