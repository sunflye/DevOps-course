# Lab 2 — Docker Containerization

## 1. Docker Best Practices Applied

### 1.1 Non-root User

**What:**  
A dedicated non-root user (`appuser`) is created and the application runs as this user.

**Why:**  
Running as a non-root user improves container security. If an attacker compromises the container, they do not get root privileges on the host. Many platforms (like Kubernetes) require containers to run as non-root for security compliance.

**Dockerfile snippet:**
```dockerfile
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
```

---

### 1.2 Minimal Base Image

**What:**  
The image uses `python:3.13-slim` as the base.

**Why:**  
A slim image reduces the attack surface, download size, and build time. Fewer packages mean fewer vulnerabilities and faster deployments.

**Dockerfile snippet:**
```dockerfile
FROM python:3.13-slim
```

---

### 1.3 Layer Caching (Optimized Layer Order)

**What:**  
`requirements.txt` is copied and dependencies are installed before copying the application code.

**Why:**  
This allows Docker to cache the dependency installation layer. If only the code changes, dependencies are not reinstalled, making builds much faster.

**Dockerfile snippet:**
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
```

---

### 1.4 .dockerignore

**What:**  
A `.dockerignore` file is used to exclude unnecessary files and directories from the build context.

**Why:**  
This reduces the build context size, speeds up builds, and prevents sensitive or irrelevant files (like `.git`, `__pycache__`, local logs, etc.) from being added to the image.

**.dockerignore snippet:**
```
# Python cache and build artifacts
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# Virtual environments
venv/
.env

# System and IDE files
.DS_Store
*.log

# Version control
.git

# Documentation and screenshots (not needed in container)
docs/screenshots/
```

---

### 1.5 Only Necessary Files Copied

**What:**  
Only the files required to run the application are copied into the image.

**Why:**  
This keeps the image small and secure, and ensures that development files, tests, and secrets are not present in the production container.

**Dockerfile snippet:**
```dockerfile
COPY app.py .
COPY requirements.txt .
```

---
## 2. Image Information & Decisions

### Base Image Chosen and Justification

**Base image:**  
```dockerfile
FROM python:3.13-slim
```

**Justification:**  
- The `python:3.13-slim` image is an official Python image with unnecessary packages removed.
- It is much smaller than the full Python image, which reduces download time and attack surface.
- The slim variant is recommended for production as it contains only what is needed to run most Python apps, making the image more secure and efficient.

---

### Final Image Size and Assessment

After building the image, the final size is:

```bash
sunflye/devops-info-service   latest   76fc66edeef2   46 minutes ago   195MB
```

**Assessment:**  
- The image size is appropriate for a Python web application.
- This is significantly smaller than using the full `python:3.13` image (which can be 1GB+).
- Smaller images are faster to pull, push, and deploy, and reduce storage costs.

---

### Layer Structure Explanation

**Layer order in Dockerfile:**
1. `FROM python:3.13-slim` — base image layer
2. `RUN useradd -m appuser` — adds non-root user
3. `WORKDIR /app` — sets working directory
4. `COPY requirements.txt .` — copies dependency file
5. `RUN pip install --no-cache-dir -r requirements.txt` — installs dependencies
6. `COPY app.py .` — copies application code
7. `USER appuser` — switches to non-root user
8. `EXPOSE 5000` — documents the port
9. `CMD ["python", "app.py"]` — default command

**Why this order:**  
- Copying `requirements.txt` and installing dependencies before copying the code allows Docker to cache the dependency layer. If only the code changes, dependencies are not reinstalled, making builds much faster.
- Only necessary files are copied, keeping the image small.

---

### Optimization Choices Made

- **Slim base image:** Reduces size and vulnerabilities.
- **Layer caching:** Dependency installation is cached unless `requirements.txt` changes.
- **.dockerignore:** Excludes unnecessary files from the build context.
- **Non-root user:** Improves security.
- **Only necessary files copied:** Keeps the image minimal and secure.

## 3. Build & Run Process

### 3.1 Build the Docker Image

```bash
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\app_python> docker build -t sunflye/devops-info-service:latest .
[+] Building 2.3s (12/12) FINISHED                                                           docker:desktop-linux 
 => [internal] load build definition from Dockerfile                                                         0.0s 
 => => transferring dockerfile: 487B                                                                         0.0s 
 => [internal] load metadata for docker.io/library/python:3.13-slim                                          1.8s 
 => [auth] library/python:pull token for registry-1.docker.io                                                0.0s 
 => [internal] load .dockerignore                                                                            0.0s
 => => transferring context: 322B                                                                            0.0s
 => [1/6] FROM docker.io/library/python:3.13-slim@sha256:51e1a0a317fdb6e170dc791bbeae63fac5272c82f43958ef74  0.1s
 => => resolve docker.io/library/python:3.13-slim@sha256:51e1a0a317fdb6e170dc791bbeae63fac5272c82f43958ef74  0.1s
 => [internal] load build context                                                                            0.0s
 => => transferring context: 63B                                                                             0.0s
 => CACHED [2/6] RUN useradd --create-home --shell /bin/bash appuser                                         0.0s
 => CACHED [3/6] WORKDIR /app                                                                                0.0s
 => CACHED [4/6] COPY requirements.txt .                                                                     0.0s
 => CACHED [5/6] RUN pip install --no-cache-dir -r requirements.txt                                          0.0s
 => CACHED [6/6] COPY app.py .                                                                               0.0s
 => exporting to image                                                                                       0.2s
 => => exporting layers                                                                                      0.0s
 => => exporting manifest sha256:168b00bf887bfe5bda411d6182ecb84abc821c89c7d9d63b518d9211f821198b            0.0s
 => => exporting config sha256:4c6edff8b2bcffb7ebe8b57bcd79f1eda4cfabc2427273bc36da83c9fd75ece6              0.0s
 => => exporting attestation manifest sha256:b2c291ac18880145c8e454024f8616f0749704180ed4386e72532bdcbeccb4  0.1s
 => => exporting manifest list sha256:9922a56135c0204526ab9d33268d73f1c551b29616ebeae06a4d314f05738fa5       0.0s
 => => naming to docker.io/sunflye/devops-info-service:latest                                                0.0s
 => => unpacking to docker.io/sunflye/devops-info-service:latest 
