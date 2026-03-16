import os
import socket
import platform
import logging
import json
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
START_TIME = datetime.now(timezone.utc)

# JSON Logging Configuration
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
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Setup JSON logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.handlers.clear()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


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


@app.before_request
def log_request():
    """Log incoming request."""
    logger.info(f"HTTP {request.method} {request.path} from {request.remote_addr}")


@app.after_request
def log_response(response):
    """Log response after request."""
    logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response


@app.route("/")
def index():
    """Main endpoint - service and system information."""
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
            "current_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "")
            + "Z",
            "timezone": "UTC",
        },
        "request": get_request_info(),
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Service information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
        ],
    }

    logger.info(f"Serving main endpoint with system info")
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


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 Not found: {request.method} {request.path}")
    return (
        jsonify(
            {
                "error": "Not Found",
                "message": "The requested endpoint does not exist",
                "available_endpoints": ["/", "/health"],
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