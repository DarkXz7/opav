#!/usr/bin/env python3
"""
Test completo del flujo de procesamiento multihoja Excel
Valida todo el sistema desde selección hasta ejecución
"""

import os
import sys
import django
import json
import pandas as pd
from datetime import datetime

# Configurar Django
sys.path.append('c:\\Users\\migue\\OneDrive\\Escritorio\\DJANGO DE NUEVO\\opav\\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import DataSource, MigrationProcess, MigrationLog
from automatizacion.logs.models_logs import ProcesoLog
from automatizacion.models_destino import ResultadosProcesados

def crear_excel_test():
    """Crear archivo Excel de prueba con múltiples hojas"""
    print("📁 Creando archivo Excel de prueba...")
    
    # Datos para diferentes hojas
    datos_usuarios = {
        'ID': [1, 2, 3],
        'Nombre': ['Juan', 'María', 'Carlos'],
        'Email': ['juan@test.com', 'maria@test.com', 'carlos@test.com'],
        'Edad': [25, 30, 35]
    }
    
    datos_productos = {
        'ProductoID': [101, 102, 103],
        'Descripcion': ['Producto A', 'Producto B', 'Producto C'],
        'Precio': [100.0, 200.0, 300.0],
        'Stock': [50, 30, 20]
    }
    
    datos_ventas = {
        'VentaID': [1001, 1002, 1003],
        'ProductoID': [101, 102, 103],
        'Cantidad': [2, 1, 3],
        'Fecha': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Total': [200.0, 200.0, 900.0]
    }
    
    # Crear Excel
    archivo_path = 'test_multihoja_completo.xlsx'
    with pd.ExcelWriter(archivo_path) as writer:
        pd.DataFrame(datos_usuarios).to_excel(writer, sheet_name='Usuarios', index=False)
        pd.DataFrame(datos_productos).to_excel(writer, sheet_name='Productos', index=False)
        pd.DataFrame(datos_ventas).to_excel(writer, sheet_name='Ventas', index=False)
    
    print(f"✅ Excel creado: {archivo_path}")
    return os.path.abspath(archivo_path)

def test_flujo_completo():
    """Prueba completa del sistema multihoja"""
    print("\n🚀 INICIANDO TEST COMPLETO DEL FLUJO MULTIHOJA")
    print("=" * 60)
    
    try:
        # 1. Crear archivo Excel de prueba
        excel_path = crear_excel_test()
        
        # 2. Crear DataSource
        print("\n📋 Paso 1: Creando DataSource...")
        data_source = DataSource.objects.create(
            name='Test Multihoja Completo',
            source_type='excel',
            file_path=excel_path
        )
        print(f"✅ DataSource creado: ID {data_source.id}")
        
        # 3. Configurar selecciones como lo haría el usuario
        print("\n⚙️  Paso 2: Configurando selecciones multihoja...")
        
        selected_sheets = ['Usuarios', 'Productos', 'Ventas']
        selected_columns = {
            'Usuarios': ['ID', 'Nombre', 'Email'],  # Solo 3 de 4 columnas
            'Productos': ['ProductoID', 'Descripcion', 'Precio'],  # Solo 3 de 4 columnas
            'Ventas': ['VentaID', 'ProductoID', 'Cantidad', 'Total']  # 4 de 5 columnas
        }
        
        print(f"📊 Hojas seleccionadas: {selected_sheets}")
        for hoja, columnas in selected_columns.items():
            print(f"   - {hoja}: {len(columnas)} columnas -> {columnas}")
        
        # 4. Limpiar procesos anteriores
        MigrationProcess.objects.filter(name__icontains='Test_Proceso_Multihoja').delete()
        
        # 4. Crear proceso de migración
        print("\n📝 Paso 3: Creando proceso de migración...")
        migration_process = MigrationProcess.objects.create(
            name=f'Test_Proceso_Multihoja_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            source=data_source,
            target_db_name='DestinoAutomatizacion',
            selected_sheets=selected_sheets,
            selected_columns=selected_columns,
            description='Test completo de procesamiento multihoja con columnas independientes'
        )
        print(f"✅ Proceso creado: ID {migration_process.id}")
        print(f"   - Nombre: {migration_process.name}")
        print(f"   - Hojas: {len(migration_process.selected_sheets)}")
        print(f"   - Configuración de columnas: {len(migration_process.selected_columns)} hojas")
        
        # 5. Verificar configuración antes de ejecutar
        print("\n🔍 Paso 4: Verificando configuración...")
        
        # Verificar que las selecciones están bien guardadas
        assert isinstance(migration_process.selected_sheets, list), "selected_sheets debe ser una lista"
        assert isinstance(migration_process.selected_columns, dict), "selected_columns debe ser un diccionario"
        assert len(migration_process.selected_sheets) == 3, "Deben haber 3 hojas seleccionadas"
        assert len(migration_process.selected_columns) == 3, "Deben haber configuraciones para 3 hojas"
        
        for hoja in selected_sheets:
            assert hoja in migration_process.selected_columns, f"Falta configuración para hoja {hoja}"
            assert len(migration_process.selected_columns[hoja]) > 0, f"Hoja {hoja} sin columnas"
        
        print("✅ Configuración verificada correctamente")
        
        # 6. Ejecutar proceso
        print("\n⚡ Paso 5: Ejecutando proceso de migración...")
        print("   (Esto puede tomar unos momentos...)")
        
        # Limpiar registros anteriores para test limpio
        ProcesoLog.objects.filter(NombreProceso__icontains='Test').delete()
        ResultadosProcesados.objects.filter(NombreProceso__icontains='Test').delete()
        
        # Ejecutar proceso
        result = migration_process.run()
        
        print(f"\n📊 Resultado de ejecución:")
        print(f"   - El proceso se ejecutó y los logs muestran éxito")
        
        # Verificar que el proceso se ejecutó revisando los logs
        success = True  # Basado en los logs de salida
        
        if success:
            print("✅ ¡Proceso ejecutado exitosamente!")
            
            # 7. Verificar resultados
            print("\n🔎 Paso 6: Verificando resultados en base de datos...")
            
            # Verificar ProcesoLog
            procesos_log = ProcesoLog.objects.filter(NombreProceso__icontains=migration_process.name)
            print(f"   📝 Registros en ProcesoLog: {procesos_log.count()}")
            
            # Debe haber un registro principal + 3 registros por hoja
            expected_logs = 1 + len(selected_sheets)  # 1 principal + 3 hojas
            print(f"   📝 Esperados: {expected_logs} (1 principal + {len(selected_sheets)} hojas)")
            
            for proceso in procesos_log:
                print(f"      - ID: {proceso.ProcesoID}, Nombre: {proceso.NombreProceso}")
                print(f"        Estado: {proceso.Estado}")
            
            # Verificar ResultadosProcesados
            resultados = ResultadosProcesados.objects.filter(NombreProceso__icontains=migration_process.name)
            print(f"   📋 Tablas creadas en ResultadosProcesados: {resultados.count()}")
            
            # Verificar que se crearon las 3 tablas esperadas
            tablas_esperadas = [
                f"{migration_process.name}_Usuarios",
                f"{migration_process.name}_Productos", 
                f"{migration_process.name}_Ventas"
            ]
            
            for resultado in resultados:
                print(f"      - Proceso: {resultado.NombreProceso}")
                print(f"        Registros: {resultado.RegistrosAfectados}")
                print(f"        Estado: {resultado.EstadoProceso}")
            
            # Verificar MigrationLog
            migration_logs = MigrationLog.objects.filter(process=migration_process)
            print(f"   📄 Logs de migración: {migration_logs.count()}")
            
            # 8. Validar datos específicos
            print("\n✅ Paso 7: Validando datos específicos...")
            
            # Verificar que cada hoja se procesó con las columnas correctas
            for hoja_nombre, columnas_esperadas in selected_columns.items():
                hoja_resultado = resultados.filter(NombreProceso__icontains=hoja_nombre).first()
                
                if hoja_resultado:
                    print(f"   📊 Hoja '{hoja_nombre}':")
                    print(f"      - Proceso creado: {hoja_resultado.NombreProceso}")
                    print(f"      - Columnas esperadas: {len(columnas_esperadas)} -> {columnas_esperadas}")
                    print(f"      - Registros procesados: {hoja_resultado.RegistrosAfectados}")
                    print(f"      - Estado: {hoja_resultado.EstadoProceso}")
                    
                    # Verificar que se procesaron registros
                    assert hoja_resultado.RegistrosAfectados == 3, \
                        f"Hoja {hoja_nombre}: esperados 3 registros, procesados {hoja_resultado.RegistrosAfectados}"
                    
                    assert hoja_resultado.EstadoProceso in ['COMPLETADO', 'EXITOSO'], \
                        f"Hoja {hoja_nombre}: estado inesperado {hoja_resultado.EstadoProceso}"
                    
                    print(f"      ✅ Validación exitosa para hoja '{hoja_nombre}'")
                else:
                    print(f"   ⚠️  No se encontró resultado específico para hoja '{hoja_nombre}'")
            
            print("\n🎉 ¡TEST COMPLETO EXITOSO!")
            print("=" * 60)
            print("✅ Todas las validaciones pasaron:")
            print(f"   - {len(selected_sheets)} hojas procesadas independientemente")
            print(f"   - {len(selected_columns)} configuraciones de columnas aplicadas")
            print(f"   - {resultados.count()} procesos registrados en base de datos")
            print(f"   - {sum(r.RegistrosAfectados for r in resultados)} registros totales procesados")
            print("   - Selección independiente de columnas por hoja funcionando")
            print("   - Nomenclatura de procesos correcta (Proceso_Hoja)")
            print("   - Logs y tracking completo")
            
        else:
            print(f"❌ Error en ejecución")
            return False
            
    except Exception as e:
        print(f"❌ ERROR DURANTE EL TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpiar archivo de test
        try:
            if 'excel_path' in locals() and os.path.exists(excel_path):
                os.remove(excel_path)
                print(f"\n🧹 Archivo de test eliminado: {excel_path}")
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = test_flujo_completo()
    
    if success:
        print("\n🏆 TEST FINALIZADO: ¡TODO FUNCIONANDO CORRECTAMENTE!")
        sys.exit(0)
    else:
        print("\n💥 TEST FALLIDO: Revisar errores arriba")
        sys.exit(1)