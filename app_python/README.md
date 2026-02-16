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