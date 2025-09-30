"""
Script para verificar la estructura exacta de la tabla ProcesoLog
"""
import pyodbc
import os
import django

# Configurar el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def check_table_structure():
    print("=== Verificando la estructura exacta de la tabla ProcesoLog ===")
    
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
        
        # Consultar la estructura exacta de la tabla
        cursor.execute("""
            SELECT 
                COLUMN_NAME, 
                DATA_TYPE, 
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ProcesoLog'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print("\nEstructura de la tabla ProcesoLog:")
            print("-" * 80)
            print("{:<20} {:<15} {:<10} {:<10} {:<20}".format(
                "COLUMNA", "TIPO", "TAMAÑO", "NULLABLE", "DEFAULT"))
            print("-" * 80)
            
            for col in columns:
                print("{:<20} {:<15} {:<10} {:<10} {:<20}".format(
                    col.COLUMN_NAME,
                    col.DATA_TYPE,
                    str(col.CHARACTER_MAXIMUM_LENGTH) if col.CHARACTER_MAXIMUM_LENGTH else "N/A",
                    col.IS_NULLABLE,
                    str(col.COLUMN_DEFAULT) if col.COLUMN_DEFAULT else "NULL"
                ))
            
            # Propuesta de modelo Django basada en la estructura real
            print("\nModelo Django propuesto:")
            print("-" * 80)
            print("class ProcesoLog(models.Model):")
            
            for col in columns:
                field_type = "models.CharField"
                field_args = ""
                
                if col.DATA_TYPE == "int":
                    if col.COLUMN_NAME == "LogID":
                        field_type = "models.AutoField"
                        field_args = "primary_key=True"
                    else:
                        field_type = "models.IntegerField"
                elif col.DATA_TYPE == "datetime":
                    field_type = "models.DateTimeField"
                elif col.DATA_TYPE == "float":
                    field_type = "models.FloatField"
                elif col.DATA_TYPE == "varchar":
                    field_type = "models.CharField"
                    field_args = f"max_length={col.CHARACTER_MAXIMUM_LENGTH}"
                elif col.DATA_TYPE == "nvarchar" or col.DATA_TYPE == "text":
                    field_type = "models.TextField"
                elif col.DATA_TYPE == "uniqueidentifier":
                    field_type = "models.UUIDField"
                
                if col.IS_NULLABLE == "YES" and col.COLUMN_NAME != "LogID":
                    if field_args:
                        field_args += ", "
                    field_args += "null=True, blank=True"
                
                print(f"    {col.COLUMN_NAME} = {field_type}({field_args})")
            
            print("\n    class Meta:")
            print("        managed = False")
            print("        db_table = 'ProcesoLog'")
            
        else:
            print("❌ No se encontró la estructura de la tabla 'ProcesoLog'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al verificar la estructura: {str(e)}")

if __name__ == "__main__":
    check_table_structure()
