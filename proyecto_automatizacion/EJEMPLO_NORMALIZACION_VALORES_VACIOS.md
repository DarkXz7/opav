# 📊 Ejemplo Práctico: Normalización de Valores Vacíos

## 🎯 Escenario Real

Tienes un Excel con datos de ventas que tiene **celdas vacías** en diferentes columnas:

### **Archivo Excel Original: `ventas.xlsx`**

| fecha | codigo | producto | cantidad | precio | activo |
|-------|--------|----------|----------|--------|--------|
| 2024-01-15 | A001 | Laptop | 5 | 999.99 | TRUE |
| **(vacío)** | A002 | Mouse | **(vacío)** | 25.50 | TRUE |
| 2024-01-17 | **(vacío)** | Teclado | 10 | **(vacío)** | **(vacío)** |
| 2024-01-18 | A004 | Monitor | 3 | 450.00 | FALSE |

---

## ⚙️ Configuración en la UI

Después de subir el Excel, vas a `/multi-config/` y configuras:

### **Hoja: "ventas"**

| Columna | Tipo SQL | Nullable | Default |
|---------|----------|----------|---------|
| ✅ fecha | DATE | ❌ No | `GETDATE()` |
| ✅ codigo | NVARCHAR(50) | ❌ No | `'SIN_CODIGO'` |
| ✅ producto | NVARCHAR(255) | ❌ No | `''` |
| ✅ cantidad | INT | ❌ No | `0` |
| ✅ precio | FLOAT | ❌ No | `0.0` |
| ✅ activo | BIT | ❌ No | `0` (False) |

**Nombre de la tabla**: `ventas_procesadas`

---

## 🔄 Procesamiento Paso a Paso

### **PASO 1: Lectura del Excel con pandas**

```python
df_original = pd.read_excel('ventas.xlsx', sheet_name='ventas')
```

**DataFrame Original**:
```
        fecha codigo producto cantidad precio activo
0  2024-01-15   A001   Laptop        5 999.99   TRUE
1         NaN   A002    Mouse      NaN  25.50   TRUE
2  2024-01-17    NaN  Teclado       10    NaN    NaN
3  2024-01-18   A004  Monitor        3 450.00  FALSE
```

---

### **PASO 2: normalize_df_for_sql() - Conversión de Tipos**

```python
from automatizacion.sql_utils import normalize_df_for_sql

df_normalized, issues = normalize_df_for_sql(df_original, strict=False)
```

**DataFrame Normalizado** (valores inválidos → None):
```
        fecha codigo producto  cantidad  precio  activo
0  2024-01-15   A001   Laptop       5.0  999.99     1.0
1         NaT   A002    Mouse       NaN   25.50     1.0  
2  2024-01-17   None  Teclado      10.0     NaN     NaN  <- None detectados
3  2024-01-18   A004  Monitor       3.0  450.00     0.0
```

**Issues Reportados**:
```python
[
    {'column': 'cantidad', 'count': 1, 'example': 'vacío'},
    {'column': 'precio', 'count': 1, 'example': 'vacío'},
    {'column': 'activo', 'count': 1, 'example': 'vacío'}
]
```

---

### **PASO 3: apply_default_values_from_mappings() - Aplicar Defaults**

```python
from automatizacion.sql_utils import apply_default_values_from_mappings

column_mappings = {
    'fecha': {'sql_type': 'DATE', 'nullable': False, 'default_value': 'GETDATE()'},
    'codigo': {'sql_type': 'NVARCHAR(50)', 'nullable': False, 'default_value': "'SIN_CODIGO'"},
    'producto': {'sql_type': 'NVARCHAR(255)', 'nullable': False, 'default_value': None},
    'cantidad': {'sql_type': 'INT', 'nullable': False, 'default_value': '0'},
    'precio': {'sql_type': 'FLOAT', 'nullable': False, 'default_value': '0.0'},
    'activo': {'sql_type': 'BIT', 'nullable': False, 'default_value': '0'}
}

df_final = apply_default_values_from_mappings(df_normalized, column_mappings)
```

**DataFrame Final** (con defaults aplicados):
```
                      fecha       codigo producto  cantidad  precio  activo
0 2024-01-15 00:00:00.000  A001       Laptop       5.0  999.99     1.0
1 2025-10-22 10:00:00.000  A002       Mouse        0.0   25.50     1.0  <- fecha=GETDATE()
2 2024-01-17 00:00:00.000  SIN_CODIGO Teclado     10.0    0.0     0.0  <- codigo='SIN_CODIGO', precio=0
3 2024-01-18 00:00:00.000  A004       Monitor      3.0  450.00     0.0
```

**Cambios Aplicados**:
- 🔄 Fila 1: `fecha` vacía → **2025-10-22** (GETDATE())
- 🔄 Fila 1: `cantidad` vacía → **0** (default)
- 🔄 Fila 2: `codigo` vacío → **'SIN_CODIGO'** (default personalizado)
- 🔄 Fila 2: `precio` vacío → **0.0** (default)
- 🔄 Fila 2: `activo` vacío → **0** (False, default)

---

### **PASO 4: Inserción en SQL Server**

