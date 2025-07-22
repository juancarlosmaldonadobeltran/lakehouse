from pyspark.sql import SparkSession

def main():
    # Create Spark Session
    spark = SparkSession.builder \
        .appName("CDC Debezium Consumer") \
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
    json_df.printSchema()
    # Print the raw JSON events to console
    query = json_df \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()
    
    print("CDC consumer started. Listening for events...")
    
    # Wait for the query to terminate
    query.awaitTermination()

if __name__ == "__main__":
    main()