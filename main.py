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
  
# try:
#   cursor = connection.cursor()
#   cursor.execute("CREATE TABLE mytest (id INTEGER PRIMARY KEY)")
#   cursor.execute("INSERT INTO mytest (id) VALUES (1), (2)")
#   cursor.execute("SELECT * FROM mytest")
#   print(cursor.fetchall())
# finally:
#   connection.close()

try:
    cursor = connection.cursor()

    # Ver todas las bases de datos
    cursor.execute("SHOW DATABASES;")
    print("Bases de datos:", cursor.fetchall())

    # Seleccionar tu base de datos (si no es defaultdb)
    cursor.execute("USE defaultdb;")

    # Ver las tablas dentro de esa base
    cursor.execute("SHOW TABLES;")
    tablas = cursor.fetchall()
    print("Tablas disponibles:", tablas)

finally:
    connection.close()


