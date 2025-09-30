"""
Script para probar que el guardado inicial solo cree un registro único
en ProcesoLog durante todo el flujo de guardado
"""

import json
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.http import HttpRequest
from automatizacion.models import DatabaseConnection, DataSource
from automatizacion.logs.models_logs import ProcesoLog
from automatizacion.views import save_process

print("🧪 Prueba: Solo un registro en guardado inicial")
print("=" * 60)

# Crear usuario de prueba
user, created = User.objects.get_or_create(
    username='test_guardado',
    defaults={'email': 'test@guardado.com'}
)

# Contar registros antes del flujo
logs_antes = ProcesoLog.objects.using('logs').count()
print(f"📊 Registros ANTES del guardado: {logs_antes}")

# Crear conexión y fuente de datos de prueba
connection = DatabaseConnection.objects.create(
    name="Conexión Test Guardado",
    server="localhost",
    username="test_user",
    password="test_pass",
    selected_database="TestDB"
)

source = DataSource.objects.create(
    name="Fuente Test Guardado",
    source_type="sql",
    connection=connection
)

# Simular la llamada a save_process (que es la única que debe crear logs)
factory = RequestFactory()

# Datos del proceso como los enviaría el frontend
process_data = {
    'name': 'TEST_GUARDADO_UNICO',
    'description': 'Proceso de prueba para verificar logging único',
    'source_id': source.id,
    'selected_database': 'DestinoAutomatizacion',
    'selected_tables': ['dbo.TestTable'],
    'selected_columns': {'dbo.TestTable': ['col1', 'col2', 'col3']},
    'target_db': 'destino'
}

# Crear request POST con los datos
request = factory.post(
    '/automatizacion/api/save_process/',
    data=json.dumps(process_data),
    content_type='application/json'
)
request.user = user

print(f"🎯 Ejecutando save_process...")

try:
    # Ejecutar save_process
    response = save_process(request)
    
    if hasattr(response, 'status_code') and response.status_code == 200:
        print(f"✅ save_process ejecutado exitosamente")
        
        # Contar registros después
        logs_despues = ProcesoLog.objects.using('logs').count()
        print(f"📊 Registros DESPUÉS del guardado: {logs_despues}")
        
        # Verificar que solo se añadió un registro
        diferencia = logs_despues - logs_antes
        
        if diferencia == 1:
            print(f"✅ PERFECTO: Solo se creó {diferencia} registro (correcto)")
            
            # Verificar el contenido del registro
            ultimo_log = ProcesoLog.objects.using('logs').order_by('-FechaEjecucion').first()
            if ultimo_log and 'TEST_GUARDADO_UNICO' in ultimo_log.NombreProceso:
                print(f"📋 Registro creado:")
                print(f"   Proceso: {ultimo_log.NombreProceso}")
                print(f"   Estado: {ultimo_log.Estado}")
                print(f"   Error: '{ultimo_log.MensajeError}'")
                
                if ultimo_log.MensajeError and 'exitosamente' in ultimo_log.MensajeError:
                    print(f"✅ Mensaje correcto y no NULL")
                else:
                    print(f"❌ Mensaje incorrecto o NULL")
            else:
                print(f"❌ No se encontró el registro esperado")
                
        elif diferencia == 0:
            print(f"❌ No se creó ningún registro")
        else:
            print(f"❌ Se crearon {diferencia} registros (debería ser solo 1)")
            
            # Mostrar los últimos registros para debug
            ultimos_logs = ProcesoLog.objects.using('logs').order_by('-FechaEjecucion')[:diferencia]
            for i, log in enumerate(ultimos_logs, 1):
                print(f"   {i}. {log.NombreProceso} | {log.Estado}")
    else:
        print(f"❌ Error en save_process: {response.status_code if hasattr(response, 'status_code') else 'No status'}")
        
except Exception as e:
    print(f"❌ Excepción en la prueba: {str(e)}")
    import traceback
    print(traceback.format_exc())

print("\n" + "=" * 60)
print("🏁 Prueba completada")

# Limpiar datos de prueba
try:
    source.delete()
    connection.delete()
    print("🧹 Datos de prueba limpiados")
except:
    pass