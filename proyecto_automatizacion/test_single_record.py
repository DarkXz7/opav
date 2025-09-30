"""
Script simple para verificar que el sistema optimizado funciona correctamente
"""

import os
import django
import sys

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.logs.process_tracker import ProcessTracker

def test_multiple_processes():
    print("="*60)
    print("PRUEBA DE MÚLTIPLES PROCESOS - UN REGISTRO POR PROCESO")
    print("="*60)
    
    # Contar registros antes
    from automatizacion.models_logs import ProcesoLog
    import pyodbc
    
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=LogsAutomatizacion;Trusted_Connection=yes;'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM ProcesoLog')
    count_before = cursor.fetchone()[0]
    print(f"Registros antes: {count_before}")
    
    # Crear 3 procesos diferentes
    processes = []
    
    for i in range(3):
        print(f"\n--- Proceso {i+1} ---")
        tracker = ProcessTracker(f"Proceso de prueba {i+1}")
        proceso_id = tracker.iniciar({'numero': i+1, 'tipo': 'prueba'})
        print(f"Iniciado: {proceso_id}")
        
        # Simular algunos estados
        tracker.actualizar_estado("Cargando", f"Cargando datos {i+1}")
        tracker.actualizar_estado("Validando", f"Validando datos {i+1}")
        tracker.actualizar_estado("Procesando", f"Procesando lote {i+1}")
        
        # Finalizar exitosamente
        tracker.finalizar_exito(f"Proceso {i+1} completado exitosamente")
        print(f"Completado: {proceso_id}")
        
        processes.append(proceso_id)
    
    # Contar registros después
    cursor.execute('SELECT COUNT(*) FROM ProcesoLog')
    count_after = cursor.fetchone()[0]
    print(f"\nRegistros después: {count_after}")
    print(f"Nuevos registros creados: {count_after - count_before}")
    
    # Verificar que cada proceso tiene su registro
    print(f"\nVerificando los {len(processes)} procesos creados:")
    for i, proceso_id in enumerate(processes):
        cursor.execute('SELECT LogID, ProcesoID, Estado, DuracionSegundos FROM ProcesoLog WHERE ProcesoID = ?', proceso_id)
        result = cursor.fetchone()
        if result:
            print(f"Proceso {i+1}: LogID={result[0]}, Estado={result[2]}, Duración={result[3]}s")
        else:
            print(f"❌ Proceso {i+1} NO encontrado!")
    
    conn.close()
    
    expected_new_records = len(processes)
    actual_new_records = count_after - count_before
    
    if actual_new_records == expected_new_records:
        print(f"\n✅ ÉXITO: Se crearon exactamente {expected_new_records} registros para {len(processes)} procesos")
    else:
        print(f"\n❌ ERROR: Se esperaban {expected_new_records} registros pero se crearon {actual_new_records}")

if __name__ == "__main__":
    test_multiple_processes()
