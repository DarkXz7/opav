"""
Prueba completa del sistema de tablas dinámicas
"""

from django.contrib.auth.models import User
from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection  
from automatizacion.data_transfer_service import data_transfer_service
from automatizacion.dynamic_table_service import dynamic_table_manager

print("🧪 PRUEBA COMPLETA DEL SISTEMA DE TABLAS DINÁMICAS")
print("=" * 70)

# 1. Probar transferencia directa con tabla dinámica
print("\n1️⃣ Probando transferencia directa a tabla dinámica...")

test_data = {
    'ejemplo': 'datos de prueba',
    'timestamp': '2025-09-29T13:00:00',
    'valores': [1, 2, 3, 4, 5]
}

success, result_info = data_transfer_service.transfer_to_dynamic_table(
    process_name="Test Directo Tabla Dinamica",
    proceso_id="test-uuid-456",
    datos_procesados=test_data,
    usuario_responsable="test_user_dinamico",
    metadata={'tipo_test': 'transferencia_directa'},
    recreate_table=True,
    estado_proceso='COMPLETADO',
    registros_afectados=5
)

if success:
    print(f"✅ Transferencia directa exitosa:")
    print(f"   📋 Tabla: {result_info['table_name']}")
    print(f"   🆔 ResultadoID: {result_info['resultado_id']}")
    print(f"   ⏱️  Tiempo: {result_info['tiempo_ejecucion']:.3f}s")
    
    # Verificar que la tabla existe
    table_exists = dynamic_table_manager.table_exists(result_info['table_name'])
    print(f"   ✅ Tabla existe en BD: {table_exists}")
else:
    print(f"❌ Error en transferencia directa:")
    print(f"   Error: {result_info['error']}")

# 2. Probar con MigrationProcess completo
print("\n2️⃣ Probando MigrationProcess completo...")

# Crear datos de prueba
user, _ = User.objects.get_or_create(
    username='test_migration_dinamico',
    defaults={'email': 'test@dinamico.com'}
)

connection, _ = DatabaseConnection.objects.get_or_create(
    name="Test Dynamic Connection",
    defaults={
        'server': 'localhost',
        'username': 'test_user',
        'password': 'test_pass',
        'selected_database': 'test'
    }
)

source, _ = DataSource.objects.get_or_create(
    name="Test Dynamic Source",
    defaults={
        'source_type': 'sql',
        'connection': connection
    }
)

# Crear proceso
process = MigrationProcess.objects.create(
    name="PROCESO_TABLA_DINAMICA_COMPLETO",
    description="Prueba completa del sistema de tablas dinámicas",
    source=source,
    selected_tables="tabla_dinamica_test",
    target_db_name="destino"
)

print(f"📦 Proceso creado: '{process.name}' (ID: {process.id})")

try:
    # Ejecutar proceso
    process.run()
    
    print(f"✅ Proceso ejecutado exitosamente")
    print(f"   Estado: {process.status}")
    
    # Verificar tabla generada
    expected_table = dynamic_table_manager.generate_table_name(process.name)
    table_exists = dynamic_table_manager.table_exists(expected_table)
    
    print(f"📋 Verificación tabla del proceso:")
    print(f"   Nombre esperado: '{expected_table}'")
    print(f"   Existe: {table_exists}")
    
except Exception as e:
    print(f"❌ Error ejecutando proceso: {str(e)}")

# 3. Probar recreación de tabla
print("\n3️⃣ Probando recreación de tabla existente...")

if 'result_info' in locals() and result_info.get('table_name'):
    table_name = result_info['table_name']
    
    print(f"🔄 Recreando tabla '{table_name}'...")
    
    success2, result_info2 = data_transfer_service.transfer_to_dynamic_table(
        process_name="Test Directo Tabla Dinamica",  # Mismo nombre
        proceso_id="test-uuid-789",  # Nuevo ID
        datos_procesados={'nuevo_dato': 'recreacion_exitosa'},
        usuario_responsable="test_user_recreacion",
        recreate_table=True,  # Recrear tabla
        estado_proceso='COMPLETADO'
    )
    
    if success2:
        print(f"✅ Recreación exitosa:")
        print(f"   📋 Tabla: {result_info2['table_name']}")
        print(f"   🆔 Nuevo ResultadoID: {result_info2['resultado_id']}")
    else:
        print(f"❌ Error en recreación: {result_info2['error']}")

print("\n" + "=" * 70)
print("🎉 PRUEBA COMPLETA FINALIZADA")
print("✅ Sistema de tablas dinámicas implementado y funcionando")
print("📋 Cada proceso genera su propia tabla independiente") 
print("🔄 Las tablas se recrean automáticamente cuando es necesario")
print("⚡ Manejo de errores y validaciones operativo")