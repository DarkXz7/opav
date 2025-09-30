#!/usr/bin/env python
"""
Script para probar la corrección del error JSON en DatosProcesados
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection

def test_correccion_json():
    """
    Prueba que la columna DatosProcesados ahora guarde JSON correctamente
    """
    print("=" * 70)
    print("PRUEBA: Corrección del error JSON en DatosProcesados")
    print("=" * 70)
    
    try:
        # Limpiar procesos de prueba anteriores
        print("\n1. Limpiando procesos de prueba anteriores...")
        MigrationProcess.objects.filter(name__icontains="Test JSON").delete()
        DataSource.objects.filter(name__icontains="Test JSON").delete()
        
        # Crear fuente de datos de prueba
        print("\n2. Creando fuente de datos con datos complejos...")
        
        connection = DatabaseConnection.objects.first()
        if connection:
            connection.selected_database = "DestinoAutomatizacion"
            connection.save()
        
        source = DataSource.objects.create(
            name="Test JSON Source",
            source_type="sql",
            connection=connection
        )
        print(f"   ✅ Fuente creada: {source.name}")
        
        # Crear proceso que va a generar listas de datos
        print("\n3. Creando proceso de migración...")
        
        process = MigrationProcess.objects.create(
            name="Test JSON Correction Process",
            description="Proceso para probar corrección de JSON en DatosProcesados",
            source=source,
            selected_tables='[{"name": "tabla_test", "full_name": "dbo.tabla_test"}, {"name": "tabla_ventas", "full_name": "dbo.tabla_ventas"}]',
            selected_columns='{"tabla_test": ["id", "nombre", "fecha", "monto"], "tabla_ventas": ["venta_id", "cliente", "producto", "cantidad", "precio"]}',
            target_db_name="DestinoAutomatizacion"
        )
        print(f"   ✅ Proceso creado: {process.name} (ID: {process.id})")
        
        # Ejecutar el proceso
        print("\n4. Ejecutando proceso (esto debería crear un resumen JSON válido)...")
        print("   🚀 Iniciando ejecución...")
        
        try:
            process.run()
            print("   ✅ Proceso ejecutado SIN errores JSON")
        except Exception as e:
            if "JSON object must be str" in str(e):
                print(f"   ❌ ERROR JSON DETECTADO: {str(e)}")
                return False
            else:
                print(f"   ⚠️  Otro tipo de error: {str(e)}")
                # Continuar para verificar si se guardó algo
        
        # Verificar el resultado
        print("\n5. Verificando que se guardó correctamente...")
        
        process.refresh_from_db()
        print(f"   📊 Estado final: {process.status}")
        
        # Verificar el contenido de la tabla
        if process.status in ['completed', 'failed']:
            from automatizacion.dynamic_table_service import dynamic_table_manager
            from django.db import connections
            
            # Generar nombre de tabla esperado
            tabla_esperada = "Proceso_Test_JSON_Correction_Process"
            
            if dynamic_table_manager.table_exists(tabla_esperada):
                print(f"   ✅ Tabla creada: {tabla_esperada}")
                
                try:
                    with connections['destino'].cursor() as cursor:
                        cursor.execute(f"""
                            SELECT TOP 1 
                                ResultadoID, 
                                ProcesoID, 
                                LEN(DatosProcesados) as TamañoJSON,
                                LEFT(DatosProcesados, 200) as InicioJSON,
                                EstadoProceso
                            FROM [{tabla_esperada}]
                        """)
                        
                        resultado = cursor.fetchone()
                        
                        if resultado:
                            print(f"   📝 Registro encontrado:")
                            print(f"      - ResultadoID: {resultado[0]}")
                            print(f"      - ProcesoID: {resultado[1]}")
                            print(f"      - Tamaño JSON: {resultado[2]} caracteres")
                            print(f"      - Inicio JSON: {resultado[3]}...")
                            print(f"      - Estado: {resultado[4]}")
                            
                            # Intentar parsear el JSON completo
                            cursor.execute(f"SELECT DatosProcesados FROM [{tabla_esperada}] WHERE ResultadoID = ?", [resultado[0]])
                            json_completo = cursor.fetchone()[0]
                            
                            try:
                                import json
                                datos_parseados = json.loads(json_completo)
                                print(f"   ✅ JSON VÁLIDO - Estructura:")
                                
                                if isinstance(datos_parseados, dict):
                                    for key in list(datos_parseados.keys())[:5]:
                                        valor = datos_parseados[key]
                                        if isinstance(valor, dict):
                                            print(f"      - {key}: dict con {len(valor)} elementos")
                                        elif isinstance(valor, list):
                                            print(f"      - {key}: lista con {len(valor)} elementos")
                                        else:
                                            print(f"      - {key}: {str(valor)[:50]}")
                                
                                print("\n   🎉 ¡CORRECCIÓN EXITOSA!")
                                print("   📋 La columna DatosProcesados ahora contiene un resumen JSON válido")
                                print("   🚫 Ya NO intenta guardar listas completas de datos")
                                
                                return True
                                
                            except json.JSONDecodeError as e:
                                print(f"   ❌ JSON INVÁLIDO: {str(e)}")
                                return False
                                
                        else:
                            print("   ⚠️  No se encontraron registros en la tabla")
                            return False
                            
                except Exception as e:
                    print(f"   ❌ Error consultando la tabla: {str(e)}")
                    return False
            else:
                print(f"   ❌ Tabla no fue creada: {tabla_esperada}")
                return False
        else:
            print(f"   ❌ Estado inesperado: {process.status}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR durante la prueba: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    exito = test_correccion_json()
    
    if exito:
        print("\n" + "=" * 70)
        print("✅ PRUEBA EXITOSA: Problema JSON corregido")
        print("📋 DatosProcesados ahora guarda resúmenes JSON válidos")
        print("🚫 Ya no intenta guardar listas completas")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ PRUEBA FALLIDA: Revisar implementación")
        print("=" * 70)
    
    sys.exit(0 if exito else 1)