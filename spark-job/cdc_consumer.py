from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

def main():
    # Create Spark Session with Iceberg support
    spark = SparkSession.builder \
        .appName("CDC Debezium Consumer") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
        .config("spark.sql.catalog.spark_catalog.type", "hive") \
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.local.type", "hadoop") \
        .config("spark.sql.catalog.local.warehouse", "s3a://lakehouse-bucket/events") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.access.key", "test") \
        .config("spark.hadoop.fs.s3a.secret.key", "test123") \
        .getOrCreate()
    
    # Set log level to ERROR to reduce console output
    spark.sparkContext.setLogLevel("ERROR")
    
    print("Starting Kafka CDC consumer...")
    
    # Create streaming DataFrame from Kafka
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "postgres.public.users") \
        .option("startingOffsets", "earliest") \
        .load()
    
    # Convert value from Kafka to string
    json_df = df.selectExpr("CAST(value AS STRING) as json_value")
    
    # Add timestamp column for event time
    json_df = json_df.withColumn("event_time", current_timestamp())
    
    # Create Iceberg database if it doesn't exist
    spark.sql("CREATE DATABASE IF NOT EXISTS local.lakehouse_db")
    
    # Print the raw JSON events to console
    console_query = json_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()
    
    # Write the raw JSON events to Iceberg table
    iceberg_query = json_df \
        .writeStream \
        .outputMode("append") \
        .foreachBatch(lambda batch_df, batch_id: write_to_iceberg(batch_df, batch_id, spark)) \
        .start()
    
    print("CDC consumer started. Listening for events...")
    
    # Wait for the queries to terminate
    console_query.awaitTermination()
    iceberg_query.awaitTermination()

def write_to_iceberg(batch_df, batch_id, spark):
    """Write batch to Iceberg table"""
    if not batch_df.isEmpty():
        print(f"Writing batch {batch_id} to Iceberg table")
        
        # Create table if it doesn't exist
        spark.sql("""
        CREATE TABLE IF NOT EXISTS local.lakehouse_db.raw_events_iceberg (
            json_value STRING,
            event_time TIMESTAMP
        ) USING iceberg
        """)
        
        # Write the batch to the Iceberg table
        batch_df.write \
            .format("iceberg") \
            .mode("append") \
            .save("local.lakehouse_db.raw_events_iceberg")
        
        print(f"Batch {batch_id} written to Iceberg table")

if __name__ == "__main__":
    main()