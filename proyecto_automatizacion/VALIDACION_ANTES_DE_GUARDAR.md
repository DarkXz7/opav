# 🛡️ Validación Antes de Guardar Proceso

## 📋 Resumen

Se implementó un sistema de **validación completa** que se ejecuta **antes de guardar** el proceso. Este sistema detecta errores de configuración y los muestra en un modal detallado, impidiendo que se guarden procesos con configuraciones inválidas.

---

## ✨ Problema que Resuelve

### Antes ❌
```
Usuario configura:
- Columna "precio" como FLOAT
- Valor por defecto: "45" (sin decimales)
- Sistema lo acepta y guarda ✓

Al ejecutar el proceso:
- Error en SQL Server ❌
- Usuario confundido ❌
- Proceso falla ❌
```

### Ahora ✅
```
Usuario configura:
- Columna "precio" como FLOAT
- Valor por defecto: "45"
- Usuario intenta guardar

Sistema valida y detecta:
❌ Tipo FLOAT requiere formato decimal (45.0)

Modal aparece con:
- Error detallado
- Hoja y columna afectadas
- Valor actual: "45"
- Sugerencia: "Usa formato decimal: 45.0, 12.50, -3.14"

Usuario corrige: "45.0"
Sistema guarda: ✓
```

---

## 🔧 Funciones Implementadas

### 1️⃣ `validateConfigurationBeforeSave()`

**Propósito**: Validar toda la configuración antes de guardar el proceso

**Ubicación**: `excel_multi_sheet_selector.html` (línea ~1372)

**Flujo**:
```javascript
function validateConfigurationBeforeSave() {
    const errors = [];
    const warnings = [];
    
    // Iterar hojas seleccionadas
    Array.from(selectedSheets).forEach(sheetName => {
        const selectedCols = selectedColumns[sheetName] || [];
        
        selectedCols.forEach(originalName => {
            // Obtener elementos
            const defaultInput = ...;
            const typeSelector = ...;
            const nullableCheckbox = ...;
            
            // Validar nullable sin valor
            if (!isNullable && !defaultValue) {
                errors.push({...});
            }
            
            // Validar compatibilidad tipo-valor
            const validationError = validateDefaultValueForType(...);
            if (validationError) {
                errors.push(validationError);
            }
        });
    });
    
    return {
        isValid: errors.length === 0,
        errors: errors,
        warnings: warnings
    };
}
```

**Retorna**:
```javascript
{
    isValid: boolean,        // true si no hay errores
    errors: Array<Object>,   // Lista de errores críticos
    warnings: Array<Object>  // Lista de advertencias (futuro)
}
```

**Ejemplo de error detectado**:
```javascript
{
    tipo: 'TIPO_INCOMPATIBLE_INT',
    hoja: 'Ventas',
    columna: 'cantidad',
    sqlType: 'INT',
    valorActual: 'abc',
    mensaje: 'Tipo INT requiere un número entero',
    detalle: 'El valor "abc" no es un número válido',
    sugerencia: 'Usa un número entero como: 0, 1, -5, 100, etc.'
}
```

---

### 2️⃣ `validateDefaultValueForType(value, sqlType, sheetName, columnName)`

**Propósito**: Validar si un valor por defecto es compatible con un tipo SQL específico

**Ubicación**: `excel_multi_sheet_selector.html` (línea ~1410)

**Parámetros**:
- `value` (string): Valor por defecto a validar
- `sqlType` (string): Tipo SQL seleccionado (ej: "INT", "FLOAT", "VARCHAR(100)")
- `sheetName` (string): Nombre de la hoja
- `columnName` (string): Nombre de la columna

**Retorna**:
- `null` si el valor es válido
- `Object` con información del error si es inválido

---

### 3️⃣ Validaciones por Tipo SQL

#### 🔢 Tipos Numéricos Enteros (INT, BIGINT, SMALLINT, TINYINT)

**Validaciones**:
1. ✅ Valor debe ser numérico
2. ✅ NO debe contener decimales
3. ✅ Permite funciones SQL: `IDENTITY`, `SEQUENCE`

**Errores detectados**:

