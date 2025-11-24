"""
Script para verificar que los procesos ejecutados se guarden en ResultadosProcesados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from automatizacion.models_destino import ResultadosProcesados
from django.db import connection

def main():
    print("="*80)
    print("🧪 TEST: Verificar guardado en ResultadosProcesados")
    print("="*80)
    
    # 1. Contar registros actuales en ResultadosProcesados
    try:
        count_antes = ResultadosProcesados.objects.using('destino').count()
        print(f"\n1️⃣ Registros actuales en ResultadosProcesados: {count_antes}")
    except Exception as e:
        print(f"❌ Error consultando ResultadosProcesados: {e}")
        return
    
    # 2. Buscar un proceso Excel configurado
    print("\n2️⃣ Buscando proceso Excel configurado...")
    procesos_excel = MigrationProcess.objects.filter(
        source__source_type='excel',
        selected_sheets__isnull=False
    ).exclude(selected_sheets='[]').exclude(selected_sheets='')
    
    if not procesos_excel.exists():
        print("❌ No se encontraron procesos Excel configurados")
        return
    
    proceso = procesos_excel.first()
    print(f"   ✅ Proceso encontrado: {proceso.name} (ID: {proceso.id})")
    print(f"   📋 Hojas seleccionadas: {proceso.selected_sheets}")
    
    # 3. Ejecutar el proceso
    print(f"\n3️⃣ Ejecutando proceso '{proceso.name}'...")
    print("   ⏳ Esto puede tomar unos momentos...")
    
    try:
        resultado = proceso.run()
        print(f"   ✅ Proceso ejecutado")
        print(f"   📊 Resultado: {resultado.get('message', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error ejecutando proceso: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Verificar si se crearon registros en ResultadosProcesados
    print("\n4️⃣ Verificando registros en ResultadosProcesados...")
    
    try:
        count_despues = ResultadosProcesados.objects.using('destino').count()
        nuevos_registros = count_despues - count_antes
        
        print(f"   📊 Registros antes: {count_antes}")
        print(f"   📊 Registros después: {count_despues}")
        print(f"   📊 Nuevos registros: {nuevos_registros}")
        
        if nuevos_registros > 0:
            print(f"\n   ✅ ¡ÉXITO! Se crearon {nuevos_registros} registro(s) en ResultadosProcesados")
            
            # Mostrar últimos registros
            ultimos = ResultadosProcesados.objects.using('destino').order_by('-ResultadoID')[:nuevos_registros]
            
            print("\n   📋 Detalles de los nuevos registros:")
            for registro in ultimos:
                print(f"\n      🆔 ResultadoID: {registro.ResultadoID}")
                print(f"      📝 NombreProceso: {registro.NombreProceso}")
                print(f"      🔑 ProcesoID: {registro.ProcesoID}")
                print(f"      ✅ Estado: {registro.EstadoProceso}")
                print(f"      📊 Registros Afectados: {registro.RegistrosAfectados}")
                print(f"      🕐 Fecha: {registro.FechaRegistro}")
                print(f"      👤 Usuario: {registro.UsuarioResponsable}")
                
                import json
                try:
                    datos = json.loads(registro.DatosProcesados)
                    print(f"      📦 Tabla Destino: {datos.get('tabla_destino', 'N/A')}")
                    print(f"      📋 Columnas: {len(datos.get('campos_columnas', []))}")
                except:
                    pass
        else:
            print(f"\n   ❌ NO se crearon registros en ResultadosProcesados")
            print(f"   ⚠️ El problema persiste")
            
    except Exception as e:
        print(f"   ❌ Error verificando ResultadosProcesados: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("🏁 TEST COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    main()
