"""
Script para verificar que los procesos se están guardando en ResultadosProcesados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models_destino import ResultadosProcesados
from django.db import connections

def verificar_tabla_resultados():
    print("="*80)
    print("🔍 VERIFICACIÓN DE TABLA ResultadosProcesados")
    print("="*80)
    
    try:
        # 1. Verificar conexión a DestinoAutomatizacion
        print("\n1️⃣ Verificando conexión a DestinoAutomatizacion...")
        with connections['destino'].cursor() as cursor:
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()[0]
            print(f"   ✅ Conectado a: {db_name}")
        
        # 2. Verificar que la tabla existe
        print("\n2️⃣ Verificando existencia de tabla ResultadosProcesados...")
        with connections['destino'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'ResultadosProcesados'
            """)
            tabla_existe = cursor.fetchone()[0]
            
            if tabla_existe:
                print("   ✅ Tabla ResultadosProcesados existe")
            else:
                print("   ❌ Tabla ResultadosProcesados NO existe")
                print("   💡 Ejecuta el script SQL de creación primero")
                return False
        
        # 3. Ver estructura de la tabla
        print("\n3️⃣ Estructura de la tabla:")
        with connections['destino'].cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'ResultadosProcesados'
                ORDER BY ORDINAL_POSITION
            """)
            
            columnas = cursor.fetchall()
            print("   " + "-"*76)
            print(f"   {'Columna':<25} {'Tipo':<20} {'Longitud':<12} {'Nullable':<10}")
            print("   " + "-"*76)
            for col in columnas:
                col_name = col[0]
                data_type = col[1]
                max_length = col[2] if col[2] else 'N/A'
                nullable = 'Sí' if col[3] == 'YES' else 'No'
                print(f"   {col_name:<25} {data_type:<20} {str(max_length):<12} {nullable:<10}")
            print("   " + "-"*76)
        
        # 4. Contar registros actuales
        print("\n4️⃣ Registros actuales en ResultadosProcesados:")
        count = ResultadosProcesados.objects.using('destino').count()
        print(f"   📊 Total de registros: {count}")
        
        # 5. Mostrar últimos 5 registros (si existen)
        if count > 0:
            print("\n5️⃣ Últimos 5 registros:")
            ultimos = ResultadosProcesados.objects.using('destino').order_by('-ResultadoID')[:5]
            
            for resultado in ultimos:
                print(f"\n   🆔 ResultadoID: {resultado.ResultadoID}")
                print(f"   📝 Proceso: {resultado.NombreProceso}")
                print(f"   🔑 ProcesoID: {resultado.ProcesoID}")
                print(f"   ✅ Estado: {resultado.EstadoProceso}")
                print(f"   📊 Registros: {resultado.RegistrosAfectados}")
                print(f"   ⏱️  Tiempo: {resultado.TiempoEjecucion}s")
                print(f"   📅 Fecha: {resultado.FechaRegistro}")
                print(f"   👤 Usuario: {resultado.UsuarioResponsable}")
                
                # Mostrar datos procesados (JSON)
                import json
                try:
                    datos = json.loads(resultado.DatosProcesados)
                    print(f"   📦 Tabla destino: {datos.get('tabla_destino', 'N/A')}")
                    print(f"   📋 Columnas: {len(datos.get('campos_columnas', []))}")
                except:
                    pass
                print("   " + "-"*76)
        else:
            print("\n5️⃣ No hay registros aún")
            print("   💡 Ejecuta un proceso para que se guarde aquí")
        
        # 6. Verificar modelo Django
        print("\n6️⃣ Verificando modelo Django ResultadosProcesados...")
        print(f"   📋 Campos del modelo: {[f.name for f in ResultadosProcesados._meta.fields]}")
        print(f"   🔗 Base de datos configurada: destino")
        print(f"   📊 Tabla SQL: {ResultadosProcesados._meta.db_table}")
        
        print("\n" + "="*80)
        print("✅ VERIFICACIÓN COMPLETADA - TODO OK")
        print("="*80)
        print("\n💡 Instrucciones:")
        print("   1. Ejecuta un proceso de Excel desde la interfaz web")
        print("   2. Vuelve a ejecutar este script para ver el nuevo registro")
        print("   3. Cada ejecución creará un nuevo registro automáticamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = verificar_tabla_resultados()
    sys.exit(0 if exito else 1)
