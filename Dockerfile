# Multi-stage build for minimal image size
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

# Copy requirements and setup.py
COPY requirements.txt setup.py ./
COPY hmon ./hmon
COPY README.rst LICENSE ./

# Build wheels
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --wheel --no-deps -r requirements.txt && \
    pip install --no-cache-dir --wheel --no-deps .

# Final stage - minimal runtime image
FROM python:3.11-alpine

WORKDIR /app

# Install runtime dependencies only
# iputils for ping, net-tools for arp
RUN apk add --no-cache iputils net-tools

# Copy wheels from builder
COPY --from=builder /build /build
RUN pip install --no-cache-dir --no-index --find-links=/build /build && \
    rm -rf /build

# Copy application
COPY hmon ./hmon
COPY justrun.py .
COPY .env.example .env

# Create non-root user
RUN addgroup -g 1000 hmon && adduser -D -u 1000 -G hmon hmon

# Set permissions for metrics output directory (will be mounted)
RUN mkdir -p /var/lib/node_exporter/textfile_collector && \
    chown -R hmon:hmon /var/lib/node_exporter/textfile_collector && \
    chmod 755 /var/lib/node_exporter/textfile_collector

USER hmon

# Default configuration
ENV HOSTS_FILE=/etc/hosts \
    OUTPUT_DIR=/var/lib/node_exporter/textfile_collector \
    OUTPUT_FILE_BASE=node_network_hosts_up.prom \
    PING_TIMEOUT=1 \
    LOG_DIR=/tmp \
    LOG_LEVEL=INFO

# Health check - verify script runs without error
HEALTHCHECK --interval=5m --timeout=30s --start-period=10s --retries=3 \
    CMD python justrun.py || exit 1

# Run as entrypoint
ENTRYPOINT ["python", "justrun.py"]
CMD []
