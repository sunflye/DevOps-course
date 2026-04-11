# Lab 11 — Kubernetes Secrets & HashiCorp Vault

## Kubernetes Secrets

### Create Secret (imperative)

```powershell
kubectl create secret generic app-credentials `
  --from-literal=username=admin `
  --from-literal=password=SuperSecret123
```

**Output:**
```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl create secret generic app-credentials `
>>   --from-literal=username=admin `
>>   --from-literal=password=SuperSecret123
secret/app-credentials created
```

### View Secret (YAML)

```powershell
kubectl get secret app-credentials -o yaml
```

**Output:**
```
secret/app-credentials created
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get secret app-credentials -o
 yaml
apiVersion: v1
data:
  password: U3VwZXJTZWNyZXQxMjM=
  username: YWRtaW4=
kind: Secret
metadata:
  creationTimestamp: "2026-04-04T17:50:23Z"
  name: app-credentials
  namespace: default
  resourceVersion: "17575"
  uid: fb588936-3c48-480d-811b-ceeeda1f30cd
type: Opaque
```

### Decode base64 values (PowerShell)

```powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("YWRtaW4="))
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("U3VwZXJTZWNyZXQxMjM="))
```

**Output:**
```
admin
SuperSecret123
```

### Encoding vs Encryption

- **Base64** = encoding (reversible without a key).  
- **Encryption** requires a key to decrypt the data.

### Security implications

- Kubernetes Secrets are **not encrypted at rest by default** (only base64).
- **etcd encryption** protects secrets stored in etcd and should be enabled in production.


---

## Helm Secret Integration

### Chart structure (includes `secrets.yaml`)

```
k8s/app-python/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── service.yaml
    ├── secrets.yaml
    └── NOTES.txt
```

### Secret template output

```powershell
kubectl get secret app-python-secret -o yaml
```

```text
apiVersion: v1
data:
  password: cGxhY2Vob2xkZXItcGFzcw==
  username: cGxhY2Vob2xkZXItdXNlcg==
kind: Secret
metadata:
  annotations:
    meta.helm.sh/release-name: app-python
    meta.helm.sh/release-namespace: default
  creationTimestamp: "2026-04-04T18:04:33Z"
  labels:
    app.kubernetes.io/instance: app-python
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: app-python
    app.kubernetes.io/version: 1.0.0
    helm.sh/chart: app-python-0.1.0
  name: app-python-secret
  namespace: default
  resourceVersion: "18254"
  uid: 477e0d1a-b1ee-429c-b915-8f9449ad5779
type: Opaque
```

### How secrets are consumed in Deployment

```yaml
envFrom:
  - secretRef:
      name: {{ include "app-python.fullname" . }}-secret
```

### Verification (env vars in pod)

```powershell
kubectl exec -it app-python-6f8ddbc699-q6sql -- printenv | Select-String "username|password"
```

```text
username=placeholder-user
password=placeholder-pass
```

**Secrets not visible in `describe`:**

```powershell
kubectl describe pod app-python-6f8ddbc699-q6sql | Select-String -Pattern "username|password"
```

```text
# (no output)
```

---

## Resource Management

### Resource limits from values

```powershell
helm template app-python k8s\app-python | Select-String -Context 3 "resources:"
```

```text
            envFrom:
              - secretRef:
                  name: app-python-secret
>           resources:
              limits:
                cpu: 200m
                memory: 256Mi
```

```powershell
kubectl get deploy app-python -o yaml | Select-String -Context 6 "resources:"
```

```text
>         resources:
            limits:
              cpu: 100m
              memory: 128Mi
            requests:
              cpu: 50m
              memory: 64Mi
```

```powershell
kubectl describe pod app-python-698d99d697-j7q87 | Select-String -Context 6 "Limits:"
```

```text
>     Limits:
        cpu:     100m
        memory:  128Mi
      Requests:
        cpu:      50m
        memory:   64Mi
```

### Requests vs Limits

- **Requests** = guaranteed resources.
- **Limits** = maximum allowed usage.

### How to choose values

- Start with low requests (based on real usage).
- Set limits to prevent noisy-neighbor issues.
- Tune after observing actual metrics.

---

## Vault Integration

### Vault installation verification

```powershell
kubectl get pods
```

**Output:**  
```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl get pods                                
NAME                                    READY   STATUS    RESTARTS   AGE
app-python-9f578645d-xvmn4              2/2     Running   0          10m
vault-0                                 1/1     Running   0          47m
vault-agent-injector-86d76999fd-s7psw   1/1     Running   0          47m
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> 
```

### Policy and role configuration (sanitized)

- **Policy name:** `app-python`  
- **Role:** `auth/kubernetes/role/app-python`  
- **Service account:** `default`

**Output:**  
```
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec -it vault-0 -- /bin/sh -c "export VAULT_TOKEN=root; vault policy read app-python"
path "secret/data/app-python/*" {
  capabilities = ["read"]
}
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> kubectl exec -it vault-0 -- /bin/sh -c "export VAULT_TOKEN=root; vault read auth/kubernetes/role/app-python"
Key                                         Value
---                                         -----
alias_name_source                           serviceaccount_uid
bound_service_account_names                 [default]
bound_service_account_namespace_selector    n/a
bound_service_account_namespaces            [default]
policies                                    [app-python]
token_bound_cidrs                           []
token_explicit_max_ttl                      0s
token_max_ttl                               0s
token_no_default_policy                     false
token_num_uses                              0
token_period                                0s
token_policies                              [app-python]
token_ttl                                   1h
token_type                                  default
ttl                                         1h
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course> 
```

### Proof of secret injection (file exists + content)

```powershell
kubectl exec -it app-python-9f578645d-xvmn4 -c app-python -- ls -la /vault/secrets/
```

```text
total 8
drwxrwxrwt 2 root root      60 Apr  4 18:53 .
drwxr-xr-x 3 root root    4096 Apr  4 18:53 ..
-rw-r--r-- 1  100 appuser  173 Apr  4 18:53 config
```

```powershell
kubectl exec -it app-python-9f578645d-xvmn4 -c app-python -- cat /vault/secrets/config
```

```text
data: map[password:vault-pass username:vault-user]
metadata: map[created_time:2026-04-04T18:19:33.744296466Z custom_metadata:<nil> deletion_time: destroyed:false version:1]
```

### Sidecar injection pattern (summary)

Vault Agent runs as a sidecar container, authenticates using the pod’s ServiceAccount, fetches secrets from Vault, and writes them into a shared volume at `/vault/secrets/`. The application container reads secrets from files instead of environment variables.

---

## Security Analysis

### K8s Secrets vs Vault

| Feature | K8s Secrets | Vault |
|--------|-------------|-------|
| Encryption at rest | Optional | ✅ Built‑in |
| Rotation | Manual | ✅ Automated |
| Audit | Limited | ✅ Full audit |
| Dynamic secrets | ❌ No | ✅ Yes |
| Multi‑platform | ❌ K8s only | ✅ Yes |

### When to use each

- **K8s Secrets:** small apps, internal environments, low complexity.  
- **Vault:** production, compliance, multi‑env, rotation/audit needed.

### Production recommendations

- Enable **etcd encryption at rest**.
- Use **RBAC least privilege**.
- Use **Vault** for sensitive/rotating credentials.
- Never commit real secrets to Git.