# DevOps Info Service

## Overview

Simple Flask-based REST API service that provides comprehensive system and runtime information. 

## Prerequisites

- Python 3.10+
- pip
- Git

## Installation

Clone repository and navigate to app_python:
```
cd app_python
```
Install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Running the Application

Run with default configuration:
```bash
python app.py
```

Or with custom configuration:

```bash
PORT=8080 HOST=127.0.0.1 python app.py
DEBUG=true python app.py
```

## API Endpoints

### GET /

Returns complete service and system information.

```bash
curl http://localhost:5000
```

### GET /health

Health check for monitoring and probes.

```bash
curl http://localhost:5000/health
```


## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `5000` | Server port |
| `DEBUG` | `False` | Enable debug mode |

## Docker

You can run this application in a container using Docker.

### Build the image locally

```bash
docker build -t <yourusername>/devops-info-service:latest .
```
- Replace `<yourusername>` with your Docker Hub username.
- This command builds the image from the Dockerfile in the current directory.

### Run a container

```bash
docker run -p 5000:5000 <yourusername>/devops-info-service:latest
```
- Maps container port 5000 to host port 5000.
- The app will be available at `http://localhost:5000`.

### Pull from Docker Hub

```bash
docker pull <yourusername>/devops-info-service:latest

docker run -p 5000:5000 <yourusername>/devops-info-service:latest
```
- Pulls the latest published image from Docker Hub and runs it.

---


## Testing

### Run tests locally

Install test dependencies (if not already in requirements.txt):
```bash
pip install pytest pytest-cov
```

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage report:
```bash
pytest tests/ -v --cov=app --cov-report=term --cov-report=html
```

Run specific test class:
```bash
pytest tests/test_app.py::TestMainEndpoint -v
```

Run specific test:
```bash
pytest tests/test_app.py::TestMainEndpoint::test_main_endpoint_status_code -v
```

### Test Coverage

Current test coverage: **89%** of application code

Tests cover:
- **GET /** endpoint - JSON structure, data types, all required fields
- **GET /health** endpoint - Status, timestamp, uptime
- **Error handling** - 404 responses and error JSON format
- **Data type validation** - Response field types verification


### CI/CD Automated Testing

Tests run automatically on:
- Every push to `master` or `lab03` branch
- Every pull request to `master` branch

See workflow status badge above for latest test results.

## CI/CD Status

[![Python CI/CD](https://github.com/sunflye/DevOps-course/actions/workflows/python-ci.yml/badge.svg)](https://github.com/sunflye/DevOps-course/actions/workflows/python-ci.yml)


## Visit Counter (Lab 12 — Task 1: Application Persistence Upgrade)

The application tracks visit counts in a persistent file (`/data/visits`). The counter:
- Increments on each `GET /` request
- Persists across container restarts
- Can be read via `GET /visits` endpoint
- Uses thread-safe file locking (`threading.Lock`) to prevent race conditions

### Implementation Pattern

```
Request to / → Read counter from file → Increment → Write back → Return response
Request to /visits → Read counter from file → Return count
```

### Counter Functions

```python
def read_visits():
    """Read visits count from file."""
    try:
        if os.path.exists(VISITS_FILE):
            with open(VISITS_FILE, 'r') as f:
                return int(f.read().strip())
    except (IOError, ValueError):
        pass
    return 0

def write_visits(count):
    """Write visits count to file."""
    with open(VISITS_FILE, 'w') as f:
        f.write(str(count))

def increment_visits():
    """Safely increment visits counter."""
    with visits_lock:
        count = read_visits()
        count += 1
        write_visits(count)
        return count
```

### Testing Persistence

```powershell
# 1. Start container
docker-compose up -d

# 2. Make requests (each increments counter)
curl http://localhost:5000/
curl http://localhost:5000/
curl http://localhost:5000/visits

# Output: {"visits":2,"timestamp":"2026-04-11T19:40:40.821933+00:00Z"}

# 3. Check file on host
cat data/visits
# Output: 2

# 4. Stop container
docker-compose stop

# 5. Verify file persisted (not deleted!)
cat data/visits
# Output: 2

# 6. Restart container
docker-compose up -d
Start-Sleep -Seconds 3

# 7. Counter should NOT reset
curl http://localhost:5000/visits
# Output: {"visits":2,...}

# 8. Make new request
curl http://localhost:5000/

# 9. Counter continues from 2 → 3
curl http://localhost:5000/visits
# Output: {"visits":3,...}

cat data/visits
# Output: 3
```

### Docker Compose Volume Mount

```yaml
# docker-compose.yml
volumes:
  - ./data:/data
```

**Configuration:**
- `./data` — host directory (persists after container stops)
- `/data` — container directory (where app writes visits file)

**Benefits:**
- ✅ Data persists on host after container stops
- ✅ Easy access to files from host machine
- ✅ Volume survives container restarts
- ✅ Multiple containers can share data

### Thread Safety

Uses `threading.Lock()` to ensure atomic operations when multiple requests arrive simultaneously:

```python
visits_lock = threading.Lock()

def increment_visits():
    with visits_lock:  # Prevents race conditions
        count = read_visits()
        count += 1
        write_visits(count)
        return count
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information (increments visit counter) |
| `/visits` | GET | Returns current visit count with timestamp |
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |
| `/ready` | GET | Readiness check |