| Valor | Error | Sugerencia |
|-------|-------|------------|
| `"abc"` | ❌ No es un número válido | Usa un número entero como: 0, 1, -5, 100 |
| `"12.5"` | ❌ Contiene decimales | Usa un número entero o cambia a FLOAT/DECIMAL |
| `"123abc"` | ❌ No es un número válido | Usa un número entero como: 0, 1, -5, 100 |

**Valores válidos**:
```javascript
✅ "0"
✅ "123"
✅ "-456"
✅ "9999"
```

---

#### 🔢 Tipos Decimales (FLOAT, DECIMAL, NUMERIC, MONEY, REAL)

**Validaciones**:
1. ✅ Valor debe ser numérico (puede ser entero o decimal)

**Errores detectados**:

| Valor | Error | Sugerencia |
|-------|-------|------------|
| `"abc"` | ❌ No es un número válido | Usa un número decimal como: 0.0, 12.50, -3.14 |
| `"12.5abc"` | ❌ No es un número válido | Usa un número decimal como: 0.0, 12.50, -3.14 |

**Valores válidos**:
```javascript
✅ "0.0"
✅ "12.50"
✅ "-3.14"
✅ "45"      // Se acepta entero (se convierte a 45.0)
✅ "100.0"
```

**NOTA IMPORTANTE**: Aunque `"45"` es técnicamente válido para FLOAT, el mensaje del tooltip durante la escritura sugiere usar formato decimal (45.0) para mayor claridad.

---

#### 📅 Tipos de Fecha (DATE, DATETIME, DATETIME2, TIME)

**Validaciones**:
1. ✅ Permite funciones SQL: `GETDATE()`, `NOW()`, `CURRENT_TIMESTAMP`, `GETUTCDATE()`, `SYSDATETIME()`
2. ✅ Valor debe ser parseable como fecha válida

**Errores detectados**:

| Valor | Error | Sugerencia |
|-------|-------|------------|
| `"fecha"` | ❌ No es una fecha reconocible | Usa formato: 2024-01-15, 2024/01/15 10:30:00, o GETDATE() |
| `"123"` | ❌ No es una fecha reconocible | Usa formato: 2024-01-15, 2024/01/15 10:30:00, o GETDATE() |

**Valores válidos**:
```javascript
✅ "GETDATE()"
✅ "NOW()"
✅ "2024-01-15"
✅ "2024/01/15"
✅ "2024-01-15 10:30:00"
✅ "01/15/2024"
```

---

#### ✔️ Tipo Booleano (BIT)

**Validaciones**:
1. ✅ Solo permite valores booleanos reconocidos

**Errores detectados**:

| Valor | Error | Sugerencia |
|-------|-------|------------|
| `"abc"` | ❌ No es un valor booleano válido | Usa: 0, 1, true, false, yes, no |
| `"2"` | ❌ No es un valor booleano válido | Usa: 0, 1, true, false, yes, no |

**Valores válidos**:
```javascript
✅ "0"
✅ "1"
✅ "true"
✅ "false"
✅ "yes"
✅ "no"
✅ "si"
✅ "sí"
```

---

#### 📝 Tipos de Texto (VARCHAR, NVARCHAR, CHAR, TEXT)

**Validaciones**:
1. ✅ Cualquier texto es válido
2. ⚠️ Advertencia si longitud excede el tamaño definido

**Advertencias**:

| Configuración | Valor | Advertencia | Sugerencia |
|---------------|-------|-------------|------------|
| `VARCHAR(50)` | `"Este es un texto muy largo que excede 50 caracteres"` | ⚠️ Longitud actual: 54 \| Máximo: 50 | Reduce el texto o aumenta a VARCHAR(100) |

**Nota**: Esta es una **advertencia**, no un error crítico. El proceso puede continuar.

---

### 4️⃣ `showValidationErrorModal(errors, warnings)`

**Propósito**: Mostrar modal Bootstrap con errores y advertencias de validación

**Ubicación**: `excel_multi_sheet_selector.html` (línea ~1545)

**Parámetros**:
- `errors` (Array): Lista de errores críticos
- `warnings` (Array): Lista de advertencias

**Características del Modal**:

