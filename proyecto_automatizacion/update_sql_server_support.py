"""
Script para modificar el archivo de django-mssql-backend para admitir SQL Server 16
"""
import os
import re

def update_sql_server_support():
    # Ruta al archivo base.py de django-mssql-backend
    base_py_path = r"C:\Users\migue\AppData\Local\Programs\Python\Python313\Lib\site-packages\sql_server\pyodbc\base.py"
    
    if not os.path.exists(base_py_path):
        print(f"El archivo {base_py_path} no existe.")
        return False
    
    # Leer el archivo
    with open(base_py_path, 'r') as f:
        content = f.read()
    
    # Buscar la sección que define los _sql_server_versions
    versions_pattern = r'_sql_server_versions\s*=\s*{\s*[^}]*}'
    versions_match = re.search(versions_pattern, content, re.DOTALL)
    
    if not versions_match:
        print("No se encontró la definición de _sql_server_versions.")
        return False
    
    versions_def = versions_match.group(0)
    
    # Verificar si ya tiene soporte para SQL Server 16
    if "16:" in versions_def:
        print("El archivo ya tiene soporte para SQL Server 16.")
        return True
    
    # Agregar SQL Server 16
    new_versions_def = versions_def.replace(
        '_sql_server_versions = {',
        '_sql_server_versions = {\n        16: 2022,'
    )
    
    # Reemplazar en el contenido
    updated_content = content.replace(versions_def, new_versions_def)
    
    # Escribir el archivo actualizado
    with open(base_py_path, 'w') as f:
        f.write(updated_content)
    
    print("¡Archivo actualizado correctamente!")
    print("Se agregó soporte para SQL Server 16 (versión 2022)")
    return True

if __name__ == "__main__":
    update_sql_server_support()
