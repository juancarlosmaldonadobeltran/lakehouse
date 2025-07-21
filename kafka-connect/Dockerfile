FROM confluentinc/cp-kafka-connect-base:7.3.0

# Instalar el conector Debezium para PostgreSQL
RUN confluent-hub install --no-prompt debezium/debezium-connector-postgresql:2.1.4

# Verificar que el conector se haya instalado correctamente
RUN ls -la /usr/share/confluent-hub-components/debezium-debezium-connector-postgresql