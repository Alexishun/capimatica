import pymysql

timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host="capimatica-mysql-capimatica.d.aivencloud.com",
  password="AVNS_V33wHPTnvdpr9Lw9HRD",
  read_timeout=timeout,
  port=12284,
  user="avnadmin",
  write_timeout=timeout,
)

try: 
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS puno_feature (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fecha_hora DATETIME NOT NULL,
        y_humedad FLOAT,
        y_precipitacion FLOAT,
        y_speedwind FLOAT,
        y_temperatura FLOAT,
        y_radiacion FLOAT,
        y_sensacion FLOAT
    );
    """
    cursor.execute(create_table_query)
    
    cursor.execute("show databases;")
    cursor.execute("use defaultdb;")
    cursor.execute("show tables;")
    print(cursor.fetchall())
finally:
    connection.close()


# try:
#     cursor = connection.cursor()

#     # Ver todas las bases de datos
#     cursor.execute("SHOW DATABASES;")
#     print("Bases de datos:", cursor.fetchall())

#     # Seleccionar tu base de datos (si no es defaultdb)
#     cursor.execute("USE defaultdb;")

#     # Ver las tablas dentro de esa base
#     cursor.execute("SHOW TABLES;")
#     tablas = cursor.fetchall()
#     print("Tablas disponibles:", tablas)

# finally:
    # connection.close()