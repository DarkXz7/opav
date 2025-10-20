# 📊 GUÍA: Cómo Lucirá el Excel de Prueba para Validar Normalización

## ✅ Archivo Creado

**Ubicación**: `datos_prueba_normalizacion.xlsx` (en la raíz del proyecto)

---

## 📋 ESTRUCTURA DEL ARCHIVO

### Hoja 1: **Empleados** (10 registros)

| ID_Empleado | Nombre_Completo | Edad | Salario_Mensual | Fecha_Ingreso | Activo | Horas_Trabajo | Departamento |
|-------------|----------------|------|-----------------|---------------|--------|---------------|-------------|
| 1 | Juan Pérez | 25 | 1500.50 | 2020-01-15 | True | 40 | Ventas |
| 2 | María López | 30 | 2000 | 2021-06-20 | False | 35.5 | Marketing |
| 3 | *(vacío)* | **treinta y cinco** | **dos mil quinientos** | **fecha_invalida** | Si | **N/A** | IT |
| 4 | *(espacios)* | **N/A** | **N/A** | **15/13/2022** | No | *(vacío)* | *(vacío)* |
| 5 | Carlos Gómez | *(vacío)* | *(vacío)* | *(vacío)* | Sí | 42 | *(None)* |
| 6 | *(None)* | *(None)* | *(None)* | *(None)* | TRUE | *(None)* | RH |
| 7 | Ana Martínez | 45 | 3500.75 | 2023-03-10 | 1 | 38 | Finanzas |
| 8 | Pedro Ruiz | 50.5 | 4000.00 | 2024-05-01 | 0 | 40.0 | Operaciones |
| 9 | Laura Torres | **abc** | **#ERROR** | **HOY** | *(vacío)* | **tiempo completo** | Legal |
| 10 | Roberto Díaz | 28 | 2500 | 2022-12-01 | *(None)* | 45 | Administración |

**Problemas incluidos:**
- ❌ **Edad**: texto ("treinta y cinco", "abc"), "N/A", valores vacíos
- ❌ **Salario**: texto ("dos mil quinientos"), "#ERROR", "N/A"
- ❌ **Fecha**: texto ("fecha_invalida", "HOY"), fechas imposibles ("15/13/2022")
- ❌ **Activo**: variaciones textuales ("Si", "No", "Sí", "TRUE")
- ❌ **Horas**: texto ("N/A", "tiempo completo")

---

### Hoja 2: **Productos** (8 registros)

| Codigo_Producto | Nombre_Producto | Precio_Unitario | Stock_Disponible | Fecha_Ultimo_Ingreso | Descontinuado | Peso_KG |
|----------------|----------------|----------------|------------------|---------------------|---------------|---------|
| P001 | Laptop | 999.99 | 50 | 2024-01-15 | False | 2.5 |
| P002 | Mouse | 25.50 | 25 | 2024-02-20 | False | 0.1 |
| P003 | *(vacío)* | **N/A** | **cero** | **hace un mes** | No | **ligero** |
| P004 | Teclado | *(vacío)* | **N/A** | *(vacío)* | *(vacío)* | **N/A** |
| P005 | Monitor | 450.00 | *(vacío)* | *(None)* | *(None)* | *(vacío)* |
| P006 | *(None)* | *(None)* | *(None)* | 2024-06-10 | True | *(None)* |
| P007 | Impresora | **GRATIS** | 100 | **30/02/2024** | SI | 15.5 |
| P008 | Scanner | 350 | 75 | 2024-08-15 | 0 | 3.2 |

**Problemas incluidos:**
- ❌ **Precio**: texto ("N/A", "GRATIS")
- ❌ **Stock**: texto ("cero", "N/A")
- ❌ **Fecha**: texto ("hace un mes"), fecha imposible ("30/02/2024")
- ❌ **Descontinuado**: variaciones textuales ("No", "SI")
- ❌ **Peso**: texto ("ligero", "N/A")

---

### Hoja 3: **Ventas** (6 registros)

