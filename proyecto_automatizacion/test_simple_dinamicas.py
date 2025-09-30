"""
Prueba simple del sistema de tablas dinámicas
"""

from automatizacion.dynamic_table_service import dynamic_table_manager, DynamicTableError

print("🧪 Prueba simple del sistema de tablas dinámicas")
print("=" * 60)

# Probar solo generación de nombres de tabla
test_names = [
    "Proceso Simple",
    "Proceso con Números 123", 
    "Test-Con-Guiones"
]

for name in test_names:
    try:
        table_name = dynamic_table_manager.generate_table_name(name)
        print(f"✅ '{name}' -> '{table_name}'")
    except Exception as e:
        print(f"❌ '{name}' -> Error: {str(e)}")

print("\n🔍 Probando verificación de tabla...")
try:
    exists = dynamic_table_manager.table_exists("ResultadosProcesados")
    print(f"✅ Tabla 'ResultadosProcesados' existe: {exists}")
except Exception as e:
    print(f"❌ Error verificando tabla: {str(e)}")

print("\n🏁 Prueba simple completada")