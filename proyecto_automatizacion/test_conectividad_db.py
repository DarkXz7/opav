#!/usr/bin/env python3
"""
Test rápido de conectividad a SQL Server para diagnosticar el problema
"""

import os
import sys
import django
import pyodbc

# Configurar Django
sys.path.append('c:\\Users\\migue\\OneDrive\\Escritorio\\DJANGO DE NUEVO\\opav\\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.conf import settings

def test_database_connection():
    """Prueba la conexión a la base de datos destino"""
    print("🔍 Probando conexión a base de datos DestinoAutomatizacion...")
    
    try:
        # Usar configuración de Django
        destino_config = settings.DATABASES['destino']
        
        server = destino_config.get('HOST', 'localhost')
        database = destino_config.get('NAME', 'DestinoAutomatizacion')
        username = destino_config.get('USER', '')
        password = destino_config.get('PASSWORD', '')
        
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        
        print(f"📋 Servidor: {server}")
        print(f"📋 Base de datos: {database}")
        print(f"📋 Usuario: {username}")
        
        # Intentar conexión
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Probar consulta simple
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✅ Conexión exitosa!")
        print(f"📊 Versión SQL Server: {version[:50]}...")
        
        # Probar creación de tabla de prueba
        test_table = "TEST_CONEXION_TEMP"
        
        # Eliminar si existe
        cursor.execute(f"IF OBJECT_ID('{test_table}', 'U') IS NOT NULL DROP TABLE [{test_table}]")
        
        # Crear tabla de prueba
        cursor.execute(f"""
            CREATE TABLE [{test_table}] (
                ID int IDENTITY(1,1) PRIMARY KEY,
                TestColumn NVARCHAR(50)
            )
        """)
        
        # Insertar datos de prueba
        cursor.execute(f"INSERT INTO [{test_table}] (TestColumn) VALUES (?)", "Test Value")
        
        # Leer datos
        cursor.execute(f"SELECT * FROM [{test_table}]")
        result = cursor.fetchone()
        print(f"✅ Tabla de prueba creada e insertada: {result}")
        
        # Limpiar
        cursor.execute(f"DROP TABLE [{test_table}]")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Test de conectividad completado exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de conectividad: {str(e)}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    if not success:
        print("\n💡 Sugerencias:")
        print("1. Verificar que SQL Server Express esté ejecutándose")
        print("2. Verificar que la base de datos 'DestinoAutomatizacion' exista")
        print("3. Verificar credenciales de usuario")
        print("4. Verificar que ODBC Driver 17 for SQL Server esté instalado")
        sys.exit(1)
    else:
        print("\n🎉 La conectividad está funcionando correctamente!")
        sys.exit(0)