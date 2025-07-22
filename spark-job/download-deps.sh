#!/bin/bash

echo "Pre-downloading Spark dependencies..."

# Create a temporary POM file to download dependencies
cat > /tmp/pom.xml << EOF
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>spark-deps-downloader</artifactId>
    <version>1.0-SNAPSHOT</version>
    <dependencies>
        <dependency>
            <groupId>org.apache.spark</groupId>
            <artifactId>spark-sql-kafka-0-10_2.12</artifactId>
            <version>3.3.0</version>
        </dependency>
        <dependency>
            <groupId>org.apache.iceberg</groupId>
            <artifactId>iceberg-spark-runtime-3.3_2.12</artifactId>
            <version>0.14.0</version>
        </dependency>
        <dependency>
            <groupId>org.apache.hadoop</groupId>
            <artifactId>hadoop-aws</artifactId>
            <version>3.3.1</version>
        </dependency>
    </dependencies>
</project>
EOF

# Use Spark's built-in ivy to download dependencies
cd /opt/bitnami/spark
./bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:0.14.0,org.apache.hadoop:hadoop-aws:3.3.1 --class org.apache.spark.examples.SparkPi --master local[1] examples/jars/spark-examples_2.12-3.3.0.jar 10

echo "Dependencies downloaded successfully"