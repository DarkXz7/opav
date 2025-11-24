# 🧪 Plan de Pruebas: Normalización de Valores Vacíos

## 📋 Objetivo

Verificar que el sistema normaliza correctamente los valores vacíos en archivos Excel según la configuración de `nullable` y `default_value`.

---

## 🎯 Casos de Prueba

### **Test Case 1: INT con nullable=False y default=0**

**Configuración**:
```json
{
  "cantidad": {
    "sql_type": "INT",
    "nullable": false,
    "default_value": "0"
  }
}
```

**Excel de Entrada**:
```
| cantidad |
|----------|
| 10       |
|          | ← vacío
| abc      | ← inválido
| 25       |
```

**Resultado Esperado en SQL**:
```
| cantidad |
|----------|
| 10       |
| 0        | ← default aplicado
| 0        | ← convertido a default
| 25       |
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test;
-- Debe mostrar 4 registros, sin NULL, sin errores

SELECT * FROM tabla_test WHERE cantidad = 0;
-- Debe mostrar 2 registros (los que estaban vacíos/inválidos)
```

✅ **Criterio de Éxito**: 4 registros insertados, 2 con valor 0

---

### **Test Case 2: INT con nullable=True**

**Configuración**:
```json
{
  "cantidad": {
    "sql_type": "INT",
    "nullable": true,
    "default_value": "0"  // ← Se ignora porque nullable=True
  }
}
```

**Excel de Entrada**:
```
| cantidad |
|----------|
| 10       |
|          | ← vacío
| 25       |
```

**Resultado Esperado en SQL**:
```
| cantidad |
|----------|
| 10       |
| NULL     | ← permite NULL
| 25       |
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test WHERE cantidad IS NULL;
-- Debe mostrar 1 registro
```

✅ **Criterio de Éxito**: 3 registros insertados, 1 con NULL

---

### **Test Case 3: FLOAT con nullable=False y default=0.0**

**Configuración**:
```json
{
  "precio": {
    "sql_type": "FLOAT",
    "nullable": false,
    "default_value": "0.0"
  }
}
```

**Excel de Entrada**:
```
| precio |
|--------|
| 99.99  |
|        | ← vacío
| abc    | ← inválido
| 150.50 |
```

**Resultado Esperado en SQL**:
```
| precio |
|--------|
| 99.99  |
| 0.0    | ← default aplicado
| 0.0    | ← convertido a default
| 150.50 |
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test WHERE precio = 0.0;
-- Debe mostrar 2 registros
```

✅ **Criterio de Éxito**: 4 registros insertados, 2 con 0.0

---

### **Test Case 4: DATE con nullable=False y default=GETDATE()**

**Configuración**:
```json
{
  "fecha": {
    "sql_type": "DATE",
    "nullable": false,
    "default_value": "GETDATE()"
  }
}
```

**Excel de Entrada**:
```
| fecha       |
|-------------|
| 2024-01-15  |
|             | ← vacío
| 2024-01-17  |
```

**Resultado Esperado en SQL**:
```
| fecha       |
|-------------|
| 2024-01-15  |
| 2025-10-22  | ← fecha actual (GETDATE())
| 2024-01-17  |
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test WHERE fecha >= CAST(GETDATE() AS DATE);
-- Debe mostrar 1 registro (el que estaba vacío)

SELECT * FROM tabla_test WHERE fecha IS NULL;
-- Debe mostrar 0 registros
```

✅ **Criterio de Éxito**: 3 registros insertados, 1 con fecha actual

---

### **Test Case 5: VARCHAR con nullable=False y sin default**

**Configuración**:
```json
{
  "nombre": {
    "sql_type": "NVARCHAR(255)",
    "nullable": false,
    "default_value": null  // ← Sin default explícito
  }
}
```

**Excel de Entrada**:
```
| nombre |
|--------|
| Juan   |
|        | ← vacío
| Pedro  |
```

**Resultado Esperado en SQL**:
```
| nombre |
|--------|
| Juan   |
|        | ← string vacío ''
| Pedro  |
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test WHERE nombre = '';
-- Debe mostrar 1 registro

SELECT * FROM tabla_test WHERE nombre IS NULL;
-- Debe mostrar 0 registros
```

