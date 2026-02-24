# Lab 5 — Ansible Fundamentals
## 1. Architecture Overview

### Ansible Version
```bash
ansible [core 2.16.3]
config file = /workspace/ansible.cfg
python version = 3.12.3
```

### Target VM Information
**OS:** Ubuntu 24.04.3 LTS  
**Kernel:** Linux 6.14.0-1018-aws x86_64  
**Python:** 3.12.3 (pre-installed)  
**Provider:** AWS EC2  
**Instance Type:** t2.micro (Free Tier)  
**Public IP:** 34.229.125.207  
**SSH User:** ubuntu  

### Ansible Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│ Local Machine (Ansible Control Node)               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ansible/                                            │
│  ├── inventory/hosts.ini  → aws-vm (34.229.125.207)│
│  ├── ansible.cfg          → Configuration           │
│  ├── playbooks/                                      │
│  │   ├── provision.yml → common + docker roles     │
│  │   └── deploy.yml    → app_deploy role           │
│  │                                                   │
│  └── roles/                                          │
│      ├── common/        → Update apt, install pkgs │
│      ├── docker/        → Install & configure      │
│      └── app_deploy/    → Pull image, run container│
│                                                      │
└────────────┬────────────────────────────────────────┘
             │ SSH + Ansible
             ↓
┌─────────────────────────────────────────────────────┐
│ AWS EC2 Ubuntu 24.04 (34.229.125.207)             │
├─────────────────────────────────────────────────────┤
│ Common packages installed (curl, git, vim, etc) │
│ Docker installed and running                    │
│ python3-docker installed                        │
│ devops-app container running on port 5000      │
│ Health endpoint responding                      │
└─────────────────────────────────────────────────────┘
```

### Why Roles Instead of Monolithic Playbooks?

**Benefits of Role-Based Architecture:**

1. **Reusability** - Same role can be used across multiple playbooks and projects
   - Example: `docker` role can provision any server needing Docker
   - No code duplication across different playbooks

2. **Maintainability** - Changes in one place affect all uses
   - Update Docker installation in one role file
   - All playbooks using that role automatically get the update

3. **Organization** - Clear structure, easy to navigate and understand
   - Each role has single responsibility (common, docker, app_deploy)
   - Easier for new team members to find relevant code

4. **Testing** - Can test roles independently
   - Test `docker` role in isolation before using in playbooks
   - Verify role functionality before deployment

5. **Sharing** - Can publish to Ansible Galaxy for community use
   - Professional standard for Ansible code organization
   - Industry best practice
---

## 2. Roles Documentation

### 2.1 Common Role

**Purpose:** 
Basic system setup that every server needs - updates package manager, installs essential tools, and configures system settings like timezone.

**Key Variables (`roles/common/defaults/main.yml`):**
```yaml
common_packages:
  - python3-pip
  - curl
  - git
  - vim
  - htop
  - wget
  - ca-certificates
  - apt-transport-https
  - gnupg
  - lsb-release
```

**Handlers:** 
None (no services to restart)

**Dependencies:** 
None

---

### 2.2 Docker Role

**Purpose:** 
Install Docker engine and configure it for containerized applications. Ensures Docker daemon is running, users have permissions, and Python Docker modules are available for Ansible automation.

**Key Variables (`roles/docker/defaults/main.yml`):**
```yaml
docker_version: "24.0"
docker_users:
  - ubuntu
```

**Handlers (`roles/docker/handlers/main.yml`):**
```yaml
- name: restart docker
  service:
    name: docker
    state: restarted
    enabled: yes
