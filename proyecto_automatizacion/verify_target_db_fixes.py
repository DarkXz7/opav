import os
import django
import sys

# Configurar Django
sys.path.append(r'c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

def verify_fixes():
    """
    Verifica que las correcciones estén funcionando correctamente
    """
    
    print("=== VERIFICACIÓN DE CORRECCIONES APLICADAS ===")
    
    try:
        # 1. Verificar el valor por defecto del modelo
        print("1. 📊 Verificando valor por defecto del modelo...")
        field = MigrationProcess._meta.get_field('target_db_name')
        print(f"   Valor por defecto del campo: '{field.default}'")
        
        # 2. Crear un proceso de prueba para verificar el comportamiento
        print("\n2. 🧪 Creando proceso de prueba...")
        from automatizacion.models import DataSource, DatabaseConnection
        
        # Usar una fuente existente para la prueba
        source = DataSource.objects.first()
        if not source:
            print("   ❌ No hay fuentes de datos para la prueba")
            return
        
        # Crear proceso temporal
        test_process = MigrationProcess.objects.create(
            name="TEMP_TEST_PROCESS_VERIFICACION",
            description="Proceso temporal para verificar correcciones",
            source=source
        )
        
        print(f"   ✅ Proceso creado con ID: {test_process.id}")
        print(f"   📊 target_db_name: '{test_process.target_db_name}'")
        
        # 3. Verificar si el valor es correcto
        if test_process.target_db_name == 'DestinoAutomatizacion':
            print("   ✅ CORRECTO: El valor por defecto es 'DestinoAutomatizacion'")
        else:
            print(f"   ❌ ERROR: El valor es '{test_process.target_db_name}' en lugar de 'DestinoAutomatizacion'")
        
        # 4. Limpiar: eliminar proceso de prueba
        test_process.delete()
        print("   🧹 Proceso de prueba eliminado")
        
        # 5. Verificar estadísticas generales
        print(f"\n3. 📊 Estadísticas generales:")
        total = MigrationProcess.objects.count()
        with_destino = MigrationProcess.objects.filter(target_db_name='DestinoAutomatizacion').count()
        with_default = MigrationProcess.objects.filter(target_db_name='default').count()
        
        print(f"   Total procesos: {total}")
        print(f"   Con 'DestinoAutomatizacion': {with_destino}")
        print(f"   Con 'default': {with_default}")
        print(f"   Otros: {total - with_destino - with_default}")
        
        if with_default == 0:
            print("   ✅ PERFECTO: No quedan procesos con 'default'")
        else:
            print(f"   ⚠️ ATENCIÓN: Aún hay {with_default} procesos con 'default'")
        
        print("\n🎉 VERIFICACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_fixes()