✅ **Criterio de Éxito**: 3 registros insertados, 1 con string vacío

---

### **Test Case 6: VARCHAR con nullable=False y default='PENDIENTE'**

**Configuración**:
```json
{
  "codigo": {
    "sql_type": "VARCHAR(50)",
    "nullable": false,
    "default_value": "'PENDIENTE'"
  }
}
```

**Excel de Entrada**:
```
| codigo |
|--------|
| A001   |
|        | ← vacío
| A002   |
```

**Resultado Esperado en SQL**:
```
| codigo     |
|------------|
| A001       |
| PENDIENTE  | ← default aplicado
| A002       |
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test WHERE codigo = 'PENDIENTE';
-- Debe mostrar 1 registro
```

✅ **Criterio de Éxito**: 3 registros insertados, 1 con 'PENDIENTE'

---

### **Test Case 7: BIT con nullable=False y default=0**

**Configuración**:
```json
{
  "activo": {
    "sql_type": "BIT",
    "nullable": false,
    "default_value": "0"
  }
}
```

**Excel de Entrada**:
```
| activo |
|--------|
| TRUE   |
|        | ← vacío
| FALSE  |
| 1      |
```

**Resultado Esperado en SQL**:
```
| activo |
|--------|
| 1      | ← TRUE → 1
| 0      | ← default aplicado
| 0      | ← FALSE → 0
| 1      | ← 1 → 1
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test WHERE activo = 0;
-- Debe mostrar 2 registros (vacío + FALSE)
```

✅ **Criterio de Éxito**: 4 registros insertados, 2 con 0

---

### **Test Case 8: Múltiples Columnas con Diferentes Configuraciones**

**Configuración**:
```json
{
  "id": {"sql_type": "INT", "nullable": false, "default_value": "0"},
  "cantidad": {"sql_type": "INT", "nullable": false, "default_value": "0"},
  "precio": {"sql_type": "FLOAT", "nullable": false, "default_value": "0.0"},
  "fecha": {"sql_type": "DATE", "nullable": false, "default_value": "GETDATE()"},
  "nombre": {"sql_type": "NVARCHAR(100)", "nullable": false, "default_value": "'SIN_NOMBRE'"},
  "activo": {"sql_type": "BIT", "nullable": false, "default_value": "0"}
}
```

**Excel de Entrada**:
```
| id | cantidad | precio | fecha       | nombre | activo |
|----|----------|--------|-------------|--------|--------|
| 1  | 10       | 99.99  | 2024-01-15  | Juan   | TRUE   |
| 2  |          |        |             |        |        | ← todo vacío
| 3  | 20       | 150.50 | 2024-01-17  | Pedro  | FALSE  |
```

**Resultado Esperado en SQL**:
```
| id | cantidad | precio | fecha       | nombre     | activo |
|----|----------|--------|-------------|------------|--------|
| 1  | 10       | 99.99  | 2024-01-15  | Juan       | 1      |
| 2  | 0        | 0.0    | 2025-10-22  | SIN_NOMBRE | 0      | ← todos defaults
| 3  | 20       | 150.50 | 2024-01-17  | Pedro      | 0      |
```

**Comandos de Verificación**:
```sql
SELECT * FROM tabla_test WHERE 
  cantidad = 0 AND 
  precio = 0.0 AND 
  nombre = 'SIN_NOMBRE' AND 
  activo = 0;
-- Debe mostrar 1 registro (la fila 2)

SELECT * FROM tabla_test WHERE fecha >= CAST(GETDATE() AS DATE);
-- Debe mostrar 1 registro
```

✅ **Criterio de Éxito**: 3 registros insertados, fila 2 con todos los defaults aplicados

---

### **Test Case 9: Columna con Espacios en Blanco**

**Configuración**:
```json
{
  "descripcion": {
    "sql_type": "NVARCHAR(255)",
    "nullable": false,
    "default_value": "' '"  // ← Espacio
  }
}
```

**Excel de Entrada**:
```
| descripcion |
|-------------|
| Texto 1     |
|             | ← vacío
|             | ← solo espacios
| Texto 2     |
```

**Resultado Esperado en SQL**:
```
| descripcion |
|-------------|
| Texto 1     |
|             | ← espacio simple ' '
|             | ← espacio simple ' '
| Texto 2     |
```