```

**Dependencies:** 
None (but typically runs after `common` role for proper ordering)

---

### 2.3 App_Deploy Role

**Purpose:** 
Securely deploy containerized Python application using Docker Hub. Pulls images using encrypted credentials from Ansible Vault, manages container lifecycle, and verifies application health.

**Key Variables (`roles/app_deploy/defaults/main.yml`):**
```yaml
app_name: devops-app
docker_image: devops-info-service
docker_image_tag: latest
app_port: 5000
app_internal_port: 5000
app_container_name: "{{ app_name }}"
restart_policy: unless-stopped
```

**Encrypted Variables (`group_vars/all.yml` via Vault):**
```yaml
dockerhub_username: sunflye
dockerhub_password: <Token>
```

**Handlers (`roles/app_deploy/handlers/main.yml`):**
```yaml
- name: restart app
  community.docker.docker_container:
    name: "{{ app_container_name }}"
    image: "{{ docker_image }}:{{ docker_image_tag }}"
    state: started
    ports:
      - "{{ app_port }}:{{ app_internal_port }}"
    restart_policy: "{{ restart_policy }}"
    env:
      PORT: "{{ app_internal_port | string }}"
      HOST: "0.0.0.0"
    force_kill: yes
```

**Dependencies:** 

Implicitly depends on Docker role (Docker must be installed before deploying containers)

---

### 2.3 App_Deploy Role

**Purpose:** Securely deploy Python application using Docker with Vault credentials.

**Location:** `roles/app_deploy/`

**Tasks Performed:**
1. Login to Docker Hub using encrypted credentials (no_log for security)
2. Pull Docker image from registry
3. Stop existing container (if running, ignore if not exists)
4. Remove old container (if exists, ignore if not)
5. Run new container with:
   - Port mapping (5000:5000)
   - Environment variables (PORT, HOST)
   - Restart policy (unless-stopped)
   - Container name
6. Wait for port 5000 to be available (up to 30 seconds)
7. Verify health endpoint responds with 200 (retry up to 5 times)
8. Display health check result


**Key Variables (`roles/app_deploy/defaults/main.yml`):**
```yaml
app_name: devops-app
docker_image: devops-info-service
docker_image_tag: latest
app_port: 5000
app_internal_port: 5000
app_container_name: "{{ app_name }}"
restart_policy: unless-stopped
```

**Encrypted Variables (`group_vars/all.yml` - encrypted with Vault):**
```yaml
dockerhub_username: sunflye
dockerhub_password: <Token>
```

**Handlers (`roles/app_deploy/handlers/main.yml`):**
```yaml
- name: restart app
  community.docker.docker_container:
    name: "{{ app_container_name }}"
    image: "{{ docker_image }}:{{ docker_image_tag }}"
    state: started
    ports:
      - "{{ app_port }}:{{ app_internal_port }}"
    restart_policy: "{{ restart_policy }}"
    env:
      PORT: "{{ app_internal_port | string }}"
      HOST: "0.0.0.0"
    force_kill: yes
```

**Dependencies:** Implicitly depends on Docker being installed (though not formally declared)

---

## 3. Idempotency Demonstration

### 3.1 First Provision Run (with changes)

```
root@1fde1d5f6de8:/workspace# ansible-playbook playbooks/provision.yml

PLAY [Provision web servers] **********************************************************

TASK [Gathering Facts] ****************************************************************
ok: [aws-vm]

TASK [common : Update apt cache] ******************************************************
changed: [aws-vm]

TASK [common : Install common packages] ***********************************************
changed: [aws-vm]

TASK [common : Set timezone to UTC] ***************************************************
changed: [aws-vm]

TASK [docker : Install Docker prerequisites] ******************************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] ****************************************************
changed: [aws-vm]

TASK [docker : Add Docker repository] *************************************************
changed: [aws-vm]

TASK [docker : Install Docker packages] ***********************************************
changed: [aws-vm]

TASK [docker : Enable Docker service] *************************************************
ok: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ***************************************
changed: [aws-vm]

TASK [docker : Install python3-docker via apt (Ubuntu 24.04 fix)] *********************
changed: [aws-vm]

