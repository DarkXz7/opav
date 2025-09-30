"""
Script para verificar los registros en la tabla ProcesoLog
"""
import pyodbc
import os
import django

# Configurar el entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def check_proceso_log_entries():
    print("=== Verificando registros en la tabla ProcesoLog ===")
    
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
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM ProcesoLog")
        row_count = cursor.fetchone()[0]
        
        print(f"\nTotal de registros en ProcesoLog: {row_count}")
        
        if row_count > 0:
            # Mostrar los registros
            print("\nÚltimos 10 registros:")
            print("-" * 100)
            print("{:<5} {:<36} {:<20} {:<20} {:<40}".format(
                "ID", "PROCESO ID", "FECHA", "ESTADO", "MENSAJE"))
            print("-" * 100)
            
            cursor.execute("""
                SELECT TOP 10 
                    LogID, 
                    ProcesoID, 
                    FechaEjecucion, 
                    Estado, 
                    CASE 
                        WHEN LEN(ParametrosEntrada) > 50 THEN LEFT(ParametrosEntrada, 47) + '...' 
                        ELSE ParametrosEntrada 
                    END as ParametrosEntrada,
                    DuracionSegundos,
                    CASE 
                        WHEN LEN(MensajeError) > 50 THEN LEFT(MensajeError, 47) + '...' 
                        ELSE MensajeError 
                    END as MensajeError
                FROM ProcesoLog 
                ORDER BY LogID DESC
            """)
            
            rows = cursor.fetchall()
            
            for row in rows:
                print("{:<5} {:<36} {:<20} {:<20} {:<40}".format(
                    row.LogID, 
                    str(row.ProcesoID) if row.ProcesoID else "None",
                    str(row.FechaEjecucion),
                    row.Estado,
                    row.MensajeError if row.MensajeError else "-"
                ))
                
                # Mostrar detalles adicionales
                print(f"   Parámetros: {row.ParametrosEntrada if row.ParametrosEntrada else '-'}")
                print(f"   Duración: {row.DuracionSegundos if row.DuracionSegundos else 0} segundos")
                print("-" * 100)
        else:
            print("⚠️ La tabla no contiene registros")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al verificar registros: {str(e)}")

if __name__ == "__main__":
    check_proceso_log_entries()
