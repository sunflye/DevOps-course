import os
import socket
import platform
import logging
import json
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, jsonify, request, Response, g
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# ==================== Configuration ====================
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ✅ базовый каталог рядом с app.py
BASE_DIR = Path(__file__).resolve().parent
# ✅ по умолчанию пишем в локальную папку app_python/data
# в Docker/K8s переопределяется через DATA_DIR=/data
DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))

START_TIME = datetime.now(timezone.utc)

# Ensure data directory exists
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
VISITS_FILE = os.path.join(DATA_DIR, "visits")
visits_lock = threading.Lock()

# ==================== Visits Counter ====================
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

# ==================== JSON Logging ====================
class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs."""
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ==================== Prometheus Metrics ====================

# HTTP Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed',
    ['method', 'endpoint']
)

# Application-specific metrics
devops_info_endpoint_calls = Counter(
    'devops_info_endpoint_calls',
    'Endpoint calls',
    ['endpoint']
)

system_info_collection_seconds = Histogram(
    'devops_info_system_collection_seconds',
    'System info collection time'
)

# ==================== Helper Functions ====================
def get_system_info():
    """Collect system information."""
    return {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'architecture': platform.machine(),
        'python_version': platform.python_version(),
        'cpu_count': os.cpu_count() or 1,
    }

def get_uptime():
    """Calculate uptime."""
    uptime_seconds = int((datetime.now(timezone.utc) - START_TIME).total_seconds())
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    return {
        'seconds': uptime_seconds,
        'human': f"{hours} hour, {minutes} minutes"
    }

def get_request_info():
    """Get request information."""
    return {
        'method': request.method,
        'path': request.path,
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'client_ip': request.remote_addr,
    }

# ==================== Middleware ====================
@app.before_request
def before_request():
    """Track request start time and increment in-progress gauge."""
    g.start_time = time.time()
    method = request.method
    endpoint = request.path or '/'
    http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
    logger.info(f"Request started: {method} {endpoint}")

@app.after_request
def after_request(response):
    """Track request duration and record metrics."""
    method = request.method
    endpoint = request.path or '/'
    status = response.status_code
    
    # Record duration
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    # Decrement in-progress gauge
    http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
    
    # Record total requests
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    
    logger.info(f"Request completed: {method} {endpoint} {status}")
    return response

# ==================== Routes ====================
@app.route('/')
def index():
    """Service information endpoint."""
    increment_visits()
    devops_info_endpoint_calls.labels(endpoint='/').inc()
    
    with system_info_collection_seconds.time():
        uptime = get_uptime()
        response = {
            "service": {
                "name": "devops-info-service",
                "version": "1.0.0",
                "description": "DevOps course info service",
                "framework": "Flask",
            },
            "system": get_system_info(),
            "runtime": {
                "uptime_seconds": uptime["seconds"],
                "uptime_human": uptime["human"],
                "current_time": datetime.now(timezone.utc).isoformat() + "Z",
                "timezone": "UTC",
            },
            "request": get_request_info(),
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Service information"},
                {"path": "/health", "method": "GET", "description": "Health check"},
                {"path": "/visits", "method": "GET", "description": "Visit count"},
                {"path": "/metrics", "method": "GET", "description": "Prometheus metrics"},
            ]
        }
        return jsonify(response)

@app.route('/visits')
def visits():
    """Return current visit count."""
    count = read_visits()
    return jsonify({
        'visits': count,
        'timestamp': datetime.now(timezone.utc).isoformat() + "Z"
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    devops_info_endpoint_calls.labels(endpoint='/health').inc()
    uptime = get_uptime()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat() + "Z",
        'uptime_seconds': uptime['seconds']
    })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/ready')
def ready():
    """Readiness check endpoint."""
    return jsonify({'ready': True})

# ==================== Error Handlers ====================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ==================== Main ====================
if __name__ == '__main__':
    logger.info(f"Starting application on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
