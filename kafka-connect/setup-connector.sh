#!/bin/bash

echo "Configurando conector Debezium para PostgreSQL..."

# Esperar a que Kafka Connect esté disponible
echo "Esperando a que Kafka Connect esté disponible..."
until curl -s http://kafka-connect:8083/ > /dev/null; do
    echo "Kafka Connect aún no está disponible, esperando..."
    sleep 5
done
echo "Kafka Connect está disponible"

# Crear el conector
echo "Creando conector postgres-connector..."
curl -X POST -H "Content-Type: application/json" --data '{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "admin",
    "database.password": "password",
    "database.dbname": "transactions",
    "topic.prefix": "postgres",
    "database.server.name": "postgres",
    "table.include.list": "public.users",
    "plugin.name": "pgoutput",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "false",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}' http://kafka-connect:8083/connectors/

echo "Configuración completada"