**Comandos de Verificación**:
```sql
SELECT LEN(descripcion), * FROM tabla_test WHERE descripcion = ' ';
-- Debe mostrar 2 registros con len=1
```

✅ **Criterio de Éxito**: 4 registros insertados, 2 con espacio simple

---

### **Test Case 10: Excel con Hoja Múltiple**

**Configuración**:
```json
{
  "Hoja 1": {
    "cantidad": {"sql_type": "INT", "nullable": false, "default_value": "0"}
  },
  "Hoja 2": {
    "precio": {"sql_type": "FLOAT", "nullable": false, "default_value": "0.0"}
  }
}
```

**Excel de Entrada**:
- **Hoja 1**: `cantidad` con valores [10, vacío, 20]
- **Hoja 2**: `precio` con valores [99.99, vacío, 150.50]

**Resultado Esperado**:
- **Tabla 1**: 3 registros, 1 con cantidad=0
- **Tabla 2**: 3 registros, 1 con precio=0.0

**Comandos de Verificación**:
```sql
SELECT * FROM proceso_hoja_1 WHERE cantidad = 0;
-- 1 registro

SELECT * FROM proceso_hoja_2 WHERE precio = 0.0;
-- 1 registro
```

✅ **Criterio de Éxito**: 2 tablas creadas, defaults aplicados en cada una

---

## 🔍 Checklist de Verificación Manual

Para cada test ejecutado:

### **Antes de Ejecutar**

- [ ] Excel de prueba creado con datos de entrada
- [ ] Proceso configurado en `/multi-config/`
- [ ] Tipos SQL verificados
- [ ] nullable y default_value configurados correctamente
- [ ] Nombre de tabla SQL válido

### **Durante la Ejecución**

- [ ] Proceso ejecutado sin errores
- [ ] Log muestra "Valores por defecto aplicados según column_mappings"
- [ ] Log muestra mensajes como: "📝 Aplicando valor por defecto '0' para columna 'cantidad'"
- [ ] Mensaje de éxito: "✅ Inserción masiva exitosa"

### **Después de Ejecutar**

- [ ] Verificar en SQL Server Management Studio (SSMS)
- [ ] Contar registros: `SELECT COUNT(*) FROM tabla_test`
- [ ] Verificar defaults: `SELECT * FROM tabla_test WHERE columna = default_value`
- [ ] Verificar sin NULL: `SELECT * FROM tabla_test WHERE columna IS NULL` (debe ser 0)
- [ ] Verificar estructura: `sp_help tabla_test` (tipos y nullable correctos)

---

## 📊 Template de Reporte de Pruebas

```markdown
## Test Case: [Número y Nombre]

**Ejecutado por**: [Tu nombre]
**Fecha**: [Fecha]
**Versión**: [Versión del sistema]

### Configuración
- Tipo SQL: [tipo]
- nullable: [true/false]
- default_value: [valor]

### Datos de Entrada
[Describir Excel o pegar tabla]

### Resultado Obtenido
[Captura de pantalla o salida SQL]

### Comandos SQL Usados
```sql
[Pegar comandos de verificación]
```

### Estado
- [ ] ✅ PASADO
- [ ] ❌ FALLADO

### Observaciones
[Notas adicionales, errores encontrados, etc.]
```

---

## 🚀 Automatización de Pruebas

Para ejecutar todas las pruebas automáticamente:

```powershell
# Ejecutar suite de tests unitarios
python test_normalizacion_defaults.py

# Resultado esperado:
# 🎯 Total: 6/6 pruebas pasadas
# 🎉 ¡TODOS LOS TESTS PASARON!
```

---

## 📚 Documentos Relacionados

- **Resumen Técnico**: `RESUMEN_NORMALIZACION_VALORES_VACIOS.md`
- **Guía Completa**: `MEJORA_NORMALIZACION_VALORES_VACIOS.md`
- **Ejemplo Práctico**: `EJEMPLO_NORMALIZACION_VALORES_VACIOS.md`
- **Guía Rápida**: `GUIA_RAPIDA_NORMALIZACION.md`

---

**🎯 Objetivo Final**: Asegurar que el sistema maneja correctamente todos los escenarios de valores vacíos en Excel según la configuración del usuario.
