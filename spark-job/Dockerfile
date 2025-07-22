FROM bitnami/spark:3.3.0

USER root

# Install Python dependencies
RUN pip install kafka-python==2.0.2 requests boto3 s3fs

# Create directory for pre-downloading dependencies
RUN mkdir -p /opt/spark/deps

# Copy a script to pre-download dependencies
COPY download-deps.sh /opt/spark/deps/
RUN chmod +x /opt/spark/deps/download-deps.sh

# Pre-download Spark dependencies
RUN /opt/spark/deps/download-deps.sh

# Set working directory
WORKDIR /opt/spark/work-dir

# Switch back to non-root user
USER 1001