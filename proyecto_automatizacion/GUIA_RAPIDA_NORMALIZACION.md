# 🚀 Guía Rápida: Normalización de Valores Vacíos

## 📖 Referencia Rápida de Tipos SQL y Defaults

### **Tipos Numéricos**

| Tipo SQL | Ejemplo Default | Descripción |
|----------|----------------|-------------|
| `INT` | `0` | Entero de 32 bits |
| `BIGINT` | `0` | Entero de 64 bits |
| `SMALLINT` | `0` | Entero de 16 bits |
| `TINYINT` | `0` | Entero de 8 bits (0-255) |
| `FLOAT` | `0.0` | Número decimal de precisión variable |
| `REAL` | `0.0` | Número decimal de precisión simple |
| `DECIMAL(10,2)` | `0.00` | Número decimal de precisión fija |
| `NUMERIC(10,2)` | `0.00` | Igual que DECIMAL |
| `MONEY` | `0.00` | Valor monetario |

**Ejemplo de Uso**:
```json
{
  "cantidad": {
    "sql_type": "INT",
    "nullable": false,
    "default_value": "0"
  }
}
```

---

### **Tipos de Fecha y Hora**

| Tipo SQL | Ejemplo Default | Descripción |
|----------|----------------|-------------|
| `DATE` | `GETDATE()` | Fecha (sin hora) |
| `DATETIME` | `GETDATE()` | Fecha y hora |
| `DATETIME2` | `GETDATE()` | Fecha y hora con mayor precisión |
| `SMALLDATETIME` | `GETDATE()` | Fecha y hora con precisión de minutos |
| `TIME` | `GETDATE()` | Solo hora |
| `TIMESTAMP` | `GETDATE()` | Marca temporal automática |

**Ejemplo de Uso**:
```json
{
  "fecha_registro": {
    "sql_type": "DATETIME",
    "nullable": false,
    "default_value": "GETDATE()"
  }
}
```

**Nota**: `GETDATE()` usa la fecha/hora **del servidor SQL Server**, no del servidor Django.

---

### **Tipos de Texto**

| Tipo SQL | Ejemplo Default | Descripción |
|----------|----------------|-------------|
| `VARCHAR(255)` | `''` | Texto ASCII de longitud variable |
| `NVARCHAR(255)` | `''` | Texto Unicode de longitud variable |
| `CHAR(10)` | `''` | Texto ASCII de longitud fija |
| `NCHAR(10)` | `''` | Texto Unicode de longitud fija |
| `TEXT` | `''` | Texto ASCII largo (deprecado) |
| `NTEXT` | `''` | Texto Unicode largo (deprecado) |

**Ejemplo de Uso**:
```json
{
  "nombre": {
    "sql_type": "NVARCHAR(255)",
    "nullable": false,
    "default_value": ""
  },
  "codigo": {
    "sql_type": "VARCHAR(50)",
    "nullable": false,
    "default_value": "'PENDIENTE'"
  }
}
```

**Nota**: Para strings con contenido específico, usar comillas simples: `"'valor'"` → `"valor"`

---

### **Tipos Booleanos**

| Tipo SQL | Ejemplo Default | Descripción |
|----------|----------------|-------------|
| `BIT` | `0` (False) | Valor booleano (0/1) |

**Ejemplo de Uso**:
```json
{
  "activo": {
    "sql_type": "BIT",
    "nullable": false,
    "default_value": "0"
  }
}
```

**Conversión**:
- `0` → `False`
- `1` → `True`
- `'true'`, `'yes'`, `'sí'` → `1`
- `'false'`, `'no'` → `0`

---

## 🎯 Matriz de Decisión: nullable + default_value

| Escenario | nullable | default_value | Celda Vacía → |
|-----------|----------|---------------|---------------|
| **Caso 1** | ❌ False | `'0'` (INT) | → `0` |
| **Caso 2** | ❌ False | `'GETDATE()'` (DATE) | → Fecha actual |
| **Caso 3** | ❌ False | `"'PENDIENTE'"` (VARCHAR) | → `'PENDIENTE'` |
| **Caso 4** | ❌ False | `None` (VARCHAR) | → `''` (vacío) |
| **Caso 5** | ❌ False | `None` (INT) | → `0` |
| **Caso 6** | ❌ False | `None` (DATE) | → Fecha actual |
| **Caso 7** | ✅ True | (cualquiera) | → `NULL` |

---

## 🛠️ Recetas Comunes

### **Receta 1: Cantidad con Cero por Defecto**

```json
{
  "cantidad": {
    "sql_type": "INT",
    "nullable": false,
    "default_value": "0"
  }
}
```

**Resultado**:
- Celda con valor: `5` → `5`
- Celda vacía: `""` → `0`
- Celda con texto: `"abc"` → `0`

---

### **Receta 2: Precio Siempre con Decimales**

```json
{
  "precio": {
    "sql_type": "DECIMAL(10,2)",
    "nullable": false,
    "default_value": "0.00"
  }
}
```

**Resultado**:
- Celda con valor: `99.99` → `99.99`
- Celda vacía: `""` → `0.00`
- Celda con valor sin decimales: `50` → `50.00`

---

### **Receta 3: Fecha de Registro Automática**

```json
{
  "fecha_registro": {
    "sql_type": "DATETIME",
    "nullable": false,
    "default_value": "GETDATE()"
  }
}
```

**Resultado**:
- Celda con fecha: `2024-01-15` → `2024-01-15 00:00:00`
- Celda vacía: `""` → `2025-10-22 10:30:45` (fecha actual)

---

### **Receta 4: Código con Marcador de Pendiente**

