"""
Script para verificar la existencia de la tabla ProcesoLog en SQL Server
"""
import pyodbc
import os
import django

# Configurar el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def check_table_exists():
    print("=== Verificando la tabla ProcesoLog en SQL Server ===")
    
    try:
        # Obtener configuración de conexión del settings.py
        from django.conf import settings
        logs_db_settings = settings.DATABASES.get('logs', {})
        
        if not logs_db_settings:
            print("❌ No se encontró configuración para la base de datos 'logs' en settings.py")
            return
        
        # Construir connection string
        server = logs_db_settings.get('HOST', '')
        database = logs_db_settings.get('NAME', '')
        username = logs_db_settings.get('USER', '')
        password = logs_db_settings.get('PASSWORD', '')
        driver = logs_db_settings.get('OPTIONS', {}).get('driver', 'ODBC Driver 17 for SQL Server')
        
        print(f"Intentando conectar a: {server}, Base de datos: {database}")
        
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
        )
        
        # Conectar a SQL Server
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'ProcesoLog'
        """)
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ La tabla 'ProcesoLog' existe en la base de datos '{database}'")
            
            # Verificar estructura
            cursor.execute("SELECT TOP 1 * FROM ProcesoLog")
            columns = [column[0] for column in cursor.description]
            print(f"Columnas: {columns}")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM ProcesoLog")
            row_count = cursor.fetchone()[0]
            print(f"Total de registros: {row_count}")
            
            # Mostrar últimos registros
            if row_count > 0:
                print("\nÚltimos 5 registros:")
                cursor.execute("SELECT TOP 5 * FROM ProcesoLog ORDER BY ProcesoID DESC")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"ID: {row.ProcesoID}, Estado: {row.Estado}, Fecha: {row.FechaEjecucion}")
            else:
                print("⚠️ La tabla existe pero no contiene registros")
        else:
            print(f"❌ La tabla 'ProcesoLog' NO existe en la base de datos '{database}'")
            
            # Sugerir creación
            print("\nSugerencia: Cree la tabla con este script SQL:")
            print("""
            CREATE TABLE ProcesoLog (
                ProcesoID INT IDENTITY(1,1) PRIMARY KEY,
                FechaEjecucion DATETIME NOT NULL,
                Estado VARCHAR(100) NOT NULL,
                ParametrosEntrada NVARCHAR(MAX) NULL,
                DuracionSegundos FLOAT NULL,
                ErrorDetalle NVARCHAR(MAX) NULL
            );
            """)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al verificar la tabla: {str(e)}")

if __name__ == "__main__":
    check_table_exists()