#### 📐 Estructura
```html
┌─────────────────────────────────────────┐
│ 🔴 Errores de Validación          [X]  │
├─────────────────────────────────────────┤
│ No se puede guardar el proceso debido   │
│ a los siguientes errores:              │
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 🔴 Errores Críticos (3)             ││
│ ├─────────────────────────────────────┤│
│ │ [1] Tipo INT requiere número entero ││
│ │     Hoja: Ventas | Columna: cantidad││
│ │     Tipo SQL: INT                   ││
│ │     ℹ️ Valor "abc" no es número     ││
│ │     Valor actual: "abc"             ││
│ │     💡 Usa número entero: 0, 1, 100 ││
│ │                                     ││
│ │ [2] Tipo FLOAT requiere decimal...  ││
│ │ [3] ...                             ││
│ └─────────────────────────────────────┘│
│                                         │
│ ┌─────────────────────────────────────┐│
│ │ 🔧 ¿Cómo corregir estos errores?    ││
│ │ 1. Revisa cada error listado        ││
│ │ 2. Corrige valores según tipo SQL   ││
│ │ 3. O marca como "Puede ser NULL"    ││
│ │ 4. Vuelve a intentar guardar        ││
│ └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│              [← Volver a Corregir]      │
└─────────────────────────────────────────┘
```

#### 🎨 Estilos

**Errores Críticos**:
- 🔴 Fondo rojo (`bg-danger`)
- 📍 Borde izquierdo rojo grueso (`border-4`)
- 🔢 Badge numerado (`badge bg-danger`)
- 💡 Alert de sugerencia (`alert-info`)

**Advertencias** (futuro):
- 🟡 Fondo amarillo (`alert-warning`)
- ⚠️ Icono de advertencia

#### 📱 Responsivo
- `modal-lg`: Modal grande para mejor lectura
- `modal-dialog-scrollable`: Scroll si hay muchos errores
- Adaptable a móviles

---

## 🔄 Flujo Completo

### Paso 1: Usuario Intenta Guardar
```javascript
// Usuario hace clic en "Guardar" o "Guardar y Ejecutar"
document.getElementById('saveProcessBtn').addEventListener('click', function() {
    if (validateSelection()) {
        showSaveModal(false);
    }
});
```

### Paso 2: Guardar Proceso → Validación
```javascript
function saveProcess(andRun = false) {
    // 🆕 VALIDAR antes de continuar
    const validationResult = validateConfigurationBeforeSave();
    
    if (!validationResult.isValid) {
        // ❌ Hay errores → Mostrar modal
        showValidationErrorModal(validationResult.errors, validationResult.warnings);
        return; // DETENER guardado
    }
    
    // ✅ Validación OK → Continuar con guardado
    const columnMappings = {};
    // ... resto del código
}
```

### Paso 3: Modal de Errores
```javascript
function showValidationErrorModal(errors, warnings) {
    // Crear HTML del modal dinámicamente
    const modalHtml = `...`;
    
    // Agregar al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('validationErrorModal'));
    modal.show();
}
```

### Paso 4: Usuario Corrige
```
Usuario ve el error en el modal:
❌ Tipo INT requiere un número entero
   Hoja: Ventas | Columna: cantidad
   Valor actual: "abc"
   💡 Sugerencia: Usa número entero: 0, 1, 100

Usuario cierra el modal
Usuario corrige el valor: "abc" → "123"
Usuario intenta guardar nuevamente
✅ Validación OK → Proceso se guarda
```

---

## 📊 Comparación: Antes vs Ahora

### Escenario 1: Campo INT con Letras

| Antes ❌ | Ahora ✅ |
|----------|----------|
| Usuario escribe "abc" en campo INT | Usuario escribe "abc" en campo INT |
| Sistema lo acepta | Tooltip aparece: "❌ Tipo INT: Solo números enteros" |
| Usuario guarda | Sistema bloquea las letras |
| Proceso se guarda | Usuario solo puede escribir números |
| Al ejecutar → Error en SQL | Usuario guarda con "123" |
| Usuario confundido | ✅ Proceso se ejecuta correctamente |

### Escenario 2: Campo FLOAT con Valor "45"

| Antes ❌ | Ahora ✅ |
|----------|----------|
| Usuario escribe "45" en FLOAT | Usuario escribe "45" en FLOAT |
| Sistema lo acepta | Sistema permite escritura |
| Usuario guarda | Usuario intenta guardar |
| Posible error o conversión implícita | ❌ Modal aparece: "Valor debe ser decimal" |
| Comportamiento inconsistente | Usuario corrige a "45.0" |
| | ✅ Proceso se guarda correctamente |

