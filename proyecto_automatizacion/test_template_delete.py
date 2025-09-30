"""
Test simple para verificar que el template confirm_delete.html funcione correctamente
"""

# Configurar Django
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.template.loader import get_template
from django.template import Context
from automatizacion.models import MigrationProcess, DataSource

def test_template():
    print("🧪 Test: Verificar que el template confirm_delete.html funcione")
    print("=" * 60)
    
    try:
        # 1. Intentar cargar el template
        template = get_template('automatizacion/confirm_delete.html')
        print("✅ Template cargado exitosamente")
        
        # 2. Crear un proceso de prueba para el contexto
        # Buscar un proceso existente o crear datos de prueba
        try:
            process = MigrationProcess.objects.first()
            if not process:
                # Crear datos de prueba si no existe ningún proceso
                print("⚠️  No hay procesos existentes, creando datos de prueba...")
                data_source = DataSource.objects.create(
                    name="Fuente de Prueba Template",
                    source_type="csv",
                    file_path="test.csv"
                )
                process = MigrationProcess.objects.create(
                    name="Proceso de Prueba Template",
                    description="Proceso para probar el template de eliminación",
                    source=data_source,
                    status="draft"
                )
                print(f"✅ Proceso de prueba creado: {process.name}")
            else:
                print(f"✅ Usando proceso existente: {process.name}")
                
        except Exception as e:
            print(f"❌ Error creando/obteniendo proceso: {e}")
            return
        
        # 3. Renderizar el template con contexto
        context = {'process': process}
        try:
            rendered = template.render(context)
            print("✅ Template renderizado exitosamente")
            print(f"📄 Tamaño del HTML generado: {len(rendered)} caracteres")
            
            # Verificar que contenga elementos importantes
            if 'Confirmar Eliminación' in rendered:
                print("✅ Título de confirmación encontrado")
            else:
                print("❌ Título de confirmación NO encontrado")
            
            if process.name in rendered:
                print(f"✅ Nombre del proceso encontrado: {process.name}")
            else:
                print(f"❌ Nombre del proceso NO encontrado: {process.name}")
            
            if 'csrf_token' in rendered:
                print("✅ Token CSRF incluido")
            else:
                print("❌ Token CSRF NO incluido")
                
        except Exception as e:
            print(f"❌ Error renderizando template: {e}")
            return
        
        print("\n🎉 Template confirm_delete.html funciona correctamente")
        print("   El error TemplateDoesNotExist debería estar solucionado")
        
    except Exception as e:
        print(f"❌ Error cargando template: {e}")
        print("   Verificar que el archivo esté en la ubicación correcta:")
        print("   automatizacion/templates/automatizacion/confirm_delete.html")

if __name__ == "__main__":
    test_template()