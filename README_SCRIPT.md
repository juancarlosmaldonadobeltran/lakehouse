# Guión para Teleprompter - Data Lakehouse con CDC y Apache Iceberg

Hola a todos. Hoy les voy a contar cómo crear un data-lakehouse realmente potente. Lo interesante es que lo hicimos en tiempo récord gracias a Amazon Q Developer. Vamos a ver cómo capturamos cambios en una base de datos relacional y los transformamos en algo realmente útil.

¿Sabías que CDC o Change Data Capture funciona como una cámara de seguridad para tu base de datos? Captura todos los cambios en los datos sin afectar el rendimiento de la base de datos. Por otra parte, Apache Iceberg es como un sistema de control de versiones para tus datos. Imagina poder volver a cualquier punto en el tiempo de tu información.

Le pedí a Amazon Q Developer que me ayudara con el código para conectar Spark con Iceberg y en segundos me generó la solución ahorrando días de trabajo.

Esta es la arquitectura propuesta: tenemos Postgres guardando los datos, Debezium y Kafka moviendo los cambios en tiempo real, y todo termina en tablas de Iceberg en S3 generando una línea de producción de datos bien definida.

¿Sabías que con Iceberg puedes prácticamente viajar en el tiempo a través de tus datos? Es como tener una máquina del tiempo. Debezium captura cada cambio en Postgres, Kafka lo distribuye, y Spark lo guarda todo en Iceberg. Así conservas la historia completa de tus datos.

Ahora veamos esto en acción: cuando insertamos datos en Postgres, observa lo que sucede. Todo el camino hasta Iceberg ocurre automáticamente. Y todo este código lo generó Amazon Q Developer usando algunos prompts.

En conclusión, puedes crear un data-lakehouse moderno en tiempo récord. Escalable, flexible y de alto rendimiento. Amazon Q Developer fue como tener un experto en cada tecnología disponible.