import os
import socket
import platform
import logging
import json
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response, g
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
START_TIME = datetime.now(timezone.utc)

# ==================== JSON Logging ====================
class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON logs."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
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
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently being processed'
)

# Application-Specific Metrics
devops_info_endpoint_calls = Counter(
    'devops_info_endpoint_calls',
    'Devops info endpoint calls',
    ['endpoint']
)

system_info_collection_seconds = Histogram(
    'devops_info_system_collection_seconds',
    'System info collection time',
    buckets=[0.01, 0.05, 0.1, 0.5]
)

# ==================== Helper Functions ====================

def get_system_info():
    """Collect system information."""
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_version": platform.platform(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count(),
        "python_version": platform.python_version(),
    }


def get_uptime():
    """Calculate application uptime."""
    uptime = (datetime.now(timezone.utc) - START_TIME).total_seconds()
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    return {"seconds": int(uptime), "human": f"{hours} hour, {minutes} minutes"}


def get_request_info():
    """Collect request information."""
    return {
        "client_ip": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "Unknown"),
        "method": request.method,
        "path": request.path,
    }


# ==================== Request Hooks ====================

@app.before_request
def before_request_hook():
    """Track request start time and increment in-progress counter."""
    http_requests_in_progress.inc()
    g.start_time = time.time()  # Используй g вместо request
    logger.info(f"HTTP {request.method} {request.path} from {request.remote_addr}")


@app.after_request
def after_request_hook(response):
    """Record request metrics."""
    # Calculate duration
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)
    
    # Increment request counter
    http_requests_total.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    
    # Decrement in-progress counter
    http_requests_in_progress.dec()
    
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response


# ==================== Routes ====================

@app.route("/")
def index():
    """Main endpoint - service and system information."""
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
                "current_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "") + "Z",
                "timezone": "UTC",
            },
            "request": get_request_info(),
            "endpoints": [
                {"path": "/", "method": "GET", "description": "Service information"},
                {"path": "/health", "method": "GET", "description": "Health check"},
                {"path": "/metrics", "method": "GET", "description": "Prometheus metrics"},
            ],
        }

    logger.info("Serving main endpoint with system info")
    return jsonify(response), 200


@app.route("/health")
def health():
    """Health check endpoint."""
    uptime = get_uptime()
    response = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "") + "Z",
        "uptime_seconds": uptime["seconds"],
    }

    logger.debug(f'Health check: {response["status"]}')
    return jsonify(response), 200


@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 Not found: {request.method} {request.path}")
    return (
        jsonify(
            {
                "error": "Not Found",
                "message": "The requested endpoint does not exist",
                "available_endpoints": ["/", "/health", "/metrics"],
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"500 Internal server error: {str(error)}")
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


if __name__ == "__main__":
    logger.info("Starting DevOps Info Service v1.0.0")
    logger.info(f"Server running at http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)