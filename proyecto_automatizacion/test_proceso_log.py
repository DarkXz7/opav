"""
Script de prueba para insertar y consultar datos en ProcesoLog
Este script utiliza el modelo ProcesoLog para:
1. Insertar un nuevo registro en la tabla ProcesoLog
2. Consultar todos los registros y mostrarlos

Para ejecutar este script:
python manage.py shell < test_proceso_log.py
"""

import os
import django
import sys
import datetime

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

# Importar el modelo ProcesoLog
from automatizacion.models_logs import ProcesoLog

print("="*80)
print("SCRIPT DE PRUEBA PARA PROCESO LOG EN SQL SERVER EXPRESS")
print("="*80)

try:
    # 1. Insertar un nuevo registro
    nuevo_log = ProcesoLog(
        FechaEjecucion=datetime.datetime.now(),
        Estado='Completado',
        ParametrosEntrada='{"fuente": "Test", "tipo": "Prueba"}',
        DuracionSegundos=2.5,
        ErrorDetalle=None
    )
    
    # Guardar el registro (utilizando la conexión 'logs')
    nuevo_log.save(using='logs')
    
    print(f"✓ Registro insertado correctamente: ID={nuevo_log.ProcesoID}")
    print(f"  - Fecha: {nuevo_log.FechaEjecucion}")
    print(f"  - Estado: {nuevo_log.Estado}")
    
    # 2. Consultar todos los registros
    print("\nConsultando todos los registros de ProcesoLog:")
    print("-" * 60)
    
    # Consulta utilizando la conexión 'logs'
    todos_logs = ProcesoLog.objects.using('logs').all()
    
    # Mostrar los registros
    if todos_logs:
        for log in todos_logs:
            print(f"ID: {log.ProcesoID} | Fecha: {log.FechaEjecucion} | Estado: {log.Estado}")
    else:
        print("No se encontraron registros en la tabla ProcesoLog")
    
    print("\n✓ Prueba completada exitosamente")
    
except Exception as e:
    print(f"\n❌ Error durante la prueba: {str(e)}")
    print(f"Tipo de error: {type(e).__name__}")
    
    # Información adicional para errores de conexión
    if "connection" in str(e).lower() or "sql" in str(e).lower():
        print("\nPosibles problemas de conexión:")
        print("1. Verifique que el servidor SQL Server Express esté ejecutándose")
        print("2. Confirme que el usuario y contraseña sean correctos")
        print("3. Verifique que la base de datos 'LogsAutomatizacion' existe")
        print("4. Confirme que la tabla 'ProcesoLog' existe y tiene la estructura esperada")

print("\n" + "="*80)