PLAY RECAP ****************************************************************************
aws-vm : ok=11 changed=9 unreachable=0 failed=0
```

**Summary:** 
- **ok=11** - Tasks that ran, no change needed
- **changed=9** - Tasks that made changes to reach desired state
- **Total changed:** 9/11 tasks made changes

### 3.2 Second Provision Run (idempotency verification)

```
root@1fde1d5f6de8:/workspace# ansible-playbook playbooks/provision.yml

PLAY [Provision web servers] **********************************************************

TASK [Gathering Facts] ****************************************************************
ok: [aws-vm]

TASK [common : Update apt cache] ******************************************************
ok: [aws-vm]

TASK [common : Install common packages] ***********************************************
ok: [aws-vm]

TASK [common : Set timezone to UTC] ***************************************************
ok: [aws-vm]

TASK [docker : Install Docker prerequisites] ******************************************
ok: [aws-vm]

TASK [docker : Add Docker GPG key] ****************************************************
ok: [aws-vm]

TASK [docker : Add Docker repository] *************************************************
ok: [aws-vm]

TASK [docker : Install Docker packages] ***********************************************
ok: [aws-vm]

TASK [docker : Enable Docker service] *************************************************
ok: [aws-vm]

TASK [docker : Add ubuntu user to docker group] ***************************************
ok: [aws-vm]

TASK [docker : Install python3-docker via apt (Ubuntu 24.04 fix)] *********************
ok: [aws-vm]

PLAY RECAP ****************************************************************************
aws-vm : ok=11 changed=0 unreachable=0 failed=0
```

**Summary:**
- **ok=11** - All tasks ran, no changes needed
- **changed=0** - **CRITICAL: No tasks made changes!**
- **Result: IDEMPOTENT** 

### 3.3 Analysis: What Changed First Run?

**Tasks that changed (9 total):**

1. **Update apt cache** - Package list was outdated, needed refresh
2. **Install common packages** - Packages not installed yet
3. **Set timezone to UTC** - System was not in UTC (was local time)
4. **Add Docker GPG key** - Key not in trusted keyring yet
5. **Add Docker repository** - Repository not configured yet
6. **Install Docker packages** - Docker binaries not installed
7. **Add ubuntu user to docker group** - User not in group yet
8. **Install python3-docker via apt** - Package not installed yet

**Tasks that didn't change (2 total):**

1. **Gathering Facts** - Fact gathering (always ok)
2. **Install Docker prerequisites** - Dependencies already satisfied from apt update

### 3.4 Why Nothing Changed Second Run?

**Idempotency Explanation:**

All tasks use **state-based modules** that check current state before making changes:

```yaml
# Example from common role:
- name: Install common packages
  apt:
    name: "{{ common_packages }}"
    state: present  # ← Only installs if not present
```

**How it works:**

1. **First run:** Package not installed → Install it → changed 
2. **Second run:** Package already installed → Skip installation → ok (no change) 

**Key Idempotency Patterns Used:**

| Module | Idempotent Parameter | Behavior |
|--------|---------------------|----------|
| `apt` | `state: present` | Only installs if not already installed |
| `service` | `state: started` | Only starts if not already running |
| `timezone` | Compare with current | Only changes if different |
| `user` | `append: yes` | Only adds group if not already member |
| `apt_key` | `state: present` | Only adds if not already trusted |
| `apt_repository` | `state: present` | Only adds if not already in sources |

**Why This Matters:**

- Safe to re-run playbooks without side effects
- Can recover from partial failures
- Detects configuration drift
- Convergence to desired state
- No accidental double installations

---

## 4. Ansible Vault Usage

### 4.1 Secure Credential Storage

**Problem:** Cannot commit Docker Hub password to Git unencrypted.

**Solution:** Ansible Vault encrypts sensitive data.

**Implementation:**

```bash
# Create encrypted file
ansible-vault create group_vars/all.yml

