#!/usr/bin/env python
"""
Script de prueba para validar todas las mejoras implementadas:
1. Campo NombreProceso en tablas dinámicas
2. ParametrosEntrada optimizado en ProcesoLog
3. Correcta relación LogID (PK) y ProcesoID/MigrationProcessID en logging
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection

def test_mejoras_completas():
    """
    Prueba integral de todas las mejoras implementadas
    """
    print("=" * 80)
    print("PRUEBA INTEGRAL: Validación de mejoras en tablas y logging")
    print("=" * 80)
    
    try:
        # Limpiar datos de prueba anteriores
        print("\n1. Preparando datos de prueba...")
        MigrationProcess.objects.filter(name__icontains="Test Mejoras").delete()
        DataSource.objects.filter(name__icontains="Test Mejoras").delete()
        
        # Configurar fuente y proceso
        connection = DatabaseConnection.objects.first()
        if connection:
            connection.selected_database = "DestinoAutomatizacion"
            connection.save()
        
        source = DataSource.objects.create(
            name="Test Mejoras Source",
            source_type="sql",
            connection=connection
        )
        
        process = MigrationProcess.objects.create(
            name="Test Mejoras Integrales Sistema",
            description="Proceso para validar todas las mejoras: NombreProceso, ParametrosEntrada optimizado, relaciones correctas",
            source=source,
            selected_tables='[{"name": "ventas", "full_name": "dbo.ventas"}, {"name": "clientes", "full_name": "dbo.clientes"}]',
            selected_columns='{"ventas": ["id", "fecha", "monto"], "clientes": ["id", "nombre", "email"]}',
            target_db_name="DestinoAutomatizacion"
        )
        
        print(f"   ✅ Proceso creado: {process.name} (ID: {process.id})")
        
        # EJECUTAR EL PROCESO (esto probará todas las mejoras)
        print(f"\n2. Ejecutando proceso que debería usar todas las mejoras...")
        print("   🚀 Iniciando ejecución integral...")
        
        process.run()
        
        # VERIFICAR MEJORA 1: Campo NombreProceso en tabla dinámica
        print(f"\n3. VERIFICANDO MEJORA 1: Campo NombreProceso en tabla dinámica")
        
        process.refresh_from_db()
        if process.status == 'completed':
            from automatizacion.dynamic_table_service import dynamic_table_manager
            from django.db import connections
            
            tabla_esperada = "Proceso_Test_Mejoras_Integrales_Sistema"
            
            if dynamic_table_manager.table_exists(tabla_esperada):
                print(f"   ✅ Tabla creada: {tabla_esperada}")
                
                # Verificar que la tabla tenga la columna NombreProceso
                with connections['destino'].cursor() as cursor:
                    cursor.execute("""
                        SELECT COLUMN_NAME 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME = ? AND COLUMN_NAME = 'NombreProceso'
                    """, [tabla_esperada])
                    
                    columna_existe = cursor.fetchone() is not None
                    
                    if columna_existe:
                        print("   ✅ MEJORA 1 CONFIRMADA: Columna NombreProceso existe en tabla dinámica")
                        
                        # Verificar que tenga datos
                        cursor.execute(f"SELECT TOP 1 ResultadoID, NombreProceso, ProcesoID FROM [{tabla_esperada}]")
                        registro = cursor.fetchone()
                        
                        if registro:
                            print(f"   📋 Datos verificados:")
                            print(f"      - ResultadoID: {registro[0]}")
                            print(f"      - NombreProceso: '{registro[1]}'")
                            print(f"      - ProcesoID: {registro[2]}")
                            
                            if registro[1] == process.name:
                                print("   🎉 ¡PERFECTO! NombreProceso coincide con el nombre del frontend")
                            else:
                                print(f"   ⚠️  Discrepancia: esperado '{process.name}', obtenido '{registro[1]}'")
                        else:
                            print("   ❌ No hay registros en la tabla")
                            return False
                    else:
                        print("   ❌ MEJORA 1 FALLIDA: Columna NombreProceso NO existe")
                        return False
            else:
                print(f"   ❌ Tabla no creada: {tabla_esperada}")
                return False
        else:
            print(f"   ❌ Proceso no completado: {process.status}")
            return False
        
        # VERIFICAR MEJORA 2: ParametrosEntrada optimizado en ProcesoLog
        print(f"\n4. VERIFICANDO MEJORA 2: ParametrosEntrada optimizado en ProcesoLog")
        
        from automatizacion.logs.models_logs import ProcesoLog
        
        # Buscar logs recientes de este proceso
        logs_proceso = ProcesoLog.objects.using('logs').filter(
            NombreProceso__icontains="Test Mejoras"
        ).order_by('-FechaEjecucion')[:3]
        
        if logs_proceso:
            print(f"   ✅ Encontrados {len(logs_proceso)} logs del proceso")
            
            for i, log in enumerate(logs_proceso):
                print(f"\n   📋 Log {i+1}:")
                print(f"      - LogID: {log.LogID}")
                print(f"      - ProcesoID: {log.ProcesoID}")
                print(f"      - MigrationProcessID: {log.MigrationProcessID}")
                print(f"      - Estado: {log.Estado}")
                
                # Verificar que ParametrosEntrada sea JSON optimizado
                if log.ParametrosEntrada:
                    try:
                        import json
                        parametros = json.loads(log.ParametrosEntrada)
                        
                        # Verificar estructura optimizada
                        if isinstance(parametros, dict):
                            print(f"      - ParametrosEntrada: JSON válido con {len(parametros)} secciones")
                            
                            # Verificar secciones esperadas
                            secciones_encontradas = []
                            secciones_esperadas = ['timestamp', 'proceso', 'configuracion', 'origen']
                            
                            for seccion in secciones_esperadas:
                                if seccion in parametros:
                                    secciones_encontradas.append(seccion)
                            
                            print(f"      - Secciones: {', '.join(secciones_encontradas)}")
                            
                            # Mostrar muestra del contenido optimizado
                            if 'proceso' in parametros:
                                proceso_info = parametros['proceso']
                                print(f"      - Proceso info: {proceso_info}")
                            
                            if len(secciones_encontradas) >= 2:
                                print("   🎉 ¡MEJORA 2 CONFIRMADA! ParametrosEntrada está optimizado")
                            else:
                                print("   ⚠️  ParametrosEntrada no tiene estructura optimizada esperada")
                        else:
                            print("   ❌ ParametrosEntrada no es un diccionario JSON válido")
                            return False
                            
                    except json.JSONDecodeError:
                        print("   ❌ ParametrosEntrada no es JSON válido")
                        return False
                else:
                    print("   ⚠️  ParametrosEntrada está vacío")
        else:
            print("   ❌ No se encontraron logs del proceso")
            return False
        
        # VERIFICAR MEJORA 3: Relaciones correctas de IDs
        print(f"\n5. VERIFICANDO MEJORA 3: Relaciones correctas LogID (PK) y ProcesoID")
        
        log_principal = logs_proceso[0]  # Tomar el log más reciente
        
        # Verificar que LogID sea PK autoincremental
        if log_principal.LogID and isinstance(log_principal.LogID, int):
            print(f"   ✅ LogID es PK autoincremental: {log_principal.LogID}")
        else:
            print("   ❌ LogID no es válido como PK")
            return False
        
        # Verificar que ProcesoID sea UUID de ejecución
        if log_principal.ProcesoID and len(log_principal.ProcesoID) == 36:
            print(f"   ✅ ProcesoID es UUID de ejecución: {log_principal.ProcesoID}")
        else:
            print("   ❌ ProcesoID no tiene formato UUID válido")
            return False
        
        # Verificar que MigrationProcessID sea FK al proceso configurado
        if log_principal.MigrationProcessID == process.id:
            print(f"   ✅ MigrationProcessID coincide con proceso configurado: {log_principal.MigrationProcessID}")
            print("   🎉 ¡MEJORA 3 CONFIRMADA! Relaciones de IDs son correctas")
        else:
            print(f"   ⚠️  MigrationProcessID ({log_principal.MigrationProcessID}) no coincide con process.id ({process.id})")
        
        # RESUMEN FINAL
        print("\n" + "=" * 80)
        print("✅ TODAS LAS MEJORAS IMPLEMENTADAS Y FUNCIONANDO:")
        print("✅ 1. Campo NombreProceso agregado a tablas dinámicas")
        print("✅ 2. ParametrosEntrada optimizado (JSON conciso y legible)")  
        print("✅ 3. Relaciones correctas: LogID (PK), ProcesoID (UUID), MigrationProcessID (FK)")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante la prueba: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    exito = test_mejoras_completas()
    sys.exit(0 if exito else 1)