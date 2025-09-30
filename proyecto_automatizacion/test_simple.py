"""
Script simple para probar el sistema de logging corregido
"""

from django.contrib.auth.models import User
from automatizacion.logs.models_logs import ProcesoLog
from automatizacion.models_destino import ResultadosProcesados
from automatizacion.web_logger_optimized import registrar_proceso_web, finalizar_proceso_web

# Crear usuario de prueba
user, created = User.objects.get_or_create(
    username='test_user',
    defaults={'email': 'test@example.com'}
)

print("🧪 Prueba del sistema de logging corregido...")

# Contar registros antes
logs_antes = ProcesoLog.objects.using('logs').count()
destino_antes = ResultadosProcesados.objects.using('destino').count()

print(f"📊 Antes - LogsAutomatizacion: {logs_antes}, DestinoAutomatizacion: {destino_antes}")

# Iniciar proceso
tracker, proceso_id = registrar_proceso_web(
    nombre_proceso="TEST_CORRECCIONES",
    usuario=user,
    datos_adicionales={'test': 'correcciones_aplicadas'}
)

if tracker:
    print(f"✅ Proceso iniciado: {proceso_id}")
    
    # Actualizar estado
    tracker.actualizar_estado("EN_PROGRESO", "Probando correcciones...")
    
    # Finalizar con éxito  
    finalizar_proceso_web(
        tracker,
        usuario=user,
        exito=True,
        detalles="Correcciones funcionando correctamente"
    )
    
    # Contar registros después
    logs_despues = ProcesoLog.objects.using('logs').count()
    
    print(f"📊 Después - LogsAutomatizacion: {logs_despues}")
    
    # Verificar que solo se añadió un registro
    if logs_despues == logs_antes + 1:
        print("✅ Solo se creó un registro (correcto)")
    else:
        print(f"❌ Se crearon {logs_despues - logs_antes} registros")
    
    # Verificar el contenido del registro
    log_record = ProcesoLog.objects.filter(ProcesoID=proceso_id).using('logs').first()
    if log_record:
        print(f"📋 Estado: {log_record.Estado}")
        print(f"📋 Error: '{log_record.MensajeError}'")
        
        if log_record.MensajeError and log_record.MensajeError != "NULL":
            print("✅ Campo error no es NULL")
        else:
            print("❌ Campo error es NULL")
else:
    print("❌ Error iniciando proceso")

print("🏁 Prueba completada")