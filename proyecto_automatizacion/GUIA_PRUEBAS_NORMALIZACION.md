# 🧪 GUÍA DE PRUEBA END-TO-END: Normalización de Datos SQL

Esta guía te permitirá probar la nueva funcionalidad de normalización y validación de datos antes de la carga a SQL Server.

## ✅ Pruebas Completadas

### 1. Prueba Unitaria de la Función `normalize_df_for_sql()`

**Estado**: ✅ COMPLETADA

**Comando**:
```powershell
cd "c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion"
python test_sql_normalization.py
```

**Resultados**:
- ✅ Valores numéricos en formato string se convierten a float
- ✅ Valores inválidos ("abc", "N/A") se convierten a NULL
- ✅ Fechas inválidas se convierten a NULL  
- ✅ Cadenas vacías y espacios se convierten a NULL
- ✅ Modo estricto detecta y reporta todos los errores

---

## 🔄 Prueba End-to-End con Proceso SQL Real

### Paso 1: Preparar Datos de Prueba en SQL Server

Primero, crea una tabla de prueba en tu base de datos origen con datos problemáticos:

```sql
-- Conectar a tu base de datos SQL Server origen
USE [TuBaseDatosOrigen];
GO

-- Crear tabla de prueba con datos problemáticos
CREATE TABLE TestNormalizacion (
    ID INT,
    Nombre NVARCHAR(100),
    Edad NVARCHAR(50),  -- Guardamos como string para simular datos sucios
    Salario NVARCHAR(50),
    FechaIngreso NVARCHAR(50),
    Activo NVARCHAR(10)
);
GO

-- Insertar datos problemáticos (simulando exportación de Excel/CSV con errores)
INSERT INTO TestNormalizacion VALUES
    (1, 'Juan Pérez', '25', '1500.50', '2020-01-15', 'True'),
    (2, 'María López', '30', '2000', '2021-06-20', '1'),
    (3, 'Carlos Gómez', 'abc', 'N/A', 'fecha_invalida', 'Si'),
    (4, 'Ana Martínez', '', '', '', ''),
    (5, 'Pedro Ruiz', NULL, NULL, NULL, NULL),
    (6, 'Laura Torres', '45.5', '3500.75', '2023-03-10', '0'),
    (7, 'Roberto Díaz', '50', '4000', '2024-05-01', 'False');
GO

-- Verificar datos insertados
SELECT * FROM TestNormalizacion;
```

### Paso 2: Crear Proceso de Migración en Django

1. **Abre tu navegador** y ve a: `http://127.0.0.1:8000/automatizacion/`

2. **Selecciona tu conexión SQL Server**

3. **Navega a la tabla `TestNormalizacion`**

4. **Selecciona todas las columnas**

5. **Dale un nombre al proceso**: "Test Normalización Datos"

6. **Guarda el proceso**

### Paso 3: Ejecutar el Proceso y Verificar Logs

1. **Ejecuta el proceso** desde la interfaz web

2. **Revisa la consola del servidor Django** (terminal donde corre `runserver`)

Deberías ver mensajes como:
```
⚠️ Advertencias de normalización antes de insertar: [
    {'column': 'Edad', 'count': 1, 'example': 'abc'},
    {'column': 'Salario', 'count': 1, 'example': 'N/A'},
    {'column': 'FechaIngreso', 'count': 1, 'example': 'fecha_invalida'}
]
```

### Paso 4: Verificar Tabla Destino en SQL Server

Conecta a tu base de datos destino y verifica los resultados:

```sql
USE DestinoAutomatizacion;
GO

-- Ver estructura de la tabla creada
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME LIKE '%TestNormalizacion%'
ORDER BY ORDINAL_POSITION;

-- Ver datos insertados
SELECT * FROM [Test Normalización Datos_TestNormalizacion];

-- Verificar valores NULL generados por la normalización
SELECT 
    COUNT(*) as TotalFilas,
    COUNT(Edad) as EdadNoNulos,
    COUNT(Salario) as SalarioNoNulos,
    COUNT(FechaIngreso) as FechaNoNulos
FROM [Test Normalización Datos_TestNormalizacion];
```

### Resultados Esperados:

| Campo | Valor Original | Valor en Destino | Explicación |
|-------|---------------|------------------|-------------|
| Edad = 'abc' | 'abc' | NULL | Valor no numérico → NULL |
| Salario = 'N/A' | 'N/A' | NULL | Valor no numérico → NULL |
| FechaIngreso = 'fecha_invalida' | 'fecha_invalida' | NULL | Fecha inválida → NULL |
| Edad = '' | '' (cadena vacía) | NULL | Cadena vacía → NULL |
| Edad = NULL | NULL | NULL | NULL preservado |
| Edad = '25' | '25' (string) | 25.0 (float) | String convertido a número |
| Salario = '1500.50' | '1500.50' (string) | 1500.50 (float) | String convertido a número |

---

