#!/usr/bin/env python3
import os
import time
import random
import logging
import psycopg2
import requests
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data-generator')

# Configuración desde variables de entorno
DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', 'postgres'),
    'port': os.environ.get('POSTGRES_PORT', '5432'),
    'user': os.environ.get('POSTGRES_USER', 'admin'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'password'),
    'dbname': os.environ.get('POSTGRES_DB', 'transactions')
}

# Nombres de ejemplo para generar datos
FIRST_NAMES = ['Juan', 'Maria', 'Carlos', 'Ana', 'Pedro', 'Laura', 'Miguel', 'Sofia', 'Luis', 'Elena']
LAST_NAMES = ['Garcia', 'Rodriguez', 'Martinez', 'Lopez', 'Gonzalez', 'Perez', 'Sanchez', 'Romero', 'Torres', 'Diaz']

def wait_for_postgres():
    """Esperar a que PostgreSQL esté disponible"""
    logger.info("Esperando a que PostgreSQL esté disponible...")
    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            logger.info("PostgreSQL está disponible")
            return
        except psycopg2.OperationalError:
            logger.info("PostgreSQL aún no está disponible, esperando...")
            time.sleep(2)

def wait_for_kafka_connect():
    """Esperar a que Kafka Connect con Debezium esté disponible"""
    logger.info("Esperando a que Kafka Connect esté disponible...")
    
    # Primero verificamos que el servicio esté disponible
    while True:
        try:
            response = requests.get("http://kafka-connect:8083/")
            if response.status_code == 200:
                logger.info("Kafka Connect está disponible")
                break
            else:
                logger.info("Kafka Connect aún no responde, esperando...")
                time.sleep(5)
        except Exception as e:
            logger.info(f"Error al conectar con Kafka Connect: {e}")
            time.sleep(5)
    
    # Luego verificamos si el conector está configurado y activo
    while True:
        try:
            # Primero verificamos si el conector existe
            response = requests.get("http://kafka-connect:8083/connectors")
            if response.status_code == 200:
                connectors = response.json()
                if "postgres-connector" in connectors:
                    # Verificamos el estado del conector
                    status_response = requests.get("http://kafka-connect:8083/connectors/postgres-connector/status")
                    if status_response.status_code == 200:
                        status = status_response.json().get("connector", {}).get("state", "")
                        if status == "RUNNING":
                            logger.info("Conector postgres-connector está activo")
                            return
                        else:
                            logger.info(f"Conector en estado: {status}, esperando...")
                    else:
                        logger.info("No se pudo obtener el estado del conector")
                else:
                    logger.info("Conector postgres-connector aún no está configurado, esperando...")
            else:
                logger.info("No se pudo obtener la lista de conectores")
            time.sleep(5)
        except Exception as e:
            logger.info(f"Error al verificar estado de Kafka Connect: {e}")
            time.sleep(5)

def generate_random_name():
    """Generar un nombre aleatorio"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return f"{first_name} {last_name}"

def insert_users(conn, count=5):
    """Insertar usuarios aleatorios"""
    cursor = conn.cursor()
    inserted_ids = []
    
    for _ in range(count):
        name = generate_random_name()
        cursor.execute("INSERT INTO users (name) VALUES (%s) RETURNING id;", (name,))
        user_id = cursor.fetchone()[0]
        inserted_ids.append(user_id)
        logger.info(f"Usuario insertado: ID={user_id}, Nombre={name}")
    
    conn.commit()
    return inserted_ids

def update_users(conn, user_ids):
    """Actualizar usuarios existentes"""
    if not user_ids:
        logger.info("No hay usuarios para actualizar")
        return
    
    cursor = conn.cursor()
    
    for user_id in user_ids:
        name = generate_random_name()
        cursor.execute("UPDATE users SET name = %s WHERE id = %s;", (name, user_id))
        logger.info(f"Usuario actualizado: ID={user_id}, Nuevo nombre={name}")
    
    conn.commit()

def delete_users(conn, user_ids, delete_count=2):
    """Eliminar algunos usuarios"""
    if not user_ids:
        logger.info("No hay usuarios para eliminar")
        return
    
    cursor = conn.cursor()
    
    # Seleccionar algunos IDs para eliminar
    to_delete = random.sample(user_ids, min(delete_count, len(user_ids)))
    
    for user_id in to_delete:
        cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        logger.info(f"Usuario eliminado: ID={user_id}")
        user_ids.remove(user_id)
    
    conn.commit()
    return user_ids

def run_data_operations():
    """Ejecutar operaciones CRUD en la tabla users"""
    wait_for_postgres()
    wait_for_kafka_connect()
    
    logger.info("Iniciando generación de datos...")
    
    # Conectar a PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        # Insertar usuarios
        logger.info("Insertando usuarios...")
        user_ids = insert_users(conn, count=5)
        
        # Esperar un momento
        time.sleep(2)
        
        # Actualizar usuarios
        logger.info("Actualizando usuarios...")
        update_users(conn, user_ids)
        
        # Esperar un momento
        time.sleep(2)
        
        # Eliminar algunos usuarios
        logger.info("Eliminando algunos usuarios...")
        remaining_ids = delete_users(conn, user_ids, delete_count=2)
        
        # Esperar un momento
        time.sleep(2)
        
        # Insertar más usuarios
        logger.info("Insertando más usuarios...")
        more_ids = insert_users(conn, count=3)
        
        # Combinar IDs
        all_ids = remaining_ids + more_ids
        
        # Actualizar todos los usuarios restantes
        logger.info("Actualizando todos los usuarios restantes...")
        update_users(conn, all_ids)
        
        logger.info("Operaciones de datos completadas")
        
    except Exception as e:
        logger.error(f"Error durante las operaciones de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        run_data_operations()
    except Exception as e:
        logger.error(f"Error en el generador de datos: {e}")