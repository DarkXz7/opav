"""
Script para probar ejecución completa de MigrationProcess
"""

from django.contrib.auth.models import User
from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection
from automatizacion.models_destino import ResultadosProcesados

print("🧪 Prueba de ejecución completa de MigrationProcess...")

# Crear usuario de prueba
user, created = User.objects.get_or_create(
    username='test_migration',
    defaults={'email': 'test@migration.com'}
)

# Contar registros antes
destino_antes = ResultadosProcesados.objects.using('destino').count()
print(f"📊 Antes - DestinoAutomatizacion: {destino_antes} registros")

# Crear conexión y proceso si no existen
connection, created = DatabaseConnection.objects.get_or_create(
    name="Test Connection",
    defaults={
        'server': 'localhost',
        'username': 'test_user',
        'password': 'test_pass',
        'selected_database': 'test'
    }
)

source, created = DataSource.objects.get_or_create(
    name="Test Source",
    defaults={
        'source_type': 'sql',
        'connection': connection
    }
)

# Crear proceso
process = MigrationProcess.objects.create(
    name="TEST_MIGRACION_COMPLETA",
    description="Proceso de prueba para inserción en destino",
    source=source,
    selected_tables="tabla_test",
    target_db_name="destino"
)

print(f"📦 Proceso creado: {process.name} (ID: {process.id})")

try:
    # Ejecutar el proceso
    process.run()
    print(f"✅ Proceso ejecutado exitosamente")
    
    # Verificar inserción en destino
    destino_despues = ResultadosProcesados.objects.using('destino').count()
    print(f"📊 Después - DestinoAutomatizacion: {destino_despues} registros")
    
    if destino_despues > destino_antes:
        print(f"✅ Se insertaron {destino_despues - destino_antes} registros nuevos")
        
        # Mostrar el último registro
        ultimo = ResultadosProcesados.objects.using('destino').order_by('-ResultadoID').first()
        if ultimo:
            print(f"📋 Último registro:")
            print(f"   ID: {ultimo.ResultadoID}")
            print(f"   Estado: {ultimo.Estado}")
            print(f"   Tipo: {ultimo.Tipo}")
            print(f"   Proceso: {ultimo.ProcesoID}")
    else:
        print("❌ No se insertaron registros nuevos")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("🏁 Prueba completada")