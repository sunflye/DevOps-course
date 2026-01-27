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

