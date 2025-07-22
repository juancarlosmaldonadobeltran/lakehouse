from pyspark.sql import SparkSession

def main():
    # Create Spark Session with Iceberg support
    spark = SparkSession.builder \
        .appName("Iceberg Query") \
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
    
    # Query the Iceberg table
    try:
        print("\n=== Iceberg Table Contents ===")
        spark.sql("SELECT * FROM local.lakehouse_db.raw_events_iceberg").show(100, False)
        print("\n=== Row Count ===")
        count = spark.sql("SELECT COUNT(*) FROM local.lakehouse_db.raw_events_iceberg").collect()[0][0]
        print(f"Total rows: {count}")
    except Exception as e:
        print(f"Error querying Iceberg table: {e}")
        
    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    main()