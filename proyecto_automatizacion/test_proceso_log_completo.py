"""
Script de prueba completo para ProcesoLog y ProcesoLogger
Este script demuestra:
1. Inserción de registros directos en ProcesoLog
2. Uso de ProcesoLogger para registro de eventos de proceso
3. Consulta y visualización de datos en la tabla ProcesoLog

Para ejecutar este script:
python manage.py shell < test_proceso_log_completo.py
"""

import os
import django
import sys
import datetime
import time
import traceback

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

# Importar el modelo ProcesoLog y utilidades
from automatizacion.models_logs import ProcesoLog
from automatizacion.logs.utils import ProcesoLogger, registrar_evento

print("="*80)
print("PRUEBA COMPLETA PARA PROCESO LOG EN SQL SERVER EXPRESS")
print("="*80)

try:
    print("\n1. INSERCIÓN DIRECTA DE UN REGISTRO")
    print("-" * 60)
    
    # Insertar un registro directamente
    nuevo_log = ProcesoLog(
        # ProcesoID se generará automáticamente con NEWID() en SQL Server
        FechaEjecucion=datetime.datetime.now(),
        Estado='Test directo',  # Máx 20 caracteres
        ParametrosEntrada='{"tipo": "prueba_directa", "origen": "test_script"}',
        DuracionSegundos=1,  # Entero
        MensajeError=None
    )
    
    # Guardar el registro (utilizando la conexión 'logs')
    nuevo_log.save(using='logs')
    
    print(f"✓ Registro insertado correctamente: ID={nuevo_log.ProcesoID}")
    
    print("\n2. USO DE ProcesoLogger PARA UN PROCESO SIMULADO")
    print("-" * 60)
    
    # Simular un proceso completo con logger
    print("Iniciando proceso simulado...")
    logger = ProcesoLogger("Proceso de prueba")
    
    # Registrar inicio
    proceso_id = logger.iniciar(parametros={"modo": "test", "simulacion": True})
    print(f"✓ Proceso iniciado: ID={proceso_id}")
    
    # Simular trabajo
    print("Ejecutando proceso (simulación 2 segundos)...")
    time.sleep(2)
    
    # Registrar finalización exitosa
    logger.finalizar_exito("Proceso completado correctamente")
    print(f"✓ Proceso finalizado con éxito: ID={proceso_id}")
    
    print("\n3. SIMULACIÓN DE PROCESO CON ERROR")
    print("-" * 60)
    
    # Simular un proceso con error
    print("Iniciando proceso que fallará...")
    logger_error = ProcesoLogger("Proceso con error")
    
    # Registrar inicio
    proceso_error_id = logger_error.iniciar(parametros={"modo": "error_test"})
    print(f"✓ Proceso iniciado: ID={proceso_error_id}")
    
    # Simular trabajo
    print("Ejecutando proceso (simulación 1 segundo)...")
    time.sleep(1)
    
    # Registrar error
    logger_error.finalizar_error("Error simulado para pruebas")
    print(f"✓ Proceso finalizado con error (simulado): ID={proceso_error_id}")
    
    print("\n4. REGISTRO DE EVENTO SIMPLE")
    print("-" * 60)
    
    # Utilizar la función auxiliar para registro simple
    evento_id = registrar_evento(
        nombre_evento="Evento de prueba", 
        estado="Notificación", 
        parametros={"origen": "script_test", "prioridad": "baja"}
    )
    print(f"✓ Evento registrado: ID={evento_id}")
    
    print("\n5. CONSULTANDO TODOS LOS REGISTROS")
    print("-" * 60)
    
    # Consulta utilizando la conexión 'logs'
    todos_logs = ProcesoLog.objects.using('logs').all().order_by('-FechaEjecucion')
    
    # Mostrar los registros
    if todos_logs:
        print(f"Encontrados {todos_logs.count()} registros:")
        for log in todos_logs[:10]:  # Mostrar solo los primeros 10
            print(f"ID: {log.ProcesoID} | Fecha: {log.FechaEjecucion.strftime('%Y-%m-%d %H:%M:%S')} | Estado: {log.Estado}")
            if log.ParametrosEntrada:
                print(f"  Parámetros: {log.ParametrosEntrada[:50]}..." if len(log.ParametrosEntrada) > 50 else f"  Parámetros: {log.ParametrosEntrada}")
            if log.ErrorDetalle:
                print(f"  Error: {log.ErrorDetalle[:50]}..." if len(log.ErrorDetalle) > 50 else f"  Error: {log.ErrorDetalle}")
            print("-" * 40)
    else:
        print("No se encontraron registros en la tabla ProcesoLog")
    
    print("\n✓ Prueba completada exitosamente")
    
except Exception as e:
    print(f"\n❌ Error durante la prueba: {str(e)}")
    print(f"Tipo de error: {type(e).__name__}")
    print(f"Detalles: {traceback.format_exc()}")
    
    # Información adicional para errores de conexión
    if "connection" in str(e).lower() or "sql" in str(e).lower():
        print("\nPosibles problemas de conexión:")
        print("1. Verifique que el servidor SQL Server Express esté ejecutándose")
        print("2. Confirme que el usuario y contraseña sean correctos")
        print("3. Verifique que la base de datos 'LogsAutomatizacion' existe")
        print("4. Confirme que la tabla 'ProcesoLog' existe y tiene la estructura esperada")
        print("\nComando para verificar tabla:")
        print("USE LogsAutomatizacion;")
        print("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ProcesoLog';")
        
        print("\nComando para crear tabla si no existe:")
        print("USE LogsAutomatizacion;")
        print("IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ProcesoLog')")
        print("CREATE TABLE ProcesoLog (")
        print("    ProcesoID INT IDENTITY(1,1) PRIMARY KEY,")
        print("    FechaEjecucion DATETIME NOT NULL,")
        print("    Estado VARCHAR(100) NOT NULL,")
        print("    ParametrosEntrada NVARCHAR(MAX) NULL,")
        print("    DuracionSegundos FLOAT NULL,")
        print("    ErrorDetalle NVARCHAR(MAX) NULL")
        print(");")

print("\n" + "="*80)