```sql
-- Tabla creada automáticamente:
CREATE TABLE [ventas_procesadas] (
    [fecha]    DATE NOT NULL DEFAULT GETDATE(),
    [codigo]   NVARCHAR(50) NOT NULL DEFAULT 'SIN_CODIGO',
    [producto] NVARCHAR(255) NOT NULL DEFAULT '',
    [cantidad] INT NOT NULL DEFAULT 0,
    [precio]   FLOAT NOT NULL DEFAULT 0.0,
    [activo]   BIT NOT NULL DEFAULT 0
);

-- Datos insertados:
INSERT INTO [ventas_procesadas] 
VALUES 
  ('2024-01-15', 'A001', 'Laptop', 5, 999.99, 1),
  ('2025-10-22', 'A002', 'Mouse', 0, 25.50, 1),     -- ✅ defaults aplicados
  ('2024-01-17', 'SIN_CODIGO', 'Teclado', 10, 0.0, 0),  -- ✅ defaults aplicados
  ('2024-01-18', 'A004', 'Monitor', 3, 450.00, 0);

-- Resultado final en la tabla:
SELECT * FROM [ventas_procesadas];
```

**Tabla SQL Server**:
```
| fecha       | codigo     | producto | cantidad | precio | activo |
|-------------|------------|----------|----------|--------|--------|
| 2024-01-15  | A001       | Laptop   | 5        | 999.99 | 1      |
| 2025-10-22  | A002       | Mouse    | 0        | 25.50  | 1      | ← valores corregidos
| 2024-01-17  | SIN_CODIGO | Teclado  | 10       | 0.0    | 0      | ← valores corregidos
| 2024-01-18  | A004       | Monitor  | 3        | 450.00 | 0      |
```

✅ **Sin errores de inserción**
✅ **Sin valores NULL no permitidos**
✅ **Sin strings vacíos en campos numéricos**
✅ **Todos los defaults aplicados correctamente**

---

## 🎯 Comparación: Antes vs Después

### **❌ ANTES (Sin normalización robusta)**

```sql
-- ❌ Intentaba insertar:
INSERT INTO ventas VALUES ('', 'A002', 'Mouse', '', 25.50, 'TRUE');
                         --^^ ERROR: fecha vacía            ^^ ERROR: string en INT
```

**Error**:
```
❌ Conversion failed when converting the varchar value '' to data type int.
❌ Cannot insert NULL into column 'fecha' (nullable=False)
```

---

### **✅ DESPUÉS (Con normalización robusta)**

```sql
-- ✅ Inserta correctamente:
INSERT INTO ventas VALUES ('2025-10-22', 'A002', 'Mouse', 0, 25.50, 1);
                        -- ✅ GETDATE()            ✅ 0 (default)   ✅ 1 (True convertido)
```

**Resultado**:
```
✅ Inserción masiva exitosa. Registros afectados: 4
✅ Valores por defecto aplicados según column_mappings
```

---

## 🔄 Caso Especial: Columnas Nullable=True

Si configuras una columna como **nullable=True**, el comportamiento cambia:

### **Configuración Alternativa**:

| Columna | Tipo SQL | Nullable | Default |
|---------|----------|----------|---------|
| cantidad | INT | ✅ **Sí** | `0` |

### **Resultado**:

```python
# DataFrame antes de defaults:
cantidad: [5.0, NaN, 10.0]

# DataFrame después de defaults (nullable=True):
cantidad: [5.0, None, 10.0]  # ✅ Mantiene None (se insertará como NULL)

# SQL Server:
INSERT INTO ventas (cantidad) VALUES (5);
INSERT INTO ventas (cantidad) VALUES (NULL);  -- ✅ Permite NULL
INSERT INTO ventas (cantidad) VALUES (10);
```

**Nota**: Cuando `nullable=True`, los valores vacíos se mantienen como `NULL` en SQL, **ignorando el default_value**.

---

## 📋 Checklist de Verificación

Para verificar que tu proceso está configurado correctamente:

1. ✅ **Subir Excel** → Ver preview de datos
2. ✅ **Configurar tipo SQL** → Verificar que coincide con los datos
3. ✅ **Configurar nullable**:
   - ❌ No → **Requiere default_value**
   - ✅ Sí → Permite NULL, ignora default_value
4. ✅ **Configurar default_value**:
   - INT/FLOAT → `0`, `0.0`, o valor numérico
   - DATE → `GETDATE()` o fecha específica
   - VARCHAR → `''`, `' '`, o texto entre comillas `'texto'`
5. ✅ **Ejecutar proceso** → Ver log de valores aplicados
6. ✅ **Verificar SQL Server** → Confirmar datos insertados correctamente

---

## 🎓 Tips Avanzados

### **Tip 1: Usar GETDATE() para Fecha de Carga**

```
default_value: GETDATE()
→ Todas las fechas vacías usarán la fecha actual de procesamiento
```

### **Tip 2: Códigos Automáticos**

```
default_value: 'PENDIENTE'
→ Todos los códigos vacíos se marcarán como 'PENDIENTE' para revisión manual
```

### **Tip 3: Valores Booleanos**

```
sql_type: BIT
default_value: 0
→ Campos vacíos se marcan como False (0)
```

### **Tip 4: Decimales con Precisión**

```
sql_type: DECIMAL(10,2)
default_value: 0.00
→ Precios/cantidades vacías se inicializan en 0.00
```

---

## 🚀 Próximos Pasos

1. **Probar con tu Excel real**:
   - Sube tu archivo
   - Configura tipos SQL y defaults
   - Ejecuta proceso
   - Verifica resultados en SQL Server

2. **Ajustar configuración**:
   - Si hay errores, revisa tipos SQL
   - Ajusta defaults según tus necesidades
   - Vuelve a ejecutar

3. **Guardar proceso**:
   - Una vez configurado correctamente
   - El sistema recuerda la configuración
   - Próximas ejecuciones usarán los mismos defaults

---

**¿Necesitas ayuda?** Revisa:
- `RESUMEN_NORMALIZACION_VALORES_VACIOS.md` - Resumen técnico
- `MEJORA_NORMALIZACION_VALORES_VACIOS.md` - Documentación completa
- `test_normalizacion_defaults.py` - Ejemplos de código
