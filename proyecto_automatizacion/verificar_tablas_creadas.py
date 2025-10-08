"""
Script para verificar las tablas creadas en la base de datos DestinoAutomatizacion
"""

import os
import django
import pyodbc

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import DatabaseConnection

def verificar_tablas_proceso(proceso_nombre="motomototo"):
    """Verifica las tablas creadas por un proceso"""
    try:
        # Obtener conexión de destino
        conn = DatabaseConnection.objects.filter(name='DestinoAutomatizacion').first()
        
        if not conn:
            print("❌ No se encontró la conexión DestinoAutomatizacion")
            return
        
        # Conectar a SQL Server
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={conn.server};"
            f"DATABASE={conn.database};"
            f"Trusted_Connection=yes;"
        )
        
        conn_db = pyodbc.connect(connection_string)
        cursor = conn_db.cursor()
        
        # Buscar tablas que contengan el nombre del proceso
        query = f"""
        SELECT 
            TABLE_NAME,
            (SELECT COUNT(*) FROM [{conn.database}].INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = t.TABLE_NAME) as NUM_COLUMNAS
        FROM [{conn.database}].INFORMATION_SCHEMA.TABLES t
        WHERE TABLE_NAME LIKE '%{proceso_nombre}%'
        ORDER BY TABLE_NAME
        """
        
        cursor.execute(query)
        tablas = cursor.fetchall()
        
        if not tablas:
            print(f"❌ No se encontraron tablas para el proceso '{proceso_nombre}'")
            return
        
        print("=" * 70)
        print(f"📊 TABLAS ENCONTRADAS PARA EL PROCESO '{proceso_nombre}':")
        print("=" * 70)
        
        for tabla, num_cols in tablas:
            print(f"\n✅ Tabla: {tabla}")
            print(f"   Columnas: {num_cols}")
            
            # Obtener nombres de columnas
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
                FROM [{conn.database}].INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{tabla}'
                ORDER BY ORDINAL_POSITION
            """)
            
            columnas = cursor.fetchall()
            print("   Estructura:")
            for col_name, data_type, max_length in columnas:
                tipo = f"{data_type}({max_length})" if max_length else data_type
                print(f"      - {col_name}: {tipo}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM [{tabla}]")
            count = cursor.fetchone()[0]
            print(f"   Registros: {count}")
            
            # Mostrar primeros 3 registros
            if count > 0:
                cursor.execute(f"SELECT TOP 3 * FROM [{tabla}]")
                rows = cursor.fetchall()
                print(f"   Primeros registros:")
                for i, row in enumerate(rows, 1):
                    print(f"      {i}. {dict(zip([col[0] for col in columnas], row))}")
        
        cursor.close()
        conn_db.close()
        
        print("\n" + "=" * 70)
        print(f"✅ Total de tablas encontradas: {len(tablas)}")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error al verificar tablas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("🔍 Verificando tablas creadas por el proceso corregido...\n")
    verificar_tablas_proceso("motomototo")
