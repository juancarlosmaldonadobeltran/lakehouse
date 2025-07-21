#!/bin/sh

echo "Iniciando servicios..."
docker-compose up -d

echo "Esperando a que PostgreSQL esté listo..."
while ! docker exec postgres-transactions pg_isready -U admin -d transactions > /dev/null 2>&1; do
    echo "PostgreSQL aún no está listo, esperando..."
    sleep 2
done

echo "Esperando a que Kafka esté listo..."
sleep 10

echo "Creando topic cdc-events en Kafka..."
docker exec kafka kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1 --topic cdc-events

echo "Esperando a que Kafka Connect esté listo..."
sleep 60

# Verificar que Kafka Connect esté disponible
echo "Verificando que Kafka Connect esté disponible..."
while ! curl -s http://localhost:8083/ > /dev/null; do
    echo "Kafka Connect aún no está disponible, esperando..."
    sleep 10
done
echo "Kafka Connect está disponible"

# Esperar un poco más para asegurarse de que los plugins estén cargados
sleep 10

# Verificar que el conector Debezium esté disponible
echo "Verificando plugins disponibles en Kafka Connect..."
PLUGINS=$(curl -s http://localhost:8083/connector-plugins)
echo "Plugins disponibles:"
echo "$PLUGINS"

echo "Configurando conector Debezium para PostgreSQL..."
CONNECTOR_RESPONSE=$(curl -X POST -H "Content-Type: application/json" --data '
{
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
    "transforms": "",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}' http://localhost:8083/connectors/)

echo "Respuesta de la configuración del conector:"
echo "$CONNECTOR_RESPONSE"

# Verificar el estado del conector
sleep 5
echo "Verificando estado del conector..."
STATUS=$(curl -s http://localhost:8083/connectors/postgres-connector/status)
echo "Estado del conector:"
echo "$STATUS"

echo "\nServicios iniciados correctamente:"
echo "- LocalStack: http://localhost:4566"
echo "  - S3: Bucket 'lakehouse-bucket'"
echo "- Kafka: localhost:29092 (Topic: cdc-events)"
echo "- Zookeeper: localhost:2181"
echo "- PostgreSQL: localhost:5432 (DB: transactions, Usuario: admin, Contraseña: password)"
echo "- Kafka Connect: http://localhost:8083 (Conector PostgreSQL configurado)"
echo "- Data Generator: Servicio que realizará operaciones CRUD en la tabla 'users'"
echo "\nDebezium está configurado para enviar cambios de la tabla 'users' al topic de Kafka 'postgres.public.users'"
echo "El generador de datos esperará a que Kafka Connect esté listo antes de realizar operaciones"

echo "\nPara probar la tabla de usuarios:"
echo "docker exec postgres-transactions psql -U admin -d transactions -c \"SELECT * FROM users;\""

echo "\nPara ver los eventos en el topic de Kafka:"
echo "docker exec kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic postgres.public.users --from-beginning"

echo "\nPara listar los topics de Kafka:"
echo "docker exec kafka kafka-topics --list --bootstrap-server kafka:9092"

echo "\nPara verificar el estado del conector:"
echo "curl -X GET http://localhost:8083/connectors/postgres-connector/status"

echo "\nPara ver los conectores configurados:"
echo "curl -X GET http://localhost:8083/connectors"
