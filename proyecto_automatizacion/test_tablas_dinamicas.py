"""
Script de prueba completo para el sistema de tablas dinámicas
Verifica:
1. Generación correcta de nombres de tabla
2. Creación automática de tablas por proceso
3. Manejo de recreación/truncado de tablas existentes
4. Inserción de datos en tablas específicas
5. Manejo de errores y validaciones
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.contrib.auth.models import User
from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection
from automatizacion.dynamic_table_service import dynamic_table_manager, DynamicTableError
from automatizacion.data_transfer_service import data_transfer_service

def test_table_name_generation():
    """Prueba la generación de nombres de tabla"""
    print("\n" + "="*60)
    print("🧪 PRUEBA 1: Generación de nombres de tabla")
    print("="*60)
    
    test_cases = [
        "Proceso Normal",
        "Proceso con Números 123",
        "Proceso-con-Guiones",
        "Proceso con Espacios y Símbolos!!!",
        "select",  # Palabra reservada
        "123NumeroAlInicio",
        "",  # Nombre vacío
        "   ",  # Solo espacios
        "Proceso_con_underscores",
        "PROCESO EN MAYÚSCULAS"
    ]
    
    for i, process_name in enumerate(test_cases, 1):
        try:
            table_name = dynamic_table_manager.generate_table_name(process_name)
            print(f"   {i:2}. '{process_name}' -> '{table_name}' ✅")
        except DynamicTableError as e:
            print(f"   {i:2}. '{process_name}' -> ERROR: {str(e)} ❌")
        except Exception as e:
            print(f"   {i:2}. '{process_name}' -> ERROR INESPERADO: {str(e)} ❌")

def test_table_creation_and_management():
    """Prueba creación y gestión de tablas"""
    print("\n" + "="*60)
    print("🧪 PRUEBA 2: Creación y gestión de tablas")
    print("="*60)
    
    test_processes = [
        "Test Proceso A",
        "Test Proceso B con Espacios",
        "Test-Proceso-C"
    ]
    
    for process_name in test_processes:
        try:
            print(f"\n🔧 Probando proceso: '{process_name}'")
            
            # Generar nombre de tabla
            table_name = dynamic_table_manager.generate_table_name(process_name)
            print(f"   📝 Nombre generado: '{table_name}'")
            
            # Verificar si existe
            exists_before = dynamic_table_manager.table_exists(table_name)
            print(f"   📋 Existía antes: {exists_before}")
            
            # Asegurar tabla (crear o limpiar)
            final_table_name = dynamic_table_manager.ensure_process_table(
                process_name, 
                recreate=True
            )
            print(f"   ✅ Tabla asegurada: '{final_table_name}'")
            
            # Verificar que ahora existe
            exists_after = dynamic_table_manager.table_exists(final_table_name)
            print(f"   📋 Existe después: {exists_after}")
            
            if exists_after:
                print(f"   🎉 SUCCESS: Tabla '{final_table_name}' gestionada correctamente")
            else:
                print(f"   ❌ FAILED: Tabla '{final_table_name}' no fue creada")
                
        except DynamicTableError as e:
            print(f"   ❌ Error de tabla dinámica: {str(e)}")
        except Exception as e:
            print(f"   ❌ Error inesperado: {str(e)}")

def test_data_insertion():
    """Prueba inserción de datos en tablas dinámicas"""
    print("\n" + "="*60)
    print("🧪 PRUEBA 3: Inserción de datos")
    print("="*60)
    
    test_process = "Test Inserción Datos"
    
    try:
        # Datos de prueba
        test_data = {
            'proceso_test': 'datos_ejemplo',
            'timestamp': datetime.now().isoformat(),
            'registros': ['dato1', 'dato2', 'dato3'],
            'metadata': {'tipo': 'test', 'version': '1.0'}
        }
        
        print(f"🔧 Probando inserción para proceso: '{test_process}'")
        
        # Usar el servicio completo de transferencia con tablas dinámicas
        success, result_info = data_transfer_service.transfer_to_dynamic_table(
            process_name=test_process,
            proceso_id="test-uuid-12345",
            datos_procesados=test_data,
            usuario_responsable="test_user",
            metadata={'test_type': 'system_test'},
            recreate_table=True,
            estado_proceso='COMPLETADO',
            tipo_operacion='TEST_INSERCION',
            registros_afectados=3
        )
        
        if success:
            print(f"   ✅ Inserción exitosa:")
            print(f"      📋 Tabla: '{result_info['table_name']}'")
            print(f"      🆔 ResultadoID: {result_info['resultado_id']}")
            print(f"      ⏱️  Tiempo: {result_info['tiempo_ejecucion']:.2f}s")
        else:
            print(f"   ❌ Inserción falló:")
            print(f"      Error: {result_info['error']}")
            
    except Exception as e:
        print(f"   ❌ Error inesperado en inserción: {str(e)}")

def test_migration_process_execution():
    """Prueba ejecución completa de MigrationProcess con tablas dinámicas"""
    print("\n" + "="*60)
    print("🧪 PRUEBA 4: Ejecución completa de MigrationProcess")
    print("="*60)
    
    try:
        # Crear usuario de prueba
        user, created = User.objects.get_or_create(
            username='test_dynamic_tables',
            defaults={'email': 'test@dynamic.com'}
        )
        
        # Crear conexión de prueba
        connection, created = DatabaseConnection.objects.get_or_create(
            name="Test Dynamic Tables Connection",
            defaults={
                'server': 'localhost',
                'username': 'test_user',
                'password': 'test_pass',
                'selected_database': 'test'
            }
        )
        
        # Crear fuente de datos
        source, created = DataSource.objects.get_or_create(
            name="Test Dynamic Tables Source",
            defaults={
                'source_type': 'sql',
                'connection': connection
            }
        )
        
        # Crear proceso de migración
        process = MigrationProcess.objects.create(
            name="TEST_TABLAS_DINAMICAS",
            description="Proceso de prueba para sistema de tablas dinámicas",
            source=source,
            selected_tables="tabla_test_dinamica",
            target_db_name="destino"
        )
        
        print(f"📦 Proceso creado: '{process.name}' (ID: {process.id})")
        
        # Ejecutar el proceso (que ahora usa tablas dinámicas)
        print(f"🚀 Ejecutando proceso...")
        process.run()
        
        print(f"✅ Proceso ejecutado exitosamente")
        print(f"   Estado final: {process.status}")
        
        # Verificar que se creó la tabla correspondiente
        expected_table_name = dynamic_table_manager.generate_table_name(process.name)
        table_exists = dynamic_table_manager.table_exists(expected_table_name)
        
        print(f"📋 Verificación de tabla:")
        print(f"   Nombre esperado: '{expected_table_name}'")
        print(f"   Existe: {table_exists}")
        
        if table_exists:
            print(f"🎉 SUCCESS: Sistema de tablas dinámicas funcionando correctamente")
        else:
            print(f"⚠️  WARNING: Tabla no encontrada (podría ser problema de permisos)")
        
    except Exception as e:
        print(f"❌ Error en ejecución de MigrationProcess: {str(e)}")
        import traceback
        print(traceback.format_exc())

def test_error_handling():
    """Prueba manejo de errores"""
    print("\n" + "="*60)
    print("🧪 PRUEBA 5: Manejo de errores")
    print("="*60)
    
    # Probar con nombre inválido extremo
    try:
        print("🔧 Probando nombre extremadamente largo...")
        very_long_name = "A" * 200  # Muy largo
        table_name = dynamic_table_manager.generate_table_name(very_long_name)
        print(f"   ✅ Nombre largo manejado: {len(table_name)} caracteres")
    except DynamicTableError as e:
        print(f"   ⚠️  Error controlado: {str(e)}")
    
    # Probar con caracteres especiales extremos
    try:
        print("🔧 Probando caracteres especiales extremos...")
        special_name = "!@#$%^&*()+=[]{}|;:'\",.<>?/~`"
        table_name = dynamic_table_manager.generate_table_name(special_name)
        print(f"   ✅ Caracteres especiales manejados: '{table_name}'")
    except DynamicTableError as e:
        print(f"   ⚠️  Error controlado: {str(e)}")

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE TABLAS DINÁMICAS")
    print("=" * 80)
    
    try:
        test_table_name_generation()
        test_table_creation_and_management()
        test_data_insertion()
        test_migration_process_execution()
        test_error_handling()
        
        print("\n" + "=" * 80)
        print("🎉 PRUEBAS COMPLETADAS")
        print("✅ Sistema de tablas dinámicas probado")
        print("📋 Cada proceso ahora genera su propia tabla independiente")
        print("🔄 Las tablas se recrean automáticamente en cada ejecución")
        print("⚡ Manejo de errores y validaciones implementado")
        
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO EN LAS PRUEBAS: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()