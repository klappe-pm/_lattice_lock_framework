FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
# curl for healthcheck, build-essential for compiling some python extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.lock pyproject.toml /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.lock

# Copy source code
COPY src /app/src
COPY README.md /app/

# Install the package
RUN pip install -e .

# Create non-root user for security
RUN useradd -m lattice
USER lattice

# Expose the API port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "lattice_lock.admin.api:app", "--host", "0.0.0.0", "--port", "8080"]