## 🔍 Qué Observar Durante la Prueba

### En la Consola de Django:
1. ✅ Mensaje "🔄 APLICANDO NORMALIZACIÓN..."
2. ✅ Lista de advertencias si hay valores inválidos
3. ✅ Mensaje "✅ Inserción masiva exitosa"
4. ❌ Si hay errores, se mostrarán claramente

### En SQL Server Destino:
1. ✅ Tabla creada con tipos de datos correctos (INT, FLOAT, DATETIME2, NVARCHAR)
2. ✅ Valores inválidos convertidos a NULL
3. ✅ Valores numéricos en formato string convertidos correctamente
4. ✅ Fechas válidas convertidas a DATETIME2

### En la Interfaz Web:
1. ✅ Proceso se marca como "Completado"
2. ✅ Log de ejecución muestra registros insertados
3. ⚠️ Si hay advertencias, aparecerán en el log

---

## 🎯 Casos de Prueba Adicionales

### Caso 1: Modo Estricto (rechazar si hay errores)

Si quieres que el proceso falle cuando hay datos inválidos:

**Archivo**: `automatizacion/models.py` línea ~1520

Cambiar:
```python
df_normalized, normalization_issues = normalize_df_for_sql(df_datos, strict=False)
```

Por:
```python
df_normalized, normalization_issues = normalize_df_for_sql(df_datos, strict=True)
```

Esto hará que el proceso lance un error y NO inserte datos si detecta valores inválidos.

### Caso 2: Datos con Decimales Problemáticos

```sql
INSERT INTO TestNormalizacion VALUES
    (8, 'Test Decimal', '25,5', '1.500,75', '2024-01-01', '1');  -- Comas como separadores
```

**Resultado Esperado**: La coma NO es válida en Python/SQL Server, debería convertirse a NULL.

### Caso 3: Fechas en Diferentes Formatos

```sql
INSERT INTO TestNormalizacion VALUES
    (9, 'Test Fecha 1', '30', '2500', '15/01/2024', '1'),  -- Formato DD/MM/YYYY
    (10, 'Test Fecha 2', '28', '2300', '2024-01-15', '1');  -- Formato YYYY-MM-DD
```

**Resultado Esperado**: Ambos formatos deberían detectarse y convertirse a DATETIME2.

---

## 📊 Verificación de Logs en Base de Datos

Para ver los logs del proceso:

```sql
USE DestinoAutomatizacion;
GO

-- Ver últimos logs de migración
SELECT TOP 10 
    proceso_id,
    nombre_proceso,
    estado,
    registros_procesados,
    registros_exitosos,
    errores_count,
    fecha_inicio,
    fecha_fin
FROM ProcesoLog
ORDER BY fecha_inicio DESC;
```

---

## 🚨 Solución de Problemas

### Error: "No se pudo importar sql_utils.normalize_df_for_sql"

**Causa**: El archivo `sql_utils.py` no existe o tiene errores de sintaxis.

**Solución**:
```powershell
# Verificar que el archivo existe
ls "c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion\automatizacion\sql_utils.py"

# Verificar sintaxis
python -m py_compile "automatizacion/sql_utils.py"
```

### Error: "TypeError: cannot convert the series to <class 'float'>"

**Causa**: Tipo de dato no compatible con la conversión.

**Solución**: Ya está manejado en la función con `try/except`, pero revisa el traceback completo.

### Warning: "Normalization errors detected"

**Esto es normal** si tienes datos problemáticos. La normalización los convierte a NULL automáticamente.

Si quieres rechazar el proceso completo cuando esto ocurre, usa `strict=True`.

---

## ✅ Checklist de Verificación

- [ ] Prueba unitaria ejecutada exitosamente
- [ ] Tabla de prueba creada en SQL Server origen
- [ ] Proceso de migración creado en Django
- [ ] Proceso ejecutado sin errores críticos
- [ ] Advertencias de normalización aparecen en logs
- [ ] Tabla destino creada con estructura correcta
- [ ] Valores inválidos convertidos a NULL
- [ ] Valores válidos insertados correctamente
- [ ] Tipos de datos SQL correctos (INT, FLOAT, DATETIME2)

---

## 📚 Documentación de la Función

```python
from automatizacion.sql_utils import normalize_df_for_sql

# Uso básico
df_normalized, issues = normalize_df_for_sql(df_original, strict=False)

# Modo estricto (lanza error si hay problemas)
try:
    df_normalized, issues = normalize_df_for_sql(df_original, strict=True)
except ValueError as e:
    print(f"Errores de normalización: {e}")
```

**Parámetros**:
- `df`: pandas DataFrame a normalizar
- `strict`: Si es True, lanza ValueError al detectar valores inválidos

**Retorna**:
- `df_normalized`: DataFrame con valores normalizados (None = NULL)
- `issues`: Lista de diccionarios con problemas detectados

---

¿Necesitas ayuda adicional o quieres probar algún caso específico?
