import os
import django
import sys

# Configurar Django
sys.path.append(r'c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.conf import settings

def check_destino_config():
    """
    Revisa la configuración de la base de datos destino
    """
    
    print("=== CONFIGURACIÓN DE BASE DE DATOS DESTINO ===")
    
    try:
        destino_config = settings.DATABASES['destino']
        
        print("📊 Configuración encontrada:")
        for key, value in destino_config.items():
            if key == 'PASSWORD':
                print(f"   {key}: {'*' * len(str(value))}")
            else:
                print(f"   {key}: {value}")
        
        # También verificar la configuración default por si necesitamos copiarla
        print(f"\n📊 Configuración 'default' para referencia:")
        default_config = settings.DATABASES['default']
        for key, value in default_config.items():
            if key == 'PASSWORD':
                print(f"   {key}: {'*' * len(str(value))}")
            else:
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_destino_config()