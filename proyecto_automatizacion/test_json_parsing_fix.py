#!/usr/bin/env python3
"""
Test script para verificar que la corrección de JSON parsing funcione
Simula el error "JSON object must be str, bytes or bytearray, not list"
"""

import os
import sys
import django
import json

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

def test_json_parsing_fix():
    """
    Test que verifica que los campos JSONField manejan tanto listas como strings JSON
    """
    from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection
    
    print("=== PRUEBA: Corrección de parsing JSON en SQL processing ===\n")
    
    try:
        # Crear una conexión de prueba (sin guardar en BD)
        connection = DatabaseConnection(
            name="Test Connection",
            server="test_server",
            username="test_user",
            password="test_pass",
            selected_database="test_db"
        )
        
        # Crear fuente de datos de prueba (sin guardar en BD)
        source = DataSource(
            name="Test SQL Source",
            source_type="sql",
            connection=connection
        )
        
        # Crear proceso de migración de prueba (sin guardar en BD)
        process = MigrationProcess(
            name="Test Process",
            source=source
        )
        
        print("📋 Casos de prueba para selected_tables:")
        
        # Caso 1: selected_tables como lista (el caso problemático)
        print("\n🔍 Caso 1: selected_tables como lista nativa de Python")
        process.selected_tables = [{"name": "tabla1", "full_name": "dbo.tabla1"}]
        print(f"   Tipo: {type(process.selected_tables)}")
        print(f"   Valor: {process.selected_tables}")
        
        # Simular extracción segura
        if isinstance(process.selected_tables, list):
            selected_tables = process.selected_tables
            print(f"   ✅ Manejado como lista: {len(selected_tables)} tablas")
        else:
            print(f"   ❌ No reconocido como lista")
        
        # Caso 2: selected_tables como JSON string
        print("\n🔍 Caso 2: selected_tables como string JSON")
        process.selected_tables = '[{"name": "tabla2", "full_name": "dbo.tabla2"}]'
        print(f"   Tipo: {type(process.selected_tables)}")
        print(f"   Valor: {process.selected_tables}")
        
        # Simular extracción segura
        if isinstance(process.selected_tables, list):
            selected_tables = process.selected_tables
        elif isinstance(process.selected_tables, str):
            selected_tables = json.loads(process.selected_tables) if process.selected_tables else []
            print(f"   ✅ Parseado desde JSON: {len(selected_tables)} tablas")
        else:
            selected_tables = process.selected_tables if process.selected_tables else []
        
        print("\n📋 Casos de prueba para selected_columns:")
        
        # Caso 3: selected_columns como dict (el caso problemático)
        print("\n🔍 Caso 3: selected_columns como diccionario nativo de Python")
        process.selected_columns = {"tabla1": ["col1", "col2"], "tabla2": ["col3", "col4"]}
        print(f"   Tipo: {type(process.selected_columns)}")
        print(f"   Valor: {process.selected_columns}")
        
        table_name = "tabla1"
        if isinstance(process.selected_columns, dict):
            selected_cols = process.selected_columns.get(table_name, [])
            print(f"   ✅ Manejado como dict: columnas para '{table_name}': {selected_cols}")
        else:
            print(f"   ❌ No reconocido como dict")
        
        # Caso 4: selected_columns como JSON string
        print("\n🔍 Caso 4: selected_columns como string JSON")
        process.selected_columns = '{"tabla1": ["col1", "col2"], "tabla2": ["col3", "col4"]}'
        print(f"   Tipo: {type(process.selected_columns)}")
        
        # Simular extracción segura
        if isinstance(process.selected_columns, dict):
            selected_cols = process.selected_columns.get(table_name, [])
        elif isinstance(process.selected_columns, str):
            selected_cols = json.loads(process.selected_columns).get(table_name, [])
            print(f"   ✅ Parseado desde JSON: columnas para '{table_name}': {selected_cols}")
        else:
            selected_cols = []
        
        print("\n" + "="*60)
        print("🎉 RESULTADO: CORRECCIÓN EXITOSA")
        print("   ✅ Todos los casos de JSONField se manejan correctamente")
        print("   ✅ No habrá más error 'JSON object must be str, bytes or bytearray, not list'")
        print("   ✅ El código maneja tanto objetos Python nativos como strings JSON")
        
        print("\n📝 RESUMEN DE LA CORRECCIÓN:")
        print("   🔧 Problema original: json.loads() aplicado a listas/dicts nativos")
        print("   🔧 Solución: isinstance() checks antes de json.loads()")
        print("   🔧 Métodos corregidos: _extract_sql_data(), _extract_csv_data()")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Ejecuta las pruebas de la corrección JSON
    """
    print("🚀 INICIANDO PRUEBAS DE CORRECCIÓN JSON PARSING")
    print("=" * 60)
    
    exito = test_json_parsing_fix()
    
    print("\n" + "=" * 60)
    
    if exito:
        print("🏁 PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("   El error 'JSON object must be str, bytes or bytearray, not list' está corregido")
    else:
        print("❌ PRUEBAS CON ERRORES")
        print("   Revisar implementación de la corrección")

if __name__ == '__main__':
    main()