```json
{
  "codigo": {
    "sql_type": "VARCHAR(50)",
    "nullable": false,
    "default_value": "'PENDIENTE'"
  }
}
```

**Resultado**:
- Celda con valor: `A001` → `A001`
- Celda vacía: `""` → `PENDIENTE`

**Nota**: Las comillas simples dentro del string: `"'PENDIENTE'"` se procesan como `PENDIENTE`

---

### **Receta 5: Texto Opcional con NULL**

```json
{
  "descripcion": {
    "sql_type": "NVARCHAR(255)",
    "nullable": true,
    "default_value": null
  }
}
```

**Resultado**:
- Celda con valor: `"Descripción larga"` → `"Descripción larga"`
- Celda vacía: `""` → `NULL` (en SQL)

---

### **Receta 6: Booleano por Defecto Inactivo**

```json
{
  "activo": {
    "sql_type": "BIT",
    "nullable": false,
    "default_value": "0"
  }
}
```

**Resultado**:
- Celda con `TRUE`, `true`, `1`, `yes`: → `1` (True)
- Celda con `FALSE`, `false`, `0`, `no`: → `0` (False)
- Celda vacía: `""` → `0` (False)

---

### **Receta 7: String con Espacio (No Vacío)**

```json
{
  "observaciones": {
    "sql_type": "NVARCHAR(500)",
    "nullable": false,
    "default_value": "' '"
  }
}
```

**Resultado**:
- Celda con valor: `"Observación importante"` → `"Observación importante"`
- Celda vacía: `""` → `" "` (un espacio)

**Uso**: Cuando necesitas distinguir entre "sin datos" (espacio) y datos reales.

---

## 🔍 Diagnóstico de Problemas

### **Problema 1: Error "Cannot insert NULL"**

**Síntoma**:
```
Cannot insert the value NULL into column 'cantidad', column does not allow nulls.
```

**Solución**:
```json
{
  "cantidad": {
    "nullable": false,  // ← Asegurar que está en false
    "default_value": "0"  // ← Proporcionar default
  }
}
```

---

### **Problema 2: Strings Vacíos en Columnas Numéricas**

**Síntoma**:
```
Conversion failed when converting the varchar value '' to data type int.
```

**Solución**:
- ✅ Verificar que `sql_type` sea `INT` (no `VARCHAR`)
- ✅ El sistema ahora convierte automáticamente

---

### **Problema 3: Fechas con Formato Incorrecto**

**Síntoma**:
```
Conversion failed when converting date and/or time from character string.
```

**Solución**:
```json
{
  "fecha": {
    "sql_type": "DATE",  // ← Asegurar tipo correcto
    "default_value": "GETDATE()"  // ← Usar GETDATE() para vacías
  }
}
```

---

### **Problema 4: Comillas en Defaults**

**Síntoma**: El default `'texto'` se inserta como `'texto'` (con comillas)

**Solución**:
```json
// ❌ Incorrecto:
"default_value": "'texto'"

// ✅ Correcto:
"default_value": "texto"

// ✅ Si necesitas comillas literales:
"default_value": "\"'texto'\""
```

---

## 📊 Tabla de Equivalencias: Pandas → SQL Server

| Pandas dtype | SQL Server | Default Sugerido |
|--------------|------------|------------------|
| `int64`, `int32` | `INT` | `0` |
| `float64`, `float32` | `FLOAT` | `0.0` |
| `datetime64[ns]` | `DATETIME` | `GETDATE()` |
| `object` (texto) | `NVARCHAR(255)` | `''` |
| `bool` | `BIT` | `0` |
| `object` (mixto) | `NVARCHAR(500)` | `''` |

---

## ⚡ Comandos Rápidos de Verificación

### **Verificar Tipos Detectados**

En la UI `/multi-config/`, expandir la hoja para ver:
```
📊 Columna: cantidad
   Tipo detectado: INT (int64)
   Nullable: ☐ No permite NULL
   Default: [0] (sugerido)
```

### **Verificar Datos Insertados en SQL Server**

```sql
-- Contar registros insertados
SELECT COUNT(*) FROM nombre_tabla;

-- Ver primeros 10 registros
SELECT TOP 10 * FROM nombre_tabla;

-- Verificar valores NULL
SELECT * FROM nombre_tabla WHERE columna IS NULL;

-- Verificar defaults aplicados
SELECT * FROM nombre_tabla WHERE columna = 0;  -- Para INT
SELECT * FROM nombre_tabla WHERE columna = '';  -- Para VARCHAR
```

---

## 🎯 Checklist Final

Antes de ejecutar un proceso:

- [ ] ✅ Tipos SQL coinciden con los datos (INT para números, DATE para fechas)
- [ ] ✅ Nullable configurado según necesidad (False = no permite NULL)
- [ ] ✅ Default_value configurado para columnas con nullable=False
- [ ] ✅ Default_value tiene el formato correcto:
  - Números: `"0"`, `"0.0"`
  - Fechas: `"GETDATE()"`
  - Texto: `"texto"` o `"'texto con espacios'"`
- [ ] ✅ Preview de datos verificado en la UI
- [ ] ✅ Nombre de tabla SQL es válido (sin espacios, caracteres especiales)

---

## 📚 Recursos Adicionales

- **Documentación Completa**: `MEJORA_NORMALIZACION_VALORES_VACIOS.md`
- **Resumen Técnico**: `RESUMEN_NORMALIZACION_VALORES_VACIOS.md`
- **Ejemplo Práctico**: `EJEMPLO_NORMALIZACION_VALORES_VACIOS.md`
- **Tests**: `test_normalizacion_defaults.py`

---

**🎉 ¡Listo para procesar tus archivos Excel con normalización robusta!**
