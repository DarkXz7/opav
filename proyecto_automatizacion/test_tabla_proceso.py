#!/usr/bin/env python
"""
Script de prueba para verificar que las tablas de proceso se crean en DestinoAutomatizacion
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.dynamic_table_service import dynamic_table_manager
from django.db import connections

def test_tabla_proceso():
    """
    Prueba la creación de una tabla de proceso en DestinoAutomatizacion
    """
    print("=" * 50)
    print("PRUEBA: Creación de tabla específica de proceso")
    print("=" * 50)
    
    try:
        # 1. Verificar conexión a DestinoAutomatizacion
        print("\n1. Verificando conexión a DestinoAutomatizacion...")
        destino_conn = connections['destino']
        cursor = destino_conn.cursor()
        
        # Verificar que estamos en la BD correcta
        cursor.execute("SELECT DB_NAME() as nombre_bd")
        bd_actual = cursor.fetchone()[0]
        print(f"   ✅ Conectado a BD: {bd_actual}")
        
        if bd_actual != "DestinoAutomatizacion":
            print(f"   ❌ ERROR: Se esperaba 'DestinoAutomatizacion', pero estamos en '{bd_actual}'")
            return False
        
        # 2. Crear tabla de prueba para un proceso
        print("\n2. Creando tabla para proceso de prueba...")
        nombre_proceso = "Test Importar Ventas"
        
        # Usar el servicio para crear la tabla
        nombre_tabla = dynamic_table_manager.ensure_process_table(
            process_name=nombre_proceso,
            recreate=True
        )
        
        print(f"   ✅ Tabla creada: {nombre_tabla}")
        
        # 3. Verificar que la tabla se creó en DestinoAutomatizacion
        print("\n3. Verificando existencia de tabla...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = ? AND TABLE_CATALOG = 'DestinoAutomatizacion'
        """, [nombre_tabla])
        
        tabla_existe = cursor.fetchone()[0] > 0
        
        if tabla_existe:
            print(f"   ✅ Tabla '{nombre_tabla}' existe en DestinoAutomatizacion")
            
            # 4. Verificar estructura de la tabla
            print("\n4. Verificando estructura de la tabla...")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = ? AND TABLE_CATALOG = 'DestinoAutomatizacion'
                ORDER BY ORDINAL_POSITION
            """, [nombre_tabla])
            
            columnas = cursor.fetchall()
            print("   Columnas encontradas:")
            for col_name, data_type, is_nullable in columnas:
                print(f"     - {col_name} ({data_type}) {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
            
            # 5. Insertar datos de prueba
            print("\n5. Insertando datos de prueba...")
            resultado_id = dynamic_table_manager.insert_to_process_table(
                table_name=nombre_tabla,
                data={
                    'ProcesoID': 'test-proceso-123',
                    'DatosProcesados': '{"test": "data", "registros": 10}',
                    'UsuarioResponsable': 'sistema_test',
                    'EstadoProceso': 'COMPLETADO',
                    'TipoOperacion': 'TEST_MIGRACION',
                    'RegistrosAfectados': 10,
                    'MetadatosProceso': '{"test_mode": true}'
                }
            )
            
            print(f"   ✅ Datos insertados con ResultadoID: {resultado_id}")
            
            # 6. Verificar que los datos se guardaron
            print("\n6. Verificando datos guardados...")
            cursor.execute(f"SELECT COUNT(*) FROM [{nombre_tabla}]")
            num_registros = cursor.fetchone()[0]
            print(f"   ✅ Registros en tabla: {num_registros}")
            
            if num_registros > 0:
                cursor.execute(f"SELECT TOP 1 * FROM [{nombre_tabla}]")
                registro = cursor.fetchone()
                print(f"   📋 Primer registro: {registro}")
            
            print("\n" + "=" * 50)
            print("✅ PRUEBA EXITOSA: Las tablas de proceso se crean correctamente en DestinoAutomatizacion")
            print("=" * 50)
            return True
            
        else:
            print(f"   ❌ ERROR: Tabla '{nombre_tabla}' NO se creó en DestinoAutomatizacion")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR durante la prueba: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        try:
            cursor.close()
        except:
            pass

if __name__ == "__main__":
    exito = test_tabla_proceso()
    sys.exit(0 if exito else 1)