# Enter password when prompted
dockerhub_username: sunflye
dockerhub_password: <Token>
app_name: devops-app
docker_image: sunflye/devops-info-service
docker_image_tag: latest
app_port: 5000
app_container_name: devops-app
app_internal_port: 5000
```

### 4.2 Vault File Encrypted
```
$ANSIBLE_VAULT;1.1;AES256
64626236626237363934303230333132306563653264633033616363386164313831313235383565
3430323936633631343636353963346563383538663730630a333961373337373436363262616635
36393432343435343833666537373139663139313038346663653737613737653961613363353131
6664323739633332300a626437303134353231343735626261353461666538653033323737393564
63643838393539396437383363666162653732303836616333346231323465633634303633333837
37343637316464663731646536323233323834333733343366303233346565363362326430326165
66326431646637316463653662636566346633333231666438336432303332633939323033656361
35383466373366323863623830383236306331646439623961313035616530646237393732303233
66333433333732396238323739643162396563373831636466383938613061383832363561613763
39633463623739373366626362346633306261623764333337346361366165633630613536636537
36663231326462613438653138316536653730333436663936326632383265336638646263303835
33393737366533666236323239616636366663643533373634613330373632393634323737393331
32313464376637333366666534363439313163323932313436646263666364363539333737316634
63653939353361383733303733383433393966646139643836333834613764323861353431346164
35626535616539323063333933383766363732633765306366333434343131303635306334353930
35303661313864346338373138643932346438313662333462613235303662363238373663626233
37396632613462623765636133356231386533376339386231383739383235323232643531613438
6333386430316132383233663961333266346130633339396432
```

### 4.3 Vault Password Management Strategy

**Method Used:** `--ask-vault-pass` (prompt for password at runtime)

**Advantages:**
- Password not stored in files
- Safe for CI/CD (can be passed via environment)
- No `.vault_pass` file to accidentally commit

**Usage:**
```bash
ansible-playbook playbooks/deploy.yml --ask-vault-pass
```


### 4.4 Why Ansible Vault is Important

1. **Security** - Encrypts credentials, not readable in plaintext
2. **Collaboration** - Can commit encrypted file to Git safely
3. **Audit Trail** - Can track when secrets were last used
4. **Rotation** - Easy to rotate passwords (re-encrypt file)
5. **Compliance** - Meets security requirements for credential management
6. **Best Practice** - Industry standard for secret management in Ansible

---

## 5. Deployment Verification

### 5.1 Deployment Run

Firstly, I had some errors during these stages, but then I fixed them, so this is the output of the third deployment run when it finally worked
```
root@1fde1d5f6de8:/workspace# ansible-playbook playbooks/deploy.yml --ask-vault-pass
Vault password: 

PLAY [Deploy application] *************************************************************

TASK [Gathering Facts] ****************************************************************
ok: [aws-vm]

TASK [app_deploy : Login to Docker Hub] ***********************************************
ok: [aws-vm]

TASK [app_deploy : Pull Docker image] *************************************************
ok: [aws-vm]

TASK [app_deploy : Stop existing container (if running)] ******************************
changed: [aws-vm]

TASK [app_deploy : Remove old container (if exists)] **********************************
changed: [aws-vm]

TASK [app_deploy : Run application container] *****************************************
changed: [aws-vm]

TASK [app_deploy : Wait for application to be ready] **********************************
ok: [aws-vm]

TASK [app_deploy : Verify health endpoint] ********************************************
ok: [aws-vm]

TASK [app_deploy : Display health check result] ***************************************
ok: [aws-vm] => {
    "msg": "✅ Application is healthy: healthy"
}

RUNNING HANDLER [app_deploy : restart app] ********************************************
ok: [aws-vm]

PLAY RECAP ****************************************************************************
aws-vm                     : ok=10   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