```

---

### 3.2 Run the Container

```bash
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\app_python> docker run -p 5000:5000 sunflye/devops-info-service:latest
2026-02-01 22:03:29,257 - __main__ - INFO - Starting DevOps Info Service v1.0.0
2026-02-01 22:03:29,257 - __main__ - INFO - Server running at http://0.0.0.0:5000
 * Serving Flask app 'app'
 * Debug mode: off
2026-02-01 22:03:29,261 - werkzeug - INFO - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.2:5000
2026-02-01 22:03:29,261 - werkzeug - INFO - Press CTRL+C to quit
```

---

### 3.3 Test Endpoints

```bash
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\app_python> curl.exe http://localhost:5000 | python -m json.tool
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:100   688  100   688    0     0  29213      0 --:--:-- --:--:-- --:--:-- 29913
{
    "endpoints": [
        {
            "description": "Service information",   
            "method": "GET",
            "path": "/"
        },
        {
            "description": "Health check",
            "method": "GET",
            "path": "/health"
        }
    ],
    "request": {
        "client_ip": "172.17.0.1",
        "method": "GET",
        "path": "/",
        "user_agent": "curl/8.16.0"
    },
    "runtime": {
        "current_time": "2026-02-01T22:04:44.576783Z",
        "timezone": "UTC",
        "uptime_human": "0 hour, 0 minutes",        
        "uptime_seconds": 28
    },
    "service": {
        "description": "DevOps course info service",
        "framework": "Flask",
        "name": "devops-info-service",
        "version": "1.0.0"
    },
    "system": {
        "architecture": "x86_64",
        "cpu_count": 16,
        "hostname": "381be4ed45e4",
        "platform": "Linux",
        "platform_version": "Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.41",
        "python_version": "3.13.11"
    }
}
```

```bash
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\app_python> curl.exe http://localhost:5000/health | python -m json.tool
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:100    83  100    83    0     0   2888      0 --:--:-- --:--:-- --:--:--  2964
{
    "status": "healthy",
    "timestamp": "2026-02-01T22:05:38.098526Z",     
    "uptime_seconds": 82
}
```

---

### 3.4 Docker Hub Repository

Docker Hub URL:  
https://hub.docker.com/r/sunflye/devops-info-service

### 3.5 Docker Image Push

**Terminal output showing successful push and authentication:**

```bash
(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\app_python> docker login -u sunflye
Info → A Personal Access Token (PAT) can be used instead.
To create a PAT, visit https://app.docker.com/settings

Password:
Login Succeeded

(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\app_python> docker push sunflye/devops-info-service:latest
The push refers to repository [docker.io/sunflye/devops-info-service]
b77222a87dc3: Pushed
3f4b601b9012: Pushed
0bee50492702: Pushed
119d43eec815: Pushed
8843ea38a07e: Pushed
b15e19cfc204: Pushed
38e37d324303: Pushed
b15e19cfc204: Pushed
38e37d324303: Pushed
36b6de65fd8d: Pushed
latest: digest: sha256:76fc66edeef2c1f733dfc3b9d6d1611067f4a67f562442acac079fa7f8358653 size: 856

(venv) PS D:\INNOPOLIS\DEVOPS ENGINEERING\DevOps-course\app_python> docker push sunflye/devops-info-service:v1
The push refers to repository [docker.io/sunflye/devops-info-service]
38e37d324303: Layer already exists
36b6de65fd8d: Layer already exists
119d43eec815: Layer already exists
8843ea38a07e: Layer already exists
3f4b601b9012: Already exists
b15e19cfc204: Layer already exists
0bee50492702: Layer already exists
1da1696c3b45: Layer already exists
b77222a87dc3: Layer already exists
dff5860bd433: Layer already exists
v1: digest: sha256:76fc66edeef2c1f733dfc3b9d6d1611067f4a67f562442acac079fa7f8358653 size: 856
```
### 3.6 Tagging Strategy

**Explanation:**  
- I use two tags for my Docker image: `latest` and `v1`.
- The `latest` tag always points to the most recent build of the image. This is convenient for development, testing, and for users who want the newest version by default.
- The `v1` tag is a versioned tag that represents a stable, production-ready release. Using version tags allows for reproducible deployments and easy rollbacks if needed.
- This strategy follows Docker best practices, making it easy to distinguish between stable releases and ongoing development.

## 4. Technical Analysis

### Why does your Dockerfile work the way it does?

My Dockerfile is organized to make builds fast, images small, and the app secure:

- I use a minimal Python base image to keep the image size small and reduce security risks.
- I copy requirements.txt and install dependencies before copying the app code. This way, Docker caches the dependencies, so if I only change the code, the build is much faster.
- I create and use a non-root user for better security.
- I only copy the files needed to run the app, so the image does not include unnecessary or sensitive files.
This setup makes the build process efficient and the resulting image safe and lightweight.

---

### What would happen if you changed the layer order?

If I copied all application files before installing dependencies:
```dockerfile
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
```
then **any change in the code** would invalidate the cache for the dependencies layer, causing `pip install` to run on every build.  
This would make builds much slower and waste resources, especially in CI/CD pipelines.

---

### What security considerations did you implement?

- **Non-root user:** The container runs as `appuser` instead of root, reducing the risk if the app is compromised.
- **Minimal base image:** Using `python:3.13-slim` reduces the attack surface by including only essential packages.
- **.dockerignore:** Prevents sensitive files (like `.env`, `.git`, logs, and local caches) from being added to the image.
- **No secrets in image:** Only required files are copied; secrets and credentials are not included.

---

### How does .dockerignore improve your build?

The `.dockerignore` file excludes unnecessary files and directories from the Docker build context:
- **Faster builds:** Less data is sent to the Docker daemon, speeding up the build process.
- **Smaller images:** Unneeded files (like caches, logs, venv, and git history) are not included in the final image.
- **Better security:** Sensitive files (such as `.env` or `.git`) are not accidentally copied into the image.

### Challenges & Solutions

**Issue:**  
PowerShell vs Bash commands:  
Some common Docker commands (like `grep`) do not work in PowerShell, so I had to use `docker images` and find the image manually.

**Solution:**  
I adapted my workflow to use PowerShell-compatible commands and manually checked the output of `docker images` to find the image size and details.

