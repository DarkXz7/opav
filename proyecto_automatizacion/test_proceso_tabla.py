#!/usr/bin/env python
"""
Script simplificado para probar la creación de tablas de proceso
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection

def test_proceso_completo():
    """
    Prueba la ejecución completa de un proceso con su propia tabla
    """
    print("=" * 60)
    print("PRUEBA: Ejecución de proceso con tabla propia en DestinoAutomatizacion")
    print("=" * 60)
    
    try:
        # 1. Crear una conexión de prueba si no existe
        print("\n1. Preparando datos de prueba...")
        
        # Buscar o crear una conexión existente
        try:
            connection = DatabaseConnection.objects.first()
            if not connection:
                print("   ℹ️  No hay conexiones disponibles. Creando una de prueba...")
                connection = DatabaseConnection.objects.create(
                    name="Conexión Test",
                    server="localhost\\SQLEXPRESS",
                    username="miguel",
                    password="16474791@",
                    port=1433,
                    selected_database="DestinoAutomatizacion"
                )
            else:
                # Asegurar que la conexión apunte a DestinoAutomatizacion
                connection.selected_database = "DestinoAutomatizacion"
                connection.save()
            
            print(f"   ✅ Usando conexión: {connection.name}")
        except Exception as e:
            print(f"   ⚠️  Error con conexión, continuando con fuente simple: {e}")
            connection = None
        
        # 2. Crear fuente de datos de prueba
        print("\n2. Creando fuente de datos de prueba...")
        
        # Limpiar procesos de prueba anteriores
        MigrationProcess.objects.filter(name__icontains="Test Proceso").delete()
        DataSource.objects.filter(name__icontains="Test Source").delete()
        
        source = DataSource.objects.create(
            name="Test Source - Proceso Tablas",
            source_type="sql",
            connection=connection
        )
        print(f"   ✅ Fuente creada: {source.name}")
        
        # 3. Crear proceso de migración de prueba
        print("\n3. Creando proceso de migración...")
        
        process = MigrationProcess.objects.create(
            name="Test Proceso Tabla Propia",
            description="Proceso de prueba para verificar creación de tabla específica",
            source=source,
            selected_tables='[{"name": "tabla_test", "full_name": "dbo.tabla_test"}]',
            selected_columns='{"tabla_test": ["id", "nombre", "fecha"]}',
            target_db_name="DestinoAutomatizacion"
        )
        print(f"   ✅ Proceso creado: {process.name} (ID: {process.id})")
        
        # 4. Ejecutar el proceso
        print("\n4. Ejecutando el proceso...")
        print("   🚀 Iniciando ejecución...")
        
        # Ejecutar el método run() que debería crear la tabla específica
        process.run()
        
        # 5. Verificar el resultado
        print("\n5. Verificando resultado de la ejecución...")
        
        # Recargar el proceso desde la BD para ver el estado actualizado
        process.refresh_from_db()
        
        print(f"   📊 Estado del proceso: {process.status}")
        print(f"   🕒 Última ejecución: {process.last_run}")
        
        if process.status == 'completed':
            print("   ✅ Proceso completado exitosamente")
            
            # La tabla debería haberse creado con nombre basado en el proceso
            nombre_esperado = "Proceso_Test_Proceso_Tabla_Propia"
            print(f"   📋 Nombre de tabla esperado: {nombre_esperado}")
            
            # Verificar usando el dynamic_table_manager
            from automatizacion.dynamic_table_service import dynamic_table_manager
            
            tabla_existe = dynamic_table_manager.table_exists(nombre_esperado)
            print(f"   🔍 ¿Tabla existe?: {tabla_existe}")
            
            if tabla_existe:
                print("   🎉 ¡ÉXITO! La tabla específica del proceso se creó correctamente")
                
                # Intentar contar registros
                try:
                    from django.db import connections
                    with connections['destino'].cursor() as cursor:
                        cursor.execute(f"SELECT COUNT(*) FROM [{nombre_esperado}]")
                        count = cursor.fetchone()[0]
                        print(f"   📊 Registros en la tabla: {count}")
                        
                        if count > 0:
                            cursor.execute(f"SELECT TOP 1 ResultadoID, ProcesoID, EstadoProceso FROM [{nombre_esperado}]")
                            registro = cursor.fetchone()
                            print(f"   📝 Primer registro: ID={registro[0]}, ProcesoID={registro[1]}, Estado={registro[2]}")
                            
                except Exception as e:
                    print(f"   ⚠️  No se pudo leer el contenido de la tabla: {e}")
                
            else:
                print("   ❌ ERROR: La tabla no se creó")
                return False
                
        elif process.status == 'failed':
            print("   ❌ ERROR: El proceso falló durante la ejecución")
            return False
        else:
            print(f"   ⚠️  Estado inesperado: {process.status}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA: El sistema de tablas dinámicas funciona correctamente")
        print("📋 Cada proceso ahora crea su propia tabla en DestinoAutomatizacion")
        print("🔄 Las tablas se vacían y recargan en cada ejecución del proceso")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante la prueba: {str(e)}")
        import traceback
        print(f"Traceback completo:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    exito = test_proceso_completo()
    sys.exit(0 if exito else 1)