```

**Summary:**
- All 10 tasks completed successfully
- 3 tasks made changes (stop, remove, run container)
- Health check passed
- Handler executed successfully

### 5.2 Container Status Verification

```
root@1fde1d5f6de8:/workspace# ansible webservers -a "docker ps" --ask-vault-pass
Vault password: 
aws-vm | CHANGED | rc=0 >>
CONTAINER ID   IMAGE                                COMMAND           CREATED          STATUS          PORTS                    NAMES
afc9c0fb699a   sunflye/devops-info-service:latest   "python app.py"   28 minutes ago   Up 28 minutes   0.0.0.0:5000->5000/tcp   devops-app
```

### 5.3 Health Check Verification and Main Endpoint Verification

```
root@1fde1d5f6de8:/workspace# curl http://34.229.125.207:5000/
{"endpoints":[{"description":"Service information","method":"GET","path":"/"},{"description":"Health check","method":"GET","path":"/health"}],"request":{"client_ip":"188.130.155.165","method":"GET","path":"/","user_agent":"curl/8.5.0"},"runtime":{"current_time":"2026-02-24T20:18:00.835698Z","timezone":"UTC","uptime_human":"0 hour, 29 minutes","uptime_seconds":1782},"service":{"description":"DevOps course info service","framework":"Flask","name":"devops-info-service","version":"1.0.0"},"system":{"architecture":"x86_64","cpu_count":1,"hostname":"afc9c0fb699a","platform":"Linux","platform_version":"Linux-6.14.0-1018-aws-x86_64-with-glibc2.41","python_version":"3.13.12"}}
root@1fde1d5f6de8:/workspace# curl http://34.229.125.207:5000/health
{"status":"healthy","timestamp":"2026-02-24T20:18:03.445124Z","uptime_seconds":1784}
root@1fde1d5f6de8:/workspace#
```

### 5.4 Handler Execution

**Handler triggered during deployment:**
```
RUNNING HANDLER [app_deploy : restart app] ************
ok: [aws-vm]
```
## 6. Key Decisions

### 6.1 Why use roles instead of plain playbooks?

Roles provide code reusability and maintainability at scale. Rather than writing all tasks in one playbook, roles organize code into logical units that can be applied independently. This allows the same role (e.g., Docker installation) to be used across multiple playbooks or projects without duplication, making infrastructure-as-code more modular and professional.

---

### 6.2 How do roles improve reusability?

Each role has a single responsibility (common system setup, Docker installation, app deployment). This separation means the `docker` role can be used on any server type—database servers, app servers, monitoring systems—without modification. Variables in `defaults/` allow customization without changing role logic, making roles portable across projects and organizations.

---

### 6.3 What makes a task idempotent?

Idempotent tasks check current state before making changes. The `apt` module checks if a package is already installed before installing, so running it twice produces the same result (package installed). This differs from shell commands which execute every time, potentially causing unintended consequences on repeated runs.

---

### 6.4 How do handlers improve efficiency?

Handlers are event-driven and only execute when notified by changed tasks. If Docker configuration changes, the handler restarts the service. But if Docker is already installed and unchanged, the handler doesn't run unnecessarily. This improves efficiency by avoiding redundant service restarts and reducing deployment time.

---

### 6.5 Why is Ansible Vault necessary?

Vault prevents accidental exposure of secrets (passwords, API keys, tokens) in Git repositories and logs. Docker Hub credentials must not be stored in plaintext in version control. Vault encrypts sensitive data at rest while keeping it readable at runtime through password-protected decryption, following security best practices for credential management.

---

## 7. Challenges Encountered

### Challenge 1: pip3 on Ubuntu 24.04

**Problem:** `pip install docker` failed with "externally-managed-environment" error.

**Solution:** Used `apt install python3-docker` instead of pip, respecting Ubuntu 24.04's policy of managing Python packages system-wide.

### Challenge 2: Docker Container Environment Variables

**Problem:** Environment variables (PORT, HOST) not recognized as strings in Ansible.

**Solution:** Applied Jinja2 filter `| string` to convert integer to string: `PORT: "{{ app_internal_port | string }}"`