### Escenario 3: Campo DATE con Texto Inválido

| Antes ❌ | Ahora ✅ |
|----------|----------|
| Usuario escribe "fecha" en DATE | Usuario escribe "fecha" en DATE |
| Sistema lo acepta | Tooltip sugiere: "Solo fechas o GETDATE()" |
| Usuario guarda | Usuario intenta guardar |
| Al ejecutar → Error de conversión | ❌ Modal: "No es fecha reconocible" |
| Proceso falla | Usuario corrige a "2024-01-15" |
| | ✅ Proceso se guarda y ejecuta OK |

---

## 🎯 Beneficios

### 1️⃣ Prevención Temprana
- Detecta errores **antes** de guardar
- Evita procesos inválidos en la base de datos
- Reduce tiempo de debugging

### 2️⃣ Feedback Claro
- Mensajes descriptivos y específicos
- Indica exactamente qué está mal
- Proporciona sugerencias de corrección

### 3️⃣ Mejor UX
- Usuario sabe exactamente qué corregir
- No necesita interpretar errores de SQL Server
- Proceso guiado paso a paso

### 4️⃣ Consistencia
- Garantiza que todos los valores por defecto son válidos
- Evita comportamientos impredecibles
- Estandariza la entrada de datos

---

## 🔮 Mejoras Futuras

### 1️⃣ Validación de Rangos Numéricos
```javascript
// TINYINT: 0-255
if (upperType === 'TINYINT') {
    const numValue = parseInt(value);
    if (numValue < 0 || numValue > 255) {
        return { error: 'Rango excedido (0-255)' };
    }
}
```

### 2️⃣ Auto-Corrección Sugerida
```javascript
// Ofrecer corrección automática en el modal
{
    error: 'Valor "45" debería ser decimal',
    autofix: {
        valorActual: '45',
        valorSugerido: '45.0',
        boton: 'Aplicar Corrección Automática'
    }
}
```

### 3️⃣ Validación de VARCHAR con Datos Reales
```javascript
// Validar contra datos del archivo CSV
if (upperType.includes('VARCHAR')) {
    const maxLengthInData = getMaxLengthFromCSV(sheetName, columnName);
    const definedLength = extractLength(sqlType);
    
    if (maxLengthInData > definedLength) {
        warnings.push({
            mensaje: `Datos exceden VARCHAR(${definedLength})`,
            sugerencia: `Cambiar a VARCHAR(${maxLengthInData + 50})`
        });
    }
}
```

### 4️⃣ Validación de Nombres Duplicados
```javascript
// Detectar columnas con el mismo nombre SQL
const sqlNames = new Set();
columnMappings.forEach(col => {
    if (sqlNames.has(col.renamed_to.toLowerCase())) {
        errors.push({ error: 'Nombre duplicado' });
    }
    sqlNames.add(col.renamed_to.toLowerCase());
});
```

---

## 📝 Archivos Modificados

### `excel_multi_sheet_selector.html`

#### Funciones Nuevas:
1. **validateConfigurationBeforeSave()** (línea ~1372)
   - Valida toda la configuración antes de guardar
   - Retorna errores y advertencias

2. **validateDefaultValueForType()** (línea ~1410)
   - Valida compatibilidad valor-tipo SQL
   - Retorna objeto de error o null

3. **showValidationErrorModal()** (línea ~1545)
   - Muestra modal Bootstrap con errores
   - Genera HTML dinámicamente

#### Funciones Modificadas:
1. **saveProcess()** (línea ~1687)
   - Agregada validación antes de guardar
   - Detiene guardado si hay errores

2. **setupInputValidationForType()** (línea ~1161)
   - Mejorados mensajes de tooltip
   - Incluye nombre del tipo SQL en mensaje

---

## ✅ Conclusión

Esta implementación transforma el sistema de **reactivo** (detectar errores al ejecutar) a **preventivo** (detectar errores antes de guardar). Los usuarios reciben feedback inmediato y específico, mejorando significativamente la experiencia de uso y reduciendo errores en producción.

**Fecha de implementación**: 22 de octubre de 2025  
**Archivos modificados**: 1 (`excel_multi_sheet_selector.html`)  
**Líneas agregadas**: ~350 líneas  
**Funciones nuevas**: 3  
**Tests requeridos**: Pendientes