| ID_Venta | Cantidad | Precio_Total | Fecha_Venta | Cliente_ID | Estado |
|----------|----------|--------------|-------------|-----------|---------|
| 1 | 5 | 5000.00 | 2024-10-01 | 101 | Completado |
| 2 | 10 | 250.50 | 2024-10-15 | 102 | Pendiente |
| 3 | **N/A** | **ERROR** | **ayer** | **N/A** | C |
| 4 | *(vacío)* | *(vacío)* | *(vacío)* | *(vacío)* | *(vacío)* |
| 5 | *(None)* | *(None)* | *(None)* | *(None)* | *(None)* |
| 6 | 8 | 2800.00 | 2024-10-20 | 106 | Cancelado |

**Problemas incluidos:**
- ❌ **Cantidad**: texto ("N/A")
- ❌ **Precio**: texto ("ERROR")
- ❌ **Fecha**: texto ("ayer")
- ❌ **Cliente_ID**: texto ("N/A")

---

## 🎯 PASOS PARA PROBAR EN EL FRONTEND

### 1. **Mover el archivo a la carpeta correcta**

```powershell
# Opción 1: Copiar al directorio de archivos de Django (ajusta la ruta según tu configuración)
copy datos_prueba_normalizacion.xlsx "c:\ruta\a\tu\carpeta\de\archivos\excel\"

# Opción 2: Usar el archivo directamente desde la raíz del proyecto
# (Django debe tener acceso a leerlo)
```

### 2. **Abrir el frontend**

Abre tu navegador en: `http://127.0.0.1:8000/automatizacion/`

### 3. **Crear nuevo proceso Excel**

1. Click en **"Nuevo Proceso"**
2. Selecciona **"Tipo: Excel"**
3. Click en **"Elegir archivo"**
4. Selecciona: `datos_prueba_normalizacion.xlsx`

### 4. **Seleccionar hojas**

Marca las hojas que quieras probar:
- ☑️ Empleados
- ☑️ Productos
- ☑️ Ventas

### 5. **Seleccionar columnas**

Para cada hoja, marca las columnas con datos problemáticos:
- En **Empleados**: Edad, Salario_Mensual, Fecha_Ingreso, Activo, Horas_Trabajo
- En **Productos**: Precio_Unitario, Stock_Disponible, Peso_KG, Fecha_Ultimo_Ingreso
- En **Ventas**: Cantidad, Precio_Total, Fecha_Venta, Cliente_ID

### 6. **Guardar y ejecutar**

1. Dale un nombre: **"Test Normalización Excel"**
2. Click en **"Guardar"**
3. Click en **"Ejecutar Proceso"**

---

## 👀 QUÉ VERÁS DURANTE LA EJECUCIÓN

### 🖥️ En la Terminal de Django:

```
🚀 Procesando hoja Excel: 'Empleados'
📊 DEBUG: Hoja leída. Shape original: (10, 8)
⚠️ Advertencias de normalización antes de insertar: [
    {'column': 'Edad', 'count': 5, 'example': 'treinta y cinco'},
    {'column': 'Salario_Mensual', 'count': 5, 'example': 'dos mil quinientos'},
    {'column': 'Fecha_Ingreso', 'count': 4, 'example': 'fecha_invalida'},
    {'column': 'Activo', 'count': 4, 'example': 'Si'},
    {'column': 'Horas_Trabajo', 'count': 3, 'example': 'N/A'}
]

⚠️ Normalización de datos para 'Test_Normalizacion_Excel_Empleados':
  • Columna 'Edad': 5 valores inválidos convertidos a NULL
    Ejemplo: 'treinta y cinco'
  • Columna 'Salario_Mensual': 5 valores inválidos convertidos a NULL
    Ejemplo: 'dos mil quinientos'
  • Columna 'Fecha_Ingreso': 4 valores inválidos convertidos a NULL
    Ejemplo: 'fecha_invalida'
  • Columna 'Activo': 4 valores inválidos convertidos a NULL
    Ejemplo: 'Si'
  • Columna 'Horas_Trabajo': 3 valores inválidos convertidos a NULL
    Ejemplo: 'N/A'

✅ Tabla Test_Normalizacion_Excel_Empleados creada exitosamente
   📊 Columnas: ['ID_Empleado', 'Nombre_Completo', 'Edad', 'Salario_Mensual', ...]
   📈 Filas insertadas: 10
```

---

## 🔍 VERIFICACIÓN EN SQL SERVER

### Consulta para ver los datos normalizados:

