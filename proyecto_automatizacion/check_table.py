import pyodbc

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=LogsAutomatizacion;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Obtener información de la tabla
cursor.execute('''
SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'ProcesoLog'
ORDER BY ORDINAL_POSITION
''')

columns = cursor.fetchall()
print('Estructura de la tabla ProcesoLog:')
for col in columns:
    max_len = col[2] if col[2] else ""
    print(f'{col[0]:<20} {col[1]:<15} {max_len}')

# Obtener algunos registros con el nuevo campo
cursor.execute('SELECT TOP 3 LogID, ProcesoID, Estado, NombreProceso, DuracionSegundos FROM ProcesoLog ORDER BY LogID DESC')
rows = cursor.fetchall()
print('\nÚltimos 3 registros:')
for row in rows:
    print(f'LogID: {row[0]}, ProcesoID: {row[1]}, Estado: {row[2]}, NombreProceso: {row[3]}, Duración: {row[4]}s')

conn.close()
