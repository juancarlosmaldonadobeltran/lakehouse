#!/bin/bash

echo "Instalando conector Debezium para PostgreSQL..."

# Crear directorio para el conector
mkdir -p /kafka/connect/debezium-connector-postgres

# Descargar y descomprimir el conector
curl -s -o /tmp/debezium-postgres.tar.gz https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.1.4.Final/debezium-connector-postgres-2.1.4.Final-plugin.tar.gz
tar -xzf /tmp/debezium-postgres.tar.gz -C /kafka/connect/debezium-connector-postgres
rm /tmp/debezium-postgres.tar.gz

echo "Conector Debezium instalado correctamente"