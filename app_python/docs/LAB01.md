# Lab 1 — DevOps Info Service: Submission

## 1. Framework Selection

### Choice: Flask

I selected Flask as my web framework for this project.

### Why Flask?

| Aspect | Flask | FastAPI | Django |
|--------|-------|---------|--------|
| **Learning Curve** | Easy | Medium | Steep |
| **Minimal Setup** | Yes | Yes | No |
| **Perfect for microservices** | Yes | Yes | No |
| **Dependencies** | Minimal | Minimal | Many |
| **Community** | Excellent | Growing | Largest |
| **Documentation** | Great | Excellent | Excellent |

**Reasoning:**

Flask is lightweight and designed for building microservices, which is ideal for DevOps applications. The framework is easy to understand - there is minimal magic happening behind the scenes, making it perfect for learning web application fundamentals.

Flask has minimal dependencies, resulting in smaller Docker images, and its large community provides plenty of ready-made solutions.



---
## 2. Best Practices Applied

### Practice 1: Clean Code Organization

**Code:**
```python
"""
DevOps Info Service
Main application module
"""
import os
import socket
import platform
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

def get_system_info():
    """Collect system information."""
    return {...}
```

**Why it matters:**
- Module docstring explains purpose
- Imports organized (standard library first, then Flask)
- Constants centralized (HOST, PORT)
- Functions have docstrings
- Clear, readable structure

---

### Practice 2: Error Handling

**Code:**
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500
```

**Why it matters:**
- App doesn't crash on errors
- Clients get meaningful responses
- Proper HTTP status codes (404, 500)
- Prevents exposing stack traces

---

### Practice 3: Configuration via Environment Variables

**Code:**
```python
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
```

**Usage:**
```bash
python app.py              # Uses defaults
PORT=8080 python app.py    # Custom port
```

**Why it matters:**
- Same code works in dev, test, and prod
- No hardcoded values
- Docker and Kubernetes can inject values easily
- Secrets stay out of code

---

### Practice 4: Logging

**Code:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"Request: {request.method} {request.path}")
logger.error(f"Error: {error_message}")
```

**Why it matters:**
- Can change log level without restarting
- Timestamps help debug timing issues
- Different levels (INFO, WARNING, ERROR) for filtering
- Production monitoring systems read these logs

---

### Practice 5: Version Pinning

**Code:**
```txt
Flask==3.1.0
Werkzeug==3.1.2
```

**Why it matters:**
- Exact versions = reproducible builds
- Prevents breaking changes from new versions
- Team members get same dependencies
- Docker images are consistent everywhere
---

## 3. API Documentation

### GET / — Service Information

**Endpoint:** `http://localhost:5000/`

**Request:**
```bash
curl http://localhost:5000 | python -m json.tool
```

**Response Structure:**
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "Flask"
  },
  "system": {
    "hostname": "MagicBookX16",
    "platform": "Windows",
    "platform_version": "Windows-11-10.0.26100-SP0",
    "architecture": "AMD64",
    "cpu_count": 16,
    "python_version": "3.13.5"
  },
  "runtime": {
    "uptime_seconds": 153,
    "uptime_human": "0 hour, 2 minutes",
    "current_time": "2026-01-27T10:14:48.063022Z",
    "timezone": "UTC"
  },
  "request": {
    "client_ip": "127.0.0.1",
    "user_agent": "curl/8.16.0",
    "method": "GET",
    "path": "/"
  },
  "endpoints": [
    {
      "path": "/",
      "method": "GET",
      "description": "Service information"
    },
    {
      "path": "/health",
      "method": "GET",
      "description": "Health check"
    }
  ]
}
```

**Response Code:** `200 OK`

### GET /health — Health Check

**Endpoint:** `http://localhost:5000/health`

**Request:**
```bash
curl http://localhost:5000/health | python -m json.tool
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T10:14:48.063022Z",
  "uptime_seconds": 153
}
```

**Response Code:** `200 OK`

**Why `/health` is important:**
- Kubernetes uses this to check if pod is alive (liveness probe)
- Load balancers use this to know if backend is healthy
- Monitoring systems alert on non-200 responses
- Will be used extensively in Labs 9+

### Testing commands

**With curl (direct output):**
```bash
curl http://localhost:5000
curl http://localhost:5000/health
```

**With curl and JSON formatting:**
```bash
curl http://localhost:5000 | python -m json.tool
curl http://localhost:5000/health | python -m json.tool
```
---

## 4. Testing Evidence

### Screenshots are located at:
```
app_python/docs/screenshots/
```

### Terminal output example:

```
curl http://localhost:5000 | python -m json.tool

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
    "client_ip": "127.0.0.1",
    "method": "GET",
    "path": "/",
    "user_agent": "curl/8.16.0"
  },
  "runtime": {
    "current_time": "2026-01-27T10:40:09.994687Z",
    "timezone": "UTC",
    "uptime_human": "0 hour, 0 minutes",
    "uptime_seconds": 6
  },
  "service": {
    "description": "DevOps course info service",
    "framework": "Flask",
    "name": "devops-info-service",
    "version": "1.0.0"
  },
  "system": {
    "architecture": "AMD64",
    "cpu_count": 16,
    "hostname": "MagicBookX16",
    "platform": "Windows",
    "platform_version": "Windows-11-10.0.26100-SP0",
    "python_version": "3.13.5"
  }
}
```
---

## 5. Challenges & Solutions

### Challenge 1: Timestamp Format

**Problem:**
The requirement specified ISO 8601 format with 'Z' suffix for UTC time.

**Initial attempt:**
```python
'current_time': datetime.now(timezone.utc).isoformat()
# Result: "2026-01-27T10:40:09.994687+00:00"  
```

**Solution:**
```python
'current_time': datetime.now(timezone.utc).isoformat().replace("+00:00", "") + "Z"
# Result: "2026-01-27T10:40:09.994687Z"  
```

**Why this matters:**
- Consistent timestamp format across all APIs
- 'Z' is standard ISO 8601 way to indicate UTC
- Other services need to parse timestamps reliably
---

## 6. GitHub Community


DevOps is fundamentally about collaboration. Stars and follows motivate open-source maintainers to keep improving their projects and help quality projects gain visibility in the community. 

By supporting developers who share knowledge freely, we build a professional network that strengthens the entire ecosystem. When we star and follow projects and people, we contribute to a culture of recognition and growth that benefits everyone in the DevOps community.

---

