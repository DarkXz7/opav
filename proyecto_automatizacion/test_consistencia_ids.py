"""
TEST DE VALIDACIÓN: Verificar que los ProcesoIDs sean consistentes entre ProcesoLog y tablas dinámicas
"""

# Configurar Django
import os
import sys
import django
from datetime import datetime

# Configurar path y Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.db import connections
from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection
from automatizacion.logs.models_logs import ProcesoLog

def crear_proceso_de_prueba():
    """Crear un proceso de migración de prueba"""
    print("🏗️  Creando proceso de migración de prueba...")
    
    # Crear una fuente de datos ficticia
    data_source = DataSource.objects.create(
        name="Fuente de Prueba Consistencia",
        source_type="csv",
        file_path="datos_prueba.csv"
    )
    
    # Crear el proceso de migración
    proceso = MigrationProcess.objects.create(
        name="Test Consistencia IDs",
        description="Proceso para verificar consistencia de IDs entre ProcesoLog y tabla dinámica",
        source=data_source,
        selected_sheets=["hoja1"],
        selected_columns={"hoja1": ["col1", "col2"]},
        target_db_name="DestinoAutomatizacion",
        status="configured"
    )
    
    print(f"   ✅ Proceso creado - ID: {proceso.id}, Nombre: '{proceso.name}'")
    return proceso

def main():
    print("🔧 TEST DE CORRECCIÓN: Consistencia de IDs ProcesoLog ↔ Tabla Dinámica")
    print("=" * 80)
    
    # 1. Crear proceso de prueba
    proceso = crear_proceso_de_prueba()
    
    # 2. Obtener conteo inicial de logs
    logs_inicial = ProcesoLog.objects.using('logs').count()
    print(f"📊 Logs iniciales en ProcesoLog: {logs_inicial}")
    
    # 3. Ejecutar el proceso (esto debería crear logging automático)
    print(f"\n🚀 Ejecutando proceso '{proceso.name}'...")
    print(f"   🆔 MigrationProcess.id: {proceso.id}")
    
    try:
        proceso.run()
        print("   ✅ Proceso ejecutado sin errores")
    except Exception as e:
        print(f"   ❌ Error ejecutando proceso: {e}")
        return
    
    # 4. Verificar que se creó un log en ProcesoLog
    logs_final = ProcesoLog.objects.using('logs').count()
    nuevos_logs = logs_final - logs_inicial
    print(f"\n📊 Logs finales en ProcesoLog: {logs_final}")
    print(f"📊 Nuevos logs creados: {nuevos_logs}")
    
    if nuevos_logs == 0:
        print("❌ ERROR: No se crearon logs en ProcesoLog")
        return
    
    # 5. Buscar el log más reciente (debería ser el del proceso que acabamos de ejecutar)
    log_reciente = ProcesoLog.objects.using('logs').order_by('-LogID').first()
    
    if not log_reciente:
        print("❌ ERROR: No se encontró el log más reciente")
        return
        
    print(f"\n📋 LOG MÁS RECIENTE EN ProcesoLog:")
    print(f"   LogID: {log_reciente.LogID}")
    print(f"   ProcesoID: {log_reciente.ProcesoID}")
    print(f"   MigrationProcessID: {log_reciente.MigrationProcessID}")
    print(f"   NombreProceso: {log_reciente.NombreProceso}")
    print(f"   Estado: {log_reciente.Estado}")
    print(f"   FechaEjecucion: {log_reciente.FechaEjecucion}")
    
    # 6. Buscar en tabla dinámica con el mismo ProcesoID
    table_name = f"Proceso_{proceso.name.replace(' ', '')}"  # Patrón del generador de nombres
    proceso_id = log_reciente.ProcesoID
    
    print(f"\n🔍 BUSCANDO EN TABLA DINÁMICA: {table_name}")
    print(f"   Buscando ProcesoID: {proceso_id}")
    
    try:
        with connections['destino'].cursor() as cursor:
            # Primero verificar que la tabla existe
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = %s AND TABLE_TYPE = 'BASE TABLE'
            """, [table_name])
            
            tabla_existe = cursor.fetchone()[0] > 0
            
            if not tabla_existe:
                print(f"❌ ERROR: La tabla '{table_name}' no existe")
                return
            
            print(f"   ✅ Tabla '{table_name}' existe")
            
            # Buscar registros con el ProcesoID del log
            cursor.execute(f"""
                SELECT ResultadoID, ProcesoID, NombreProceso, EstadoProceso, FechaRegistro, UsuarioResponsable
                FROM [{table_name}]
                WHERE ProcesoID = %s
            """, [proceso_id])
            
            registros = cursor.fetchall()
            
            if not registros:
                print(f"❌ ERROR: No se encontraron registros en '{table_name}' con ProcesoID '{proceso_id}'")
                
                # Mostrar todos los ProcesoIDs en la tabla para debug
                cursor.execute(f"""
                    SELECT TOP 5 ResultadoID, ProcesoID, NombreProceso 
                    FROM [{table_name}] 
                    ORDER BY ResultadoID DESC
                """)
                
                todos_registros = cursor.fetchall()
                print(f"   📋 Últimos 5 registros en la tabla:")
                for reg in todos_registros:
                    print(f"      ResultadoID: {reg[0]}, ProcesoID: {reg[1]}, NombreProceso: {reg[2]}")
                return
            
            print(f"   ✅ Se encontraron {len(registros)} registros con ProcesoID coincidente")
            
            for i, registro in enumerate(registros, 1):
                resultado_id, tabla_proceso_id, tabla_nombre_proceso, tabla_estado, tabla_fecha, tabla_usuario = registro
                print(f"\n📊 REGISTRO {i} EN TABLA DINÁMICA:")
                print(f"   ResultadoID (PK): {resultado_id}")
                print(f"   ProcesoID: {tabla_proceso_id}")
                print(f"   NombreProceso: {tabla_nombre_proceso}")
                print(f"   EstadoProceso: {tabla_estado}")
                print(f"   FechaRegistro: {tabla_fecha}")
                print(f"   UsuarioResponsable: {tabla_usuario}")
                
                # ✅ VERIFICACIÓN CRÍTICA: ¿Coinciden los ProcesoIDs?
                if tabla_proceso_id == proceso_id:
                    print(f"   ✅ SUCCESS: ProcesoID coincide perfectamente")
                else:
                    print(f"   ❌ FALLA: ProcesoID no coincide")
                    print(f"      ProcesoLog.ProcesoID: {proceso_id}")
                    print(f"      Tabla.ProcesoID: {tabla_proceso_id}")
                
                # ✅ VERIFICACIÓN ADICIONAL: ¿Está el MigrationProcessID correcto?
                if log_reciente.MigrationProcessID == proceso.id:
                    print(f"   ✅ SUCCESS: MigrationProcessID correcto ({log_reciente.MigrationProcessID})")
                else:
                    print(f"   ❌ FALLA: MigrationProcessID incorrecto")
                    print(f"      Esperado: {proceso.id}")
                    print(f"      En log: {log_reciente.MigrationProcessID}")
            
    except Exception as e:
        print(f"❌ ERROR consultando tabla dinámica: {e}")
        return
    
    print(f"\n" + "=" * 80)
    print("🎯 RESULTADO FINAL:")
    
    if registros and registros[0][1] == proceso_id and log_reciente.MigrationProcessID == proceso.id:
        print("   ✅ CORRECCIÓN EXITOSA: Los IDs son consistentes")
        print(f"   - ProcesoLog.ProcesoID == Tabla.ProcesoID: {proceso_id}")
        print(f"   - ProcesoLog.MigrationProcessID: {log_reciente.MigrationProcessID}")
        print(f"   - MigrationProcess.id: {proceso.id}")
        print("   - ✅ Relación FK correcta entre ProcesoLog y MigrationProcess")
        print("   - ✅ UUID consistente entre ProcesoLog y tabla dinámica")
    else:
        print("   ❌ CORRECCIÓN INCOMPLETA: Los IDs NO son consistentes")
    
    print(f"\n🧹 Limpiando proceso de prueba...")
    proceso.source.delete()  # También elimina el proceso por CASCADE
    print("   ✅ Limpieza completada")

if __name__ == "__main__":
    main()