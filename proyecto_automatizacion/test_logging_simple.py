#!/usr/bin/env python
"""
Test simple del sistema de logging sin usar Django Test Client
"""
import os
import django
import pyodbc
from datetime import datetime

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def test_sql_server_connection():
    """Test directo de conexión a SQL Server"""
    print("=== TEST CONEXIÓN SQL SERVER ===")
    try:
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=LogsAutomatizacion;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Verificar tabla
        cursor.execute("SELECT COUNT(*) FROM ProcesoLog")
        count = cursor.fetchone()[0]
        print(f"✓ Conexión exitosa. Total logs: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT TOP 3 LogID, ProcesoID, NombreProceso, Estado, FechaEjecucion 
                FROM ProcesoLog 
                ORDER BY FechaEjecucion DESC
            """)
            
            print("\nÚltimos logs:")
            for row in cursor.fetchall():
                print(f"  LogID: {row[0]}, ProcesoID: {row[1][:8]}..., Nombre: {row[2]}, Estado: {row[3]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_process_tracker():
    """Test directo del ProcessTracker"""
    print("\n=== TEST PROCESS TRACKER ===")
    try:
        from automatizacion.logs.process_tracker import ProcessTracker
        
        # Crear proceso de prueba
        proceso_nombre = f"Test ProcessTracker {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"Creando proceso: {proceso_nombre}")
        tracker = ProcessTracker(proceso_nombre)
        
        print(f"ProcesoID generado: {tracker.proceso_id}")
        
        # Usar los métodos correctos del ProcessTracker
        proceso_id = tracker.iniciar({"test": "parametros"})
        print(f"Proceso iniciado con ID: {proceso_id}")
        
        tracker.actualizar_estado("EN_PROGRESO", "Procesando datos...")
        print("Estado actualizado a EN_PROGRESO")
        
        tracker.finalizar_exito("Proceso completado exitosamente")
        print("Proceso finalizado exitosamente")
        
        print("✓ ProcessTracker ejecutado correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error en ProcessTracker: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_logger():
    """Test directo del web logger"""
    print("\n=== TEST WEB LOGGER ===")
    try:
        from automatizacion.web_logger_optimized import registrar_proceso_web, finalizar_proceso_web
        from django.contrib.auth.models import User
        
        proceso_nombre = f"Test WebLogger {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        parametros = {
            'name': proceso_nombre,
            'description': 'Test desde web logger',
            'source_id': 1,
            'selected_sheets': ['Hoja1'],
            'target_db': 'test'
        }
        
        # Crear o obtener un usuario de prueba
        user, created = User.objects.get_or_create(
            username='testuser', 
            defaults={'email': 'test@test.com'}
        )
        
        print(f"Registrando proceso web: {proceso_nombre}")
        # Usar la función con usuario correcto
        tracker, proceso_id = registrar_proceso_web(proceso_nombre, user, parametros)
        print(f"ProcesoID: {proceso_id}")
        
        # Finalizar proceso
        finalizar_proceso_web(tracker, user, exito=True, detalles="Proceso completado exitosamente")
        
        print("✓ WebLogger ejecutado correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error en WebLogger: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_logs_created():
    """Verificar que se crearon los logs"""
    print("\n=== VERIFICACIÓN FINAL ===")
    try:
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=LogsAutomatizacion;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Contar logs recientes (últimos 10 minutos)
        cursor.execute("""
            SELECT COUNT(*) FROM ProcesoLog 
            WHERE FechaEjecucion >= DATEADD(MINUTE, -10, GETDATE())
        """)
        recent_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT LogID, ProcesoID, NombreProceso, Estado, FechaEjecucion 
            FROM ProcesoLog 
            WHERE FechaEjecucion >= DATEADD(MINUTE, -10, GETDATE())
            ORDER BY FechaEjecucion DESC
        """)
        
        print(f"Logs creados en los últimos 10 minutos: {recent_count}")
        if recent_count > 0:
            print("\nLogs recientes:")
            for row in cursor.fetchall():
                print(f"  {row[4]} - {row[2]} ({row[3]})")
        
        cursor.close()
        conn.close()
        return recent_count > 0
        
    except Exception as e:
        print(f"✗ Error verificando logs: {e}")
        return False

if __name__ == "__main__":
    print("INICIANDO TESTS DE LOGGING")
    print("=" * 50)
    
    # Ejecutar tests
    results = []
    results.append(test_sql_server_connection())
    results.append(test_process_tracker())
    results.append(test_web_logger())
    results.append(verify_logs_created())
    
    print("\n" + "=" * 50)
    print("RESUMEN DE TESTS:")
    tests = ["Conexión SQL Server", "ProcessTracker", "WebLogger", "Verificación Logs"]
    for i, result in enumerate(results):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {tests[i]}: {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\nTasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 Todos los tests pasaron correctamente!")
    else:
        print("⚠️  Algunos tests fallaron. Revisar la configuración.")