```sql
-- Ver estructura de la tabla
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Test_Normalizacion_Excel_Empleados';

-- Esperado:
-- ID_Empleado     → float      → YES
-- Nombre_Completo → nvarchar   → YES
-- Edad            → float      → YES  ⚠️ (antes era texto mixto)
-- Salario_Mensual → float      → YES  ⚠️ (antes era texto mixto)
-- Fecha_Ingreso   → datetime   → YES  ⚠️ (antes era texto mixto)
-- Activo          → float      → YES  ⚠️ (antes era booleano/texto)
-- Horas_Trabajo   → float      → YES  ⚠️ (antes era texto/número)

-- Ver datos con NULLs generados por normalización
SELECT * FROM Test_Normalizacion_Excel_Empleados;

-- Contar NULLs por columna
SELECT 
    COUNT(*) - COUNT(Edad) AS NULLs_Edad,
    COUNT(*) - COUNT(Salario_Mensual) AS NULLs_Salario,
    COUNT(*) - COUNT(Fecha_Ingreso) AS NULLs_Fecha,
    COUNT(*) - COUNT(Activo) AS NULLs_Activo,
    COUNT(*) - COUNT(Horas_Trabajo) AS NULLs_Horas
FROM Test_Normalizacion_Excel_Empleados;

-- Esperado:
-- NULLs_Edad: 5
-- NULLs_Salario: 5
-- NULLs_Fecha: 4
-- NULLs_Activo: 4
-- NULLs_Horas: 3
```

---

## ✅ RESULTADO ESPERADO

### Datos ANTES de la normalización (en Excel):

| Edad | Salario | Tipo |
|------|---------|------|
| "treinta y cinco" | "dos mil quinientos" | ❌ Texto |
| "N/A" | "#ERROR" | ❌ Error |
| "abc" | "GRATIS" | ❌ Inválido |

### Datos DESPUÉS de la normalización (en SQL Server):

| Edad | Salario | Tipo |
|------|---------|------|
| NULL | NULL | ✅ float |
| NULL | NULL | ✅ float |
| NULL | NULL | ✅ float |

### Valores válidos preservados:

| Edad (Excel) | Edad (SQL) | Salario (Excel) | Salario (SQL) |
|--------------|-----------|----------------|--------------|
| 25 | 25.0 | "1500.50" | 1500.50 |
| "30" | 30.0 | "2000" | 2000.00 |
| 45 | 45.0 | "3500.75" | 3500.75 |
| "50.5" | 50.5 | "4000.00" | 4000.00 |

---

## 🎯 CHECKLIST DE VALIDACIÓN

Al finalizar la prueba, verifica:

- ✅ **Terminal muestra warnings** con detalle de columnas/valores normalizados
- ✅ **Tabla creada en SQL Server** con el nombre correcto
- ✅ **Tipos de datos correctos**: float para números, datetime para fechas, nvarchar para strings
- ✅ **Valores inválidos convertidos a NULL** en la base de datos
- ✅ **Valores válidos preservados** (incluso si venían como strings)
- ✅ **Logs del proceso** muestran resumen de normalización
- ✅ **No hay errores** durante la ejecución

---

## 🚨 PROBLEMAS COMUNES

| Problema | Causa | Solución |
|----------|-------|----------|
| No veo warnings en terminal | Todos los datos son válidos | Verifica que estás usando el archivo correcto con datos problemáticos |
| Error al crear tabla | Permisos insuficientes | Verifica configuración de SQL Server |
| Archivo no encontrado | Ruta incorrecta | Copia el archivo a la carpeta configurada en Django |
| Proceso no inicia | Hojas no seleccionadas | Marca al menos una hoja antes de guardar |

---

## 📝 NOTAS IMPORTANTES

1. **La normalización NO se ve en el frontend durante la creación del proceso**
   - Solo se activa cuando EJECUTAS el proceso
   
2. **Los warnings aparecen en la terminal de Django**, no en el navegador
   
3. **Los valores NULL en SQL Server** son el resultado de la normalización

4. **El proceso continúa aunque haya valores inválidos** (modo tolerante)

5. **Si quieres modo estricto** (que lance error), modifica el código en `models.py`:
   ```python
   df_normalized, issues = normalize_df_for_sql(df_datos, strict=True)  # ⚠️ Fallará si hay errores
   ```

---

¡Tu archivo está listo para probar! 🎉
