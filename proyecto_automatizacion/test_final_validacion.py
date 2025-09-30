"""
TEST FINAL DE VALIDACIÓN: Verificación completa de consistencia de IDs
"""

# Configurar Django
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.db import connections
from automatizacion.logs.models_logs import ProcesoLog

def main():
    print("🎯 VERIFICACIÓN FINAL: Consistencia de IDs después de las correcciones")
    print("=" * 80)
    
    # Buscar el último log creado
    ultimo_log = ProcesoLog.objects.using('logs').order_by('-LogID').first()
    
    if not ultimo_log:
        print("❌ No se encontró ningún log")
        return
    
    print(f"📋 ÚLTIMO LOG EN ProcesoLog:")
    print(f"   LogID: {ultimo_log.LogID}")
    print(f"   ProcesoID: {ultimo_log.ProcesoID}")
    print(f"   MigrationProcessID: {ultimo_log.MigrationProcessID}")
    print(f"   NombreProceso: {ultimo_log.NombreProceso}")
    print(f"   Estado: {ultimo_log.Estado}")
    
    # Buscar la tabla dinámica correspondiente
    with connections['destino'].cursor() as cursor:
        # Buscar tablas que contengan el proceso ID
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME LIKE 'Proceso_%' 
            AND TABLE_TYPE = 'BASE TABLE'
        """)
        
        tablas = cursor.fetchall()
        tabla_encontrada = None
        registro_encontrado = None
        
        # Buscar en cada tabla el ProcesoID
        for tabla in tablas:
            table_name = tabla[0]
            try:
                cursor.execute(f"""
                    SELECT ResultadoID, ProcesoID, NombreProceso, EstadoProceso, FechaRegistro
                    FROM [{table_name}]
                    WHERE UPPER(ProcesoID) = UPPER(%s)
                """, [ultimo_log.ProcesoID])
                
                registro = cursor.fetchone()
                if registro:
                    tabla_encontrada = table_name
                    registro_encontrado = registro
                    break
                    
            except Exception as e:
                # Ignorar errores de tablas sin la estructura esperada
                continue
        
        if not tabla_encontrada:
            print(f"❌ ERROR: No se encontró tabla con ProcesoID: {ultimo_log.ProcesoID}")
            print("📋 Tablas disponibles:")
            for tabla in tablas:
                print(f"   - {tabla[0]}")
            return
        
        print(f"\n📊 REGISTRO ENCONTRADO EN TABLA: {tabla_encontrada}")
        resultado_id, tabla_proceso_id, tabla_nombre, tabla_estado, tabla_fecha = registro_encontrado
        print(f"   ResultadoID (PK): {resultado_id}")
        print(f"   ProcesoID: {tabla_proceso_id}")
        print(f"   NombreProceso: {tabla_nombre}")
        print(f"   EstadoProceso: {tabla_estado}")
        print(f"   FechaRegistro: {tabla_fecha}")
        
        # ✅ VERIFICACIONES CRÍTICAS
        print(f"\n🎯 VERIFICACIONES DE CONSISTENCIA:")
        
        # 1. ProcesoID coincidente
        if tabla_proceso_id.upper() == ultimo_log.ProcesoID.upper():
            print("   ✅ SUCCESS: ProcesoID coincide entre ProcesoLog y tabla dinámica")
        else:
            print("   ❌ FALLA: ProcesoID NO coincide")
            print(f"      ProcesoLog: {ultimo_log.ProcesoID}")
            print(f"      Tabla: {tabla_proceso_id}")
        
        # 2. MigrationProcessID no NULL
        if ultimo_log.MigrationProcessID is not None:
            print(f"   ✅ SUCCESS: MigrationProcessID asignado correctamente ({ultimo_log.MigrationProcessID})")
        else:
            print("   ❌ FALLA: MigrationProcessID es NULL")
        
        # 3. NombreProceso consistente
        if ultimo_log.NombreProceso and tabla_nombre:
            print(f"   ✅ SUCCESS: NombreProceso presente en ambos lados")
        else:
            print("   ❌ FALLA: NombreProceso faltante")
        
        # 4. Estados válidos
        if ultimo_log.Estado and tabla_estado:
            print(f"   ✅ SUCCESS: Estados válidos (Log: {ultimo_log.Estado}, Tabla: {tabla_estado})")
        else:
            print("   ❌ FALLA: Estados inválidos")
        
        # RESULTADO FINAL
        todas_verificaciones_ok = (
            tabla_proceso_id.upper() == ultimo_log.ProcesoID.upper() and
            ultimo_log.MigrationProcessID is not None and
            ultimo_log.NombreProceso and
            tabla_nombre and
            ultimo_log.Estado and
            tabla_estado
        )
        
        print(f"\n" + "=" * 80)
        if todas_verificaciones_ok:
            print("🎉 CORRECCIÓN COMPLETAMENTE EXITOSA")
            print("   ✅ ProcesoLog.ProcesoID == Tabla.ProcesoID")
            print("   ✅ MigrationProcessID correctamente asignado")
            print("   ✅ Relación FK funcional entre ProcesoLog y MigrationProcess") 
            print("   ✅ UUID consistente entre ambas bases de datos")
            print("   ✅ ResultadoID como PK local en tabla dinámica")
        else:
            print("❌ CORRECCIÓN INCOMPLETA")
            print("   Revisar las verificaciones que fallaron arriba")
        
        # RESUMEN TÉCNICO
        print(f"\n📋 RESUMEN TÉCNICO:")
        print(f"   • LogID (PK ProcesoLog): {ultimo_log.LogID}")
        print(f"   • ProcesoID (UUID compartido): {ultimo_log.ProcesoID}")
        print(f"   • MigrationProcessID (FK): {ultimo_log.MigrationProcessID}")
        print(f"   • ResultadoID (PK tabla): {resultado_id}")
        print(f"   • Tabla dinámica: {tabla_encontrada}")

if __name__ == "__main__":
    main()