"""
DevOps Info Service
Main application module
"""

import os
import socket
import platform
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
START_TIME = datetime.now(timezone.utc)

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

    logger.info(f"Request: {request.method} {request.path}")
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
    logger.warning(f"Not found: {request.method} {request.path}")
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
    logger.error(f"Internal server error: {str(error)}")
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
