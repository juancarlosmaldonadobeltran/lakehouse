# Lakehouse - Entorno de desarrollo para data lakehouse

Este proyecto configura un entorno de desarrollo local para servicios de data lakehouse utilizando LocalStack para S3, Kafka para streaming de datos y PostgreSQL para almacenamiento relacional.

## Estructura del proyecto

```
lakehouse/
├── docker-compose.yml      # Configuración de Docker Compose
├── run-localstack.sh       # Script para iniciar los servicios
├── localstack/
│   └── localstack_setup.sh # Script para configurar recursos en LocalStack
├── sql/
│   └── initdb.sql         # Script para inicializar la base de datos PostgreSQL
└── data-generator/
    ├── generate_data.py    # Generador de datos para pruebas
    └── requirements.txt   # Dependencias del generador de datos
```

## Requisitos previos

- Docker
- Docker Compose
- AWS CLI (opcional, para interactuar con los servicios)

## Servicios habilitados

- **Kafka**: Para streaming de datos y CDC (Change Data Capture)
- **PostgreSQL**: Para almacenamiento relacional y origen de eventos CDC
- **S3 (LocalStack)**: Para almacenamiento de objetos
- **Debezium Connect**: Plataforma CDC que captura cambios en PostgreSQL y los envía a Kafka
- **Data Generator**: Servicio que genera datos de prueba

## Uso

1. Dar permisos de ejecución a los scripts:
   ```bash
   chmod +x run-localstack.sh scripts/create-artifacts.sh
   ```

2. Iniciar LocalStack:
   ```bash
   ./run-localstack.sh
   ```

3. Interactuar con los servicios:
   ```bash
   # Ver eventos CDC en Kafka
   docker exec -it kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic postgres.public.users --from-beginning
   
   # Ver datos en PostgreSQL
   docker exec -it postgres-transactions psql -U admin -d transactions -c "SELECT * FROM users;"
   
   # Ver estado del conector Debezium
   curl -X GET http://localhost:8083/connectors/postgres-connector/status
   ```

## Endpoints de servicios

```
Kafka: localhost:29092 (Topic: postgres.public.users)
PostgreSQL: localhost:5432 (DB: transactions, Usuario: admin, Contraseña: password)
Debezium Connect: http://localhost:8083
LocalStack S3: http://localhost:4566 (Bucket: lakehouse-bucket)
```

## Detener los servicios

```bash
docker-compose down
```

## Probar los eventos de Kafka

Para ver los eventos CDC en el topic de Kafka:

```bash
docker exec -it kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic postgres.public.users --from-beginning
```

## Consultar la tabla Iceberg

Para consultar los datos almacenados en la tabla Iceberg:

```bash
docker exec -it spark-streaming /opt/spark/work-dir/run_query.sh
```

### Formato de eventos CDC

Los eventos CDC de Debezium contienen la siguiente estructura:

```json
{
  "schema": {...},
  "payload": {
    "before": {"id": 1, "name": "Old Name"},  // Estado anterior (null para inserciones)
    "after": {"id": 1, "name": "New Name"},   // Estado nuevo (null para eliminaciones)
    "source": {...},                            // Metadatos de la fuente
    "op": "u",                                // Tipo de operación (c=create, u=update, d=delete, r=read)
    "ts_ms": 1234567890,                       // Timestamp en milisegundos
    "transaction": null                        // Información de la transacción
  }
}
```

### Configuración del formato de eventos

Por defecto, el conector está configurado para mostrar el evento CDC completo. Si prefieres ver solo el estado final del registro (sin los campos before/after/op), puedes modificar el archivo `run-localstack.sh` para añadir la transformación `ExtractNewRecordState`:

```bash
"transforms": "unwrap",
"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
"transforms.unwrap.drop.tombstones": "false",
```

## Administrar Debezium

Para verificar el estado del conector:

```bash
curl -X GET http://localhost:8083/connectors/postgres-connector/status
```

Para pausar el conector:

```bash
curl -X PUT http://localhost:8083/connectors/postgres-connector/pause
```

Para reanudar el conector:

```bash
curl -X PUT http://localhost:8083/connectors/postgres-connector/resume
```