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