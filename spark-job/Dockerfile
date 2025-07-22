FROM python:3.9-slim

# Install Java - fixed to work with Debian slim image
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the PySpark job
COPY cdc_consumer.py .

# Command to run the job
CMD ["python", "cdc_consumer.py"]