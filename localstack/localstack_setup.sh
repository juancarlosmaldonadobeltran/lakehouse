#!/bin/bash
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}
error_exit() {
    log "Error: $1"
    exit 1
}

log "Creating the lakehouse S3 bucket"
awslocal s3 mb s3://lakehouse-bucket

log "Creating directory structure for Iceberg tables"
awslocal s3api put-object --bucket lakehouse-bucket --key events/

log "Creating directory for Flink job JARs"
awslocal s3api put-object --bucket lakehouse-bucket --key jars/

log "LocalStack setup completed"
