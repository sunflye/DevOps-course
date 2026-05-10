# Lab 18 — Reproducible Builds with Nix

## Task 1 — Build Reproducible Python App (Revisiting Lab 1)

### 1.1: Nix Installation
```
polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course$ curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
info: downloading the Determinate Nix Installer
 INFO nix-installer v3.20.0
`nix-installer` needs to run as `root`, attempting to escalate now via `sudo`...
[sudo: authenticate] Password: 
 INFO nix-installer v3.20.0
Nix install plan (v3.20.0)
Planner: linux (with default settings)

Planned actions:
* Create directory `/nix`
* Install Determinate Nixd
* Extract the bundled Nix (originally from /nix/store/3h8wrgwk0rczd8rjv4fvl344mp1w765m-nix-binary-tarball-3.20.0/nix-3.20.0-x86_64-linux.tar.xz) to `/nix/temp-install-dir`
* Create a directory tree in `/nix`
* Synchronize /nix and /nix/var ownership
* Move the downloaded Nix into `/nix`
* Synchronize /nix/store ownership
* Create build users (UID 30001-30032) and group (GID 30000)
* Setup the default Nix profile
* Place the Nix configuration in `/etc/nix/nix.conf`
* Configure the shell profiles
* Configure the Determinate Nix daemon
* Cleanup


Proceed? ([Y]es/[n]o/[e]xplain): y
 INFO Step: Create directory `/nix`
 INFO Step: Install Determinate Nixd
 INFO Step: Provision Nix
 INFO Step: Create build users (UID 30001-30032) and group (GID 30000)
 INFO Step: Configure Nix
 INFO Step: Create directory `/etc/tmpfiles.d`
 INFO Step: Configure the Determinate Nix daemon
 INFO Step: Cleanup
 INFO Running self test for shell sh
 INFO Running self test for shell bash
Nix was installed successfully!
To get started using Nix, open a new shell or run `. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh`

polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course$ 
```
```
polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course$ nix --version
nix (Determinate Nix 3.20.0) 2.34.6
polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course$ 
```


### 1.2: Python Application Preparation
```
polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course/labs/lab18/app_python$ ls
Dockerfile  __pycache__  data         docs              tests
README.md   app.py       default.nix  requirements.txt
polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course/labs/lab18/app_python$
```

### 1.3: Nix Derivation for Python App

The application is built using the following Nix derivation in `default.nix`. It pins a stable version of `nixpkgs` to ensure reproducibility, defines the application's dependencies, and specifies a custom `installPhase` because the application is a simple script, not a standard Python package.

```nix
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/23.11.tar.gz") {} }:

pkgs.python311.pkgs.buildPythonApplication {
  pname = "devops-info-service";
  version = "1.0.0";

  src = ./.;

  propagatedBuildInputs = with pkgs.python311.pkgs; [
    flask
    prometheus-client
  ];

  # This is not a standard package with setup.py
  format = "other";

  # Specify how to "install" the application
  installPhase = ''
    mkdir -p $out/bin
    cp app.py $out/bin/devops-info-service
    chmod +x $out/bin/devops-info-service
  '';

  # Disable the check phase as we don't have tests configured here
  doCheck = false;
}
```

### 1.4: Proof of Reproducibility

#### 1.4.1: Successful Build and Run

First, the application was successfully built using `nix-build`. The build process shows Nix patching the script's interpreter to point to the correct Python version from the Nix store.

```bash
polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course/labs/lab18/app_python$ nix-build
...
patching script interpreter paths in /nix/store/b0dalrgy0fidaliqd8imwfskq3q1vrxx-devops-info-service-1.0.0
/nix/store/b0dalrgy0fidaliqd8imwfskq3q1vrxx-devops-info-service-1.0.0/bin/devops-info-service: interpreter directive changed from "#!/usr/bin/env python" to "/nix/store/qp5zys77biz7imbk6yy85q5pdv7qk84j-python3-3.11.6/bin/python"
...
/nix/store/b0dalrgy0fidaliqd8imwfskq3q1vrxx-devops-info-service-1.0.0
```

The application was then launched. The `DATA_DIR` environment variable was set to `./data` to ensure the state file is written to the current working directory, not the read-only Nix store, which would cause a `Permission denied` error.

```bash
polina@MagicBookX16:/mnt/d/INNOPOLIS/DEVOPS ENGINEERING/DevOps-course/labs/lab18/app_python$ DATA_DIR=./data ./result/bin/devops-info-service
{"timestamp": "2026-05-10T18:03:22.911354+00:00Z", "level": "INFO", "message": "Starting application on 0.0.0.0:5000", "module": ".devops-info-service-wrapped"}    
 * Serving Flask app '.devops-info-service-wrapped'
 * Debug mode: off
...
 * Running on http://127.0.0.1:5000
```

The running service was tested with `curl` and responded correctly:

```bash
$ curl http://localhost:5000/
{"endpoints":[...],"service":{"name":"devops-info-service","version":"1.0.0"},...}

$ curl http://localhost:5000/visits
{"timestamp":"2026-05-10T18:03:46.462401+00:00Z","visits":9}
```
![](/labs/lab18/app_python/docs/screenshots/33.png)
![](/labs/lab18/app_python/docs/screenshots/34.png)


#### 1.4.2: Proving Bit-for-Bit Reproducibility

To prove that Nix provides bit-for-bit reproducibility, I performed a forced rebuild, ensuring no source files were changed between builds.

1.  **First Build:** The build produced a specific, stable path in the Nix store.

    ```bash
    $ readlink result
    /nix/store/b0dalrgy0fidaliqd8imwfskq3q1vrxx-devops-info-service-1.0.0
    ```

2.  **Forced Rebuild:** I then removed the `result` symlink (the GC root) and manually deleted the build artifact from the Nix store to force a complete rebuild from scratch.

    ```bash
    # Save the path and remove the GC root
    $ storePath=$(readlink result)
    $ rm result
    
    # Delete the artifact from the Nix store
    $ nix-store --delete $storePath
    1 store paths deleted, 10.2 KiB freed
    
    # Rebuild from scratch
    $ nix-build
    ...
    /nix/store/b0dalrgy0fidaliqd8imwfskq3q1vrxx-devops-info-service-1.0.0
    ```

3.  **Verification:** The new build produced the **exact same store path**.

    ```bash
    $ readlink result
    /nix/store/b0dalrgy0fidaliqd8imwfskq3q1vrxx-devops-info-service-1.0.0
    ```

This demonstrates that given the same inputs (source code and Nix expression), Nix produces a bit-for-bit identical output every time. The hash `b0dalrgy0fidaliqd8imwfskq3q1vrxx` is a cryptographic proof of the build's contents.

#### 1.4.3: Demonstrating `pip`'s Non-Reproducibility

To contrast with Nix's guarantees, I performed an experiment to demonstrate the non-reproducibility of the traditional `pip` workflow. The experiment simulates installing dependencies at two different points in time, clearing `pip`'s cache in between to mimic a fresh setup on another machine or at a later date.

```bash
# Create unpinned requirements
$ echo "flask" > requirements-unpinned.txt
$ echo "prometheus-client" >> requirements-unpinned.txt

# First install
$ python3 -m venv venv1 && source venv1/bin/activate
$ pip install -r requirements-unpinned.txt && pip freeze > freeze1.txt
$ deactivate && rm -rf venv1

# Simulate time passing by clearing cache
$ pip cache purge

# Second install
$ python3 -m venv venv2 && source venv2/bin/activate
$ pip install -r requirements-unpinned.txt && pip freeze > freeze2.txt
$ deactivate && rm -rf venv2

# Compare results
$ diff freeze1.txt freeze2.txt
```

**Observation:**
The experiment successfully demonstrated the issue. The `diff` command showed that while the primary dependencies were the same, their transitive dependencies had different versions between the two installations.

```diff
1c1
< blinker==1.7.0
---
> blinker==1.8.2
8c8
< Werkzeug==3.0.2
---
> Werkzeug==3.0.3
```

This output proves that even though we requested `flask` both times, the versions of its own dependencies (`blinker` and `Werkzeug`) have drifted. This is the core problem: `requirements.txt` without hashes doesn't lock the entire dependency tree, leading to environments that are not bit-for-bit identical and causing "works on my machine" issues.

#### 1.4.4: Comparison with `pip`

| Aspect                  | Lab 1 (pip + venv)                               | Lab 18 (Nix)                                     |
| ----------------------- | ------------------------------------------------ | ------------------------------------------------ |
| **Python version**      | System-dependent, can vary between machines      | Pinned to `python3.11` in the derivation         |
| **Dependency resolution** | At runtime (`pip install`), can pull new versions | At build-time, pure and deterministic            |
| **Reproducibility**     | **Approximate.** Transitive dependencies can drift. | **Bit-for-bit identical.** The entire dependency tree is hashed. |
| **Portability**         | Requires same OS, Python version, and `pip install` | Works anywhere Nix is installed.                 |
| **Binary Caching**      | `pip` has a local cache, but it's not shared.    | Uses shared binary caches (`cache.nixos.org`).   |
| **Isolation**           | Virtual environment (`venv`)                     | Sandboxed build in the read-only `/nix/store`.   |

**Why `requirements.txt` is weaker:**
A `requirements.txt` file only guarantees the versions of the packages you list directly (e.g., `flask==3.0.0`). It does **not** pin the versions of Flask's own dependencies (like `Werkzeug`, `Jinja2`, `click`). Over time, a fresh `pip install` can pull newer versions of these transitive dependencies, leading to a different environment and potential "works on my machine" issues. Nix, by contrast, hashes the entire dependency graph, ensuring the environment is identical down to the last bit.

#### 1.4.5: Understanding the Nix Store Path

The Nix store path format is fundamental to its reproducibility guarantees:

`/nix/store/<hash>-<name>-<version>`

-   **/nix/store/**: The read-only directory where all build artifacts (derivations) are stored.
-   **`<hash>`**: A cryptographic hash (e.g., `b0dalrgy0fidaliqd8imwfskq3q1vrxx`) computed from *all* inputs to the build: source code, dependencies, compiler flags, and build scripts. Any change to any input results in a different hash. This is the core of content-addressable storage.
-   **`<name>-<version>`**: A human-readable name and version (e.g., `devops-info-service-1.0.0`) for easier identification. This part is purely for convenience and does not affect reproducibility; only the hash matters for uniqueness.

---

### 1.5: Reflection

If I had used Nix from the beginning in **Lab 1**, it would have solved several potential problems:

1.  **"Works on my machine" issues:** I wouldn't have had to worry if my Python version or the TA's Python version were different. The `default.nix` file would guarantee the exact same environment for everyone.
2.  **Dependency Drift:** I wouldn't need to manually run `pip freeze > requirements.txt`. The Nix derivation is the single source of truth for all dependencies, including transitive ones, preventing them from changing unexpectedly over time.
3.  **Simplified Setup:** Instead of a multi-step process (`python -m venv venv`, `source venv/bin/activate`, `pip install`), anyone could build and run the project with a single command: `nix-build`. This makes onboarding new developers or setting up CI/CD environments much simpler and more reliable.

## Task 2 — Reproducible Docker Images (Revisiting Lab 2)

### 2.1: Review Your Lab 2 Dockerfile

The goal of this task is to compare a traditional `Dockerfile` build with a reproducible build using Nix's `dockerTools`.

First, I located the `Dockerfile` from Lab 2 in the `app_python` directory:

```dockerfile
FROM python:3.13-slim

# Create non-root user with home directory and bash shell
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy only requirements.txt first for better layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files (source code and docs)
COPY app.py .

# Switch to non-root user
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
```

To demonstrate its lack of reproducibility, I built the image twice with a small delay.

```bash
# Build #1
$ docker build -t lab2-app:v1 ./app_python
[+] Building 16.9s (12/12) FINISHED
...
 => => naming to docker.io/library/lab2-app:v1

# Wait 5 seconds
$ sleep 5

# Build #2
$ docker build -t lab2-app:v2 ./app_python
[+] Building 1.0s (11/11) FINISHED
...
 => => naming to docker.io/library/lab2-app:v2

# Compare the resulting images
$ docker images | grep "lab2-app"
lab2-app     v1      494f15f37a73   About a minute ago   204MB
lab2-app     v2      1997e14c4dc3   About a minute ago   204MB
```

**Observation:**
As proven by the output, the two images have **different Image IDs** (`494f15f37a73` vs `1997e14c4dc3`) and creation timestamps, even though the source code and `Dockerfile` were identical. This proves that `docker build` is not bit-for-bit reproducible by default, as it embeds build-time metadata into the final image.

### 2.2: Build Docker Image with Nix

Now, I will create a truly reproducible Docker image using Nix's `dockerTools`.

First, I created `labs/lab18/app_python/docker.nix` with the following content. This file reuses the application built by `default.nix` and packages it into a minimal Docker image without needing a base OS like `python:3.13-slim`.

```nix
# filepath: labs/lab18/app_python/docker.nix
{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/23.11.tar.gz") {} }:

let
  # 1. Import our application built by default.nix
  app = pkgs.callPackage ./default.nix {};
in
# 2. Use dockerTools to build the image
pkgs.dockerTools.buildImage {
  name = "devops-info-service-nix";
  tag = "1.0.0";

  # 3. Copy our application from the Nix Store into the image
  copyToRoot = [ app ];

  # 4. Configure how to run the container
  config = {
    # Set the command to run
    Cmd = [ "${app}/bin/devops-info-service" ];
    # Set environment variables
    Env = [ "DATA_DIR=/data" ];
    # Expose the port
    ExposedPorts = { "5000/tcp" = {}; };
    # Create a volume for persistent data
    Volumes = { "/data" = {}; };
  };
}
```

### 2.3: Side-by-Side Comparison

To verify that both containers work identically, I ran them side-by-side. Initially, the container built with the traditional `Dockerfile` failed to start due to a permission error: the non-root `appuser` did not have write access to the `/app` directory.

I fixed this by adding `RUN chown -R appuser:appuser /app` to the `Dockerfile` and rebuilt the image. After the fix, both containers started successfully.

```bash
# Stop and remove any old containers
$ docker stop lab2-container nix-container
$ docker rm lab2-container nix-container

# Run the fixed Lab 2 container
$ docker run -d --name lab2-container -p 5000:5000 lab2-app:v1
70706a914970...

# Run the Nix-built container
$ docker run -d --name nix-container -p 5001:5000 devops-info-service-nix:1.0.0
e5dc8c42ff65...

# Check that both containers are running
$ docker ps
CONTAINER ID   IMAGE                           COMMAND                  CREATED          STATUS          PORTS                                         NAMES
e5dc8c42ff65   devops-info-service-nix:1.0.0   "/nix/store/apv61i5n…"   10 seconds ago   Up 9 seconds    0.0.0.0:5001->5000/tcp, [::]:5001->5000/tcp   nix-container
70706a914970   lab2-app:v1                     "python app.py"          13 seconds ago   Up 13 seconds   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp   lab2-container
```

Then, I tested both endpoints with `curl`, and both responded successfully.

```bash
$ curl http://localhost:5000/health
{"status":"healthy","timestamp":"2026-05-10T18:38:58.270128+00:00Z","uptime_seconds":18}

$ curl http://localhost:5001/health
{"status":"healthy","timestamp":"2026-05-10T18:39:11.831272+00:00Z","uptime_seconds":28}
```

**Observation:** After fixing the permission issue in the `Dockerfile`, both containers are running and serving requests identically. This highlights another benefit of the Nix approach: by explicitly defining the data volume (`/data`), we avoided this common Docker permission issue from the start.

**Proof of Running Containers:**
![](/labs/lab18/app_python/docs/screenshots/35.png)
![](/labs/lab18/app_python/docs/screenshots/36.png)
![](/labs/lab18/app_python/docs/screenshots/37.png)

### 2.4: Final Comparison: Reproducibility, Size, and Layers

This is the most critical comparison. I performed three tests to highlight the fundamental differences between the two approaches.

#### Test 1: Rebuild Reproducibility (SHA256 Hash Comparison)

I rebuilt both images twice and compared the SHA256 hash of the resulting artifacts. For the Nix image, I hashed the output `.tar.gz` file. For the Dockerfile image, I used `docker save`.

**Nix Build:**
```bash
$ nix-build docker.nix && sha256sum result
a4bc0e4b35987f2813bc229d0c5eb706af7e54e3826c3e19ddde74238b3afbbf  result
$ rm result && nix-build docker.nix && sha256sum result
a4bc0e4b35987f2813bc229d0c5eb706af7e54e3826c3e19ddde74238b3afbbf  result
```
**Result:** The hashes are **identical**. Nix produces a bit-for-bit identical artifact every time.

**Dockerfile Build:**
```bash
$ docker build -t lab2-app:test1 . > /dev/null
$ docker save lab2-app:test1 | sha256sum
a68277907cae48d3e4d58d719d34546ddd91aa836d1acd334081979572fb5341  -
$ docker build -t lab2-app:test2 . > /dev/null
$ docker save lab2-app:test2 | sha256sum
92c5a987819ea31725077984de6efa50a63444e1c3f67e2f8c4bfb6492fd2853  -
```
**Result:** The hashes are **different**. This is the ultimate proof that the traditional Docker build process is not reproducible.

#### Test 2: Image Size Comparison

```bash
$ docker images | grep -E "lab2-app|devops-info-service-nix"
lab2-app                 v1      126accac9217   5 minutes ago    204MB
devops-info-service-nix  1.0.0   475877efdd11   56 years ago     477MB
```

| Metric     | Lab 2 Dockerfile              | Lab 18 Nix `dockerTools`      |
| ---------- | ----------------------------- | ----------------------------- |
| Image Size | ~204MB                        | ~477MB                        |
| Analysis   | Relies on a shared base image | Bundles all dependencies from `/nix/store` for a self-contained artifact. This increases size but removes reliance on external base images. |

#### Test 3: Layer Analysis

**Dockerfile Image History:**
```bash
$ docker history lab2-app:v1
IMAGE          CREATED          CREATED BY                                      SIZE
126accac9217   5 minutes ago    CMD ["python" "app.py"]                         0B
<missing>      5 minutes ago    ...                                             ...
<missing>      15 minutes ago   RUN /bin/sh -c pip install ...                  21.9MB
...
<missing>      5 days ago       # debian.sh ...                                 87.4MB
```
The history shows multiple layers with varying, recent timestamps (`5 minutes ago`, `15 minutes ago`).

**Nix Image History:**
```bash
$ docker history devops-info-service-nix:1.0.0
IMAGE          CREATED   CREATED BY   SIZE      COMMENT
475877efdd11   N/A                    244MB
```
The history shows a single application layer with no specific creation time (`N/A` in some tools, or `1970-01-01` in others). Nix intentionally sets a fixed, deterministic timestamp (the Unix epoch) to eliminate time as a source of non-reproducibility.

---

### 2.5: Reflection

**Why can't traditional Dockerfiles achieve bit-for-bit reproducibility?**
1.  **Base Images:** Tags like `python:3.13-slim` are mutable. The image they point to can be updated, changing your build's foundation without you changing your `Dockerfile`.
2.  **Package Managers:** Commands like `apt-get update && apt-get install` will fetch the latest available packages *at build time*, leading to different results on different days.
3.  **Timestamps:** Docker embeds build timestamps into image layers and metadata, guaranteeing that two images built at different times will have different hashes.

**If you could redo Lab 2 with Nix, what would you do differently?**
I would have used Nix from the start. This would have eliminated the need for a `Dockerfile` entirely. The entire environment, from the Python interpreter to the final container image, would be defined in one place (`.nix` files). This would have also prevented the permission errors encountered, as the Nix approach encourages thinking about data persistence via volumes from the beginning.

**Practical scenarios where Nix's reproducibility matters:**
*   **CI/CD:** Guarantees that the artifact tested in CI is bit-for-bit identical to the one deployed to production.
*   **Security Audits:** Allows for precise analysis of an image's contents. If a vulnerability is found in a dependency, you can know with 100% certainty which images are affected just by looking at their Nix derivations.
*   **Rollbacks:** Enables perfect, reliable rollbacks to a previous version, as you are deploying a known, identical artifact, not rebuilding an old version with potentially new dependencies.

### 2.6: Comprehensive Comparison Summary

This table summarizes the core differences between the traditional Dockerfile approach from Lab 2 and the Nix-based approach from this lab.

| Aspect                 | Lab 2 Traditional Dockerfile                | Lab 18 Nix `dockerTools`                      |
| ---------------------- | ------------------------------------------- | --------------------------------------------- |
| **Base Images**        | Relies on mutable tags (`python:3.13-slim`) | No base image needed; built from pure derivations |
| **Timestamps**         | Different on each build, causing hash changes | Fixed and deterministic (Unix epoch)          |
| **Package Installation** | `pip install` at build time (can vary)      | Uses immutable Nix store paths                |
| **Reproducibility**    | ❌ **No.** Same Dockerfile → Different images | ✅ **Yes.** Same `docker.nix` → Identical images |
| **Caching**            | Layer-based, can break on minor changes   | Content-addressable, perfect caching          |
| **Image Size**         | ~204MB (relies on shared base image)        | ~477MB (fully self-contained)                 |
| **Security**           | Inherits vulnerabilities from base image    | Minimal set of dependencies, easier to audit  |
| **Portability**        | Requires Docker to run                      | Requires Nix to build, then Docker to run     |