#!/bin/bash

echo "Waiting for Kafka to be ready..."
python -c "
import time
import socket
import sys

print('Checking if Kafka is ready...')
max_retries = 30
for i in range(max_retries):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('kafka', 9092))
        s.close()
        print('Kafka is ready!')
        sys.exit(0)
    except socket.error:
        pass
    
    print(f'Kafka not ready yet, waiting... ({i+1}/{max_retries})')
    time.sleep(5)

print('Timed out waiting for Kafka')
"

echo "Waiting for LocalStack to be ready..."
python -c "
import time
import requests
import sys

print('Checking if LocalStack is ready...')
max_retries = 30
for i in range(max_retries):
    try:
        response = requests.get('http://localstack:4566')
        if response.status_code in [200, 400, 404]:
            print('LocalStack is ready!')
            sys.exit(0)
    except Exception:
        pass
    
    print(f'LocalStack not ready yet, waiting... ({i+1}/{max_retries})')
    time.sleep(5)

print('Timed out waiting for LocalStack')
"

echo "Starting PySpark streaming job..."
/opt/bitnami/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:0.14.0,org.apache.hadoop:hadoop-aws:3.3.1 \
  --conf spark.ui.port=4040 \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkSessionCatalog \
  --conf spark.sql.catalog.spark_catalog.type=hive \
  --conf spark.sql.catalog.local=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.local.type=hadoop \
  --conf spark.sql.catalog.local.warehouse=s3a://lakehouse-bucket/events \
  --conf spark.hadoop.fs.s3a.endpoint=http://localstack:4566 \
  --conf spark.hadoop.fs.s3a.path.style.access=true \
  --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
  --conf spark.hadoop.fs.s3a.access.key=test \
  --conf spark.hadoop.fs.s3a.secret.key=test123 \
  /opt/spark/work-dir/cdc_consumer.py