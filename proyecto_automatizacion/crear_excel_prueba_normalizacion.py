"""
Script para crear un archivo Excel de prueba con datos problemáticos
para validar la normalización de datos desde el frontend
"""
import pandas as pd
from datetime import datetime

# Crear datos de prueba con problemas comunes
datos_hoja1 = {
    'ID_Empleado': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Nombre_Completo': ['Juan Pérez', 'María López', '', '  ', 'Carlos Gómez', None, 'Ana Martínez', 'Pedro Ruiz', 'Laura Torres', 'Roberto Díaz'],
    'Edad': [25, '30', 'treinta y cinco', 'N/A', '', None, 45, '50.5', 'abc', '28'],
    'Salario_Mensual': ['1500.50', '2000', 'dos mil quinientos', 'N/A', '', None, '3500.75', '4000.00', '#ERROR', '2500'],
    'Fecha_Ingreso': ['2020-01-15', '2021-06-20', 'fecha_invalida', '15/13/2022', '', None, '2023-03-10', '2024-05-01', 'HOY', '2022-12-01'],
    'Activo': [True, False, 'Si', 'No', 'Sí', 'TRUE', 1, 0, '', None],
    'Horas_Trabajo': [40, 35.5, 'N/A', '', 42, None, 38, '40.0', 'tiempo completo', 45],
    'Departamento': ['Ventas', 'Marketing', 'IT', '', None, 'RH', 'Finanzas', 'Operaciones', 'Legal', 'Administración']
}

datos_hoja2 = {
    'Codigo_Producto': ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008'],
    'Nombre_Producto': ['Laptop', 'Mouse', '', 'Teclado', 'Monitor', None, 'Impresora', 'Scanner'],
    'Precio_Unitario': ['999.99', '25.50', 'N/A', '', '450.00', None, 'GRATIS', '350'],
    'Stock_Disponible': [50, '25', 'cero', 'N/A', '', None, 100, '75'],
    'Fecha_Ultimo_Ingreso': ['2024-01-15', '2024-02-20', 'hace un mes', '', None, '2024-06-10', '30/02/2024', '2024-08-15'],
    'Descontinuado': [False, False, 'No', '', None, True, 'SI', 0],
    'Peso_KG': ['2.5', '0.1', 'ligero', 'N/A', '', None, '15.5', '3.2']
}

datos_hoja3 = {
    'ID_Venta': [1, 2, 3, 4, 5, 6],
    'Cantidad': [5, '10', 'N/A', '', None, 8],
    'Precio_Total': ['5000.00', '250.50', 'ERROR', '', None, '2800.00'],
    'Fecha_Venta': ['2024-10-01', '2024-10-15', 'ayer', '', None, '2024-10-20'],
    'Cliente_ID': [101, '102', 'N/A', '', None, 106],
    'Estado': ['Completado', 'Pendiente', 'C', '', None, 'Cancelado']
}

# Crear archivo Excel con múltiples hojas
output_file = 'datos_prueba_normalizacion.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    # Hoja 1: Datos de empleados con problemas
    pd.DataFrame(datos_hoja1).to_excel(writer, sheet_name='Empleados', index=False)
    
    # Hoja 2: Datos de productos con problemas
    pd.DataFrame(datos_hoja2).to_excel(writer, sheet_name='Productos', index=False)
    
    # Hoja 3: Datos de ventas con problemas
    pd.DataFrame(datos_hoja3).to_excel(writer, sheet_name='Ventas', index=False)

print(f"✅ Archivo Excel creado exitosamente: {output_file}")
print("\n📋 CONTENIDO DEL ARCHIVO:")
print("\n" + "="*80)
print("📊 Hoja 1: Empleados (10 registros)")
print("="*80)
print("Columnas:", list(datos_hoja1.keys()))
print("\nDatos problemáticos incluidos:")
print("  • Edad: 'treinta y cinco', 'N/A', 'abc', cadenas vacías")
print("  • Salario_Mensual: 'dos mil quinientos', 'N/A', '#ERROR'")
print("  • Fecha_Ingreso: 'fecha_invalida', '15/13/2022' (fecha imposible), 'HOY'")
print("  • Activo: 'Si', 'No', 'Sí', 'TRUE' (variaciones de booleanos)")
print("  • Horas_Trabajo: 'N/A', 'tiempo completo'")
print("  • Valores None y cadenas vacías en múltiples columnas")

print("\n" + "="*80)
print("📦 Hoja 2: Productos (8 registros)")
print("="*80)
print("Columnas:", list(datos_hoja2.keys()))
print("\nDatos problemáticos incluidos:")
print("  • Precio_Unitario: 'N/A', 'GRATIS'")
print("  • Stock_Disponible: 'cero', 'N/A'")
print("  • Fecha_Ultimo_Ingreso: 'hace un mes', '30/02/2024' (fecha imposible)")
print("  • Descontinuado: 'No', 'SI' (variaciones de booleanos)")
print("  • Peso_KG: 'ligero', 'N/A'")

print("\n" + "="*80)
print("💰 Hoja 3: Ventas (6 registros)")
print("="*80)
print("Columnas:", list(datos_hoja3.keys()))
print("\nDatos problemáticos incluidos:")
print("  • Cantidad: 'N/A'")
print("  • Precio_Total: 'ERROR'")
print("  • Fecha_Venta: 'ayer'")
print("  • Cliente_ID: 'N/A'")
print("  • Valores None y cadenas vacías en múltiples columnas")

print("\n" + "="*80)
print("🎯 CÓMO USAR ESTE ARCHIVO PARA PRUEBAS:")
print("="*80)
print("""
1. Copia el archivo a tu carpeta de archivos Excel configurada en Django

2. Abre el frontend: http://127.0.0.1:8000/automatizacion/

3. Crea un nuevo proceso de tipo Excel

4. Selecciona el archivo: datos_prueba_normalizacion.xlsx

5. Selecciona las hojas que quieras probar (Empleados, Productos, Ventas)

6. Selecciona las columnas a migrar

7. Ejecuta el proceso

8. Observa en la terminal de Django los warnings de normalización:
   ⚠️ Se normalizaron datos con problemas:
   - Columna 'Edad': X valores inválidos convertidos a NULL
   - Columna 'Salario_Mensual': X valores inválidos convertidos a NULL
   - Columna 'Fecha_Ingreso': X valores inválidos convertidos a NULL
   ...

9. Verifica en SQL Server que la tabla destino tenga:
   - Tipos de datos correctos (float, datetime, etc.)
   - NULL en los valores que eran inválidos
   - Datos válidos preservados correctamente

10. Revisa los logs del proceso en la interfaz para ver el resumen
""")

print("\n" + "="*80)
print("📊 VALORES ESPERADOS DESPUÉS DE LA NORMALIZACIÓN:")
print("="*80)
print("""
Hoja Empleados:
  • Edad: [25, 30, NULL, NULL, NULL, NULL, 45, 50.5, NULL, 28] (tipo: float)
  • Salario_Mensual: [1500.50, 2000, NULL, NULL, NULL, NULL, 3500.75, 4000, NULL, 2500] (tipo: float)
  • Fecha_Ingreso: fechas válidas → datetime, inválidas → NULL
  • Activo: [1, 0, NULL, NULL, NULL, 1, 1, 0, NULL, NULL] (tipo: float, True→1, False→0)
  • Horas_Trabajo: [40, 35.5, NULL, NULL, 42, NULL, 38, 40, NULL, 45] (tipo: float)

Hoja Productos:
  • Precio_Unitario: [999.99, 25.50, NULL, NULL, 450, NULL, NULL, 350] (tipo: float)
  • Stock_Disponible: [50, 25, NULL, NULL, NULL, NULL, 100, 75] (tipo: float)
  • Peso_KG: [2.5, 0.1, NULL, NULL, NULL, NULL, 15.5, 3.2] (tipo: float)

Hoja Ventas:
  • Cantidad: [5, 10, NULL, NULL, NULL, 8] (tipo: float)
  • Precio_Total: [5000, 250.5, NULL, NULL, NULL, 2800] (tipo: float)
  • Cliente_ID: [101, 102, NULL, NULL, NULL, 106] (tipo: float)
""")

print("\n✅ ¡Listo para probar!")
