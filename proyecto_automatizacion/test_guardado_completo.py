"""
Script de prueba completa: Ejecutar proceso y verificar guardado en ResultadosProcesados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from automatizacion.models_destino import ResultadosProcesados

def test_proceso_completo():
    print("="*80)
    print("🧪 TEST COMPLETO: Ejecutar Proceso y Verificar Guardado")
    print("="*80)
    
    # 1. Contar registros ANTES
    count_antes = ResultadosProcesados.objects.using('destino').count()
    print(f"\n1️⃣ Registros en ResultadosProcesados ANTES: {count_antes}")
    
    # 2. Buscar un proceso Excel configurado
    print("\n2️⃣ Buscando proceso Excel configurado...")
    procesos = MigrationProcess.objects.filter(
        source__source_type='excel',
        selected_sheets__isnull=False
    ).exclude(selected_sheets='[]').exclude(selected_sheets='')
    
    if not procesos.exists():
        print("   ❌ No hay procesos Excel configurados")
        print("   💡 Crea un proceso desde la interfaz web primero")
        return False
    
    proceso = procesos.first()
    print(f"   ✅ Proceso encontrado: '{proceso.name}' (ID: {proceso.id})")
    print(f"   📋 Hojas: {proceso.selected_sheets}")
    
    # 3. Ejecutar el proceso
    print(f"\n3️⃣ Ejecutando proceso '{proceso.name}'...")
    print("   ⏳ Procesando... (esto puede tomar unos segundos)")
    
    try:
        resultado = proceso.run()
        print(f"   ✅ Proceso ejecutado exitosamente")
        print(f"   📊 Mensaje: {resultado.get('message', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error ejecutando proceso: {e}")
        return False
    
    # 4. Contar registros DESPUÉS
    print(f"\n4️⃣ Verificando guardado en ResultadosProcesados...")
    count_despues = ResultadosProcesados.objects.using('destino').count()
    nuevos_registros = count_despues - count_antes
    
    print(f"   📊 Registros ANTES: {count_antes}")
    print(f"   📊 Registros DESPUÉS: {count_despues}")
    print(f"   📊 Nuevos registros: {nuevos_registros}")
    
    # 5. Mostrar detalles de los nuevos registros
    if nuevos_registros > 0:
        print(f"\n   ✅ ¡ÉXITO! Se crearon {nuevos_registros} registro(s)")
        print(f"\n5️⃣ Detalles de los nuevos registros:")
        
        # Obtener los últimos registros creados
        ultimos = ResultadosProcesados.objects.using('destino').order_by('-ResultadoID')[:nuevos_registros]
        
        for i, registro in enumerate(ultimos, 1):
            print(f"\n   📋 Registro #{i}:")
            print(f"      🆔 ResultadoID: {registro.ResultadoID}")
            print(f"      📝 NombreProceso: {registro.NombreProceso}")
            print(f"      🔑 ProcesoID: {registro.ProcesoID}")
            print(f"      ✅ Estado: {registro.EstadoProceso}")
            print(f"      📊 Registros Afectados: {registro.RegistrosAfectados}")
            print(f"      ⏱️  Tiempo Ejecución: {registro.TiempoEjecucion}s")
            print(f"      📅 Fecha: {registro.FechaRegistro}")
            print(f"      👤 Usuario: {registro.UsuarioResponsable}")
            print(f"      🔧 Tipo Operación: {registro.TipoOperacion}")
            
            # Mostrar datos procesados (JSON)
            import json
            try:
                datos = json.loads(registro.DatosProcesados)
                print(f"      📦 Tabla Destino: {datos.get('tabla_destino', 'N/A')}")
                print(f"      📋 Columnas: {datos.get('campos_columnas', [])}")
                print(f"      📊 Total Registros: {datos.get('total_registros_cargados', 0)}")
                print(f"      ⚡ Estado Final: {datos.get('estado_final', 'N/A')}")
            except Exception as e:
                print(f"      ⚠️ No se pudo parsear DatosProcesados: {e}")
            
            # Mostrar metadatos (JSON)
            try:
                metadatos = json.loads(registro.MetadatosProceso)
                print(f"      🔍 Metadatos:")
                print(f"         - Versión: {metadatos.get('version_proceso', 'N/A')}")
                print(f"         - Tabla Creada: {metadatos.get('tabla_creada', 'N/A')}")
                print(f"         - Columnas Procesadas: {metadatos.get('columnas_procesadas', 0)}")
                print(f"         - Hoja Origen: {metadatos.get('hoja_origen', 'N/A')}")
            except Exception as e:
                print(f"      ⚠️ No se pudo parsear MetadatosProceso: {e}")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("="*80)
        print("\n💡 Resumen:")
        print(f"   ✅ Proceso '{proceso.name}' ejecutado correctamente")
        print(f"   ✅ {nuevos_registros} registro(s) guardado(s) en ResultadosProcesados")
        print(f"   ✅ La integración está funcionando perfectamente")
        print("\n🎉 Ahora cada ejecución se registrará automáticamente en DestinoAutomatizacion")
        
        return True
        
    else:
        print(f"\n   ❌ NO se crearon registros en ResultadosProcesados")
        print(f"   ⚠️ Revisa los logs del proceso para ver si hubo errores")
        print(f"\n   💡 Posibles causas:")
        print(f"      - Error en la conexión a DestinoAutomatizacion")
        print(f"      - Error al guardar el registro (revisar permisos)")
        print(f"      - Excepción capturada pero no mostrada")
        
        return False

if __name__ == "__main__":
    exito = test_proceso_completo()
    sys.exit(0 if exito else 1)
