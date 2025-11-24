# 🎨 Nueva Funcionalidad: Selector de Tipo SQL Editable

**Fecha**: 22 de Octubre, 2025
**Estado**: ✅ **IMPLEMENTADO**

---

## 🎯 Objetivo

Permitir que el usuario **force/cambie el tipo SQL** de cada columna en la interfaz, haciendo la detección de tipos más precisa y flexible.

---

## ❓ ¿Por Qué Es Necesario?

### **Problema Anterior**:

```python
# Excel tenía una columna "codigo" con valores: A001, A002, A003
# Sistema detectaba automáticamente: NVARCHAR(255)
# Pero el usuario NO podía cambiarla si quería INT u otro tipo
```

**Limitación**:
- ❌ Detección automática no siempre es precisa
- ❌ Datos mixtos en Excel confunden al detector
- ❌ Usuario no podía corregir manualmente
- ❌ Tenía que modificar el Excel o aceptar el tipo detectado

### **Solución Implementada**:

```python
# Ahora el usuario puede:
✅ Ver el tipo detectado automáticamente
✅ Cambiarlo con un selector dropdown
✅ Sistema usa el tipo seleccionado por el usuario
✅ Placeholder de default_value se actualiza según el tipo
```

---

## 🎨 Interfaz de Usuario

### **Antes (Solo Lectura)**:

```
┌─────────────────────────────────────────────────┐
│ ☑ fecha          (DATE)                         │
│   └─ Renombrar: [fecha____________]             │
│                                                  │
│ ☑ codigo         (NVARCHAR(255))  ← No editable │
│   └─ Renombrar: [codigo___________]             │
└─────────────────────────────────────────────────┘
```

### **Ahora (Editable)**:

```
┌─────────────────────────────────────────────────────────────┐
│ ☑ fecha        [DATE ▼]               [fecha_________]      │
│   ├─ Nullable: ☐ Permitir NULL                              │
│   └─ Default:  [GETDATE()_____________________] [Sugerir]   │
│                                                              │
│ ☑ codigo       [VARCHAR(50) ▼]        [codigo________]      │
│   ├─ Nullable: ☑ Permitir NULL                              │
│   └─ Default:  [_____________________________] [Sugerir]    │
│                                                              │
│ ☑ cantidad     [INT ▼]                [cantidad_______]     │
│   ├─ Nullable: ☐ Permitir NULL                              │
│   └─ Default:  [0_____________________________] [Sugerir]   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Implementación Técnica

### **1. Selector HTML Agregado**

**Ubicación**: `excel_multi_sheet_selector.html` (líneas 375-425)

```html
<select class="form-select form-select-sm column-type-selector" 
        id="type-{{ sheet|slugify }}-{{ forloop.counter }}"
        data-sheet="{{ sheet }}"
        data-column="{{ column.name }}"
        onchange="onSqlTypeChange('{{ sheet }}', '{{ column.name }}', '{{ forloop.counter }}', '{{ sheet|slugify }}')"
        disabled>
    <optgroup label="Numéricos">
        <option value="INT" {% if 'INT' in column.sql_type %}selected{% endif %}>INT</option>
        <option value="BIGINT">BIGINT</option>
        <option value="FLOAT">FLOAT</option>
        <option value="DECIMAL(10,2)">DECIMAL(10,2)</option>
        ...
    </optgroup>
    <optgroup label="Fecha/Hora">
        <option value="DATE">DATE</option>
        <option value="DATETIME">DATETIME</option>
        ...
    </optgroup>
    <optgroup label="Texto">
        <option value="VARCHAR(50)">VARCHAR(50)</option>
        <option value="NVARCHAR(255)">NVARCHAR(255)</option>
        ...
    </optgroup>
    <optgroup label="Booleano">
        <option value="BIT">BIT</option>
    </optgroup>
</select>
```

**Tipos SQL Disponibles**:

| Categoría | Tipos |
|-----------|-------|
| **Numéricos** | INT, BIGINT, SMALLINT, TINYINT, FLOAT, REAL, DECIMAL(10,2), MONEY |
| **Fecha/Hora** | DATE, DATETIME, DATETIME2, SMALLDATETIME, TIME |
| **Texto** | VARCHAR(50/255), NVARCHAR(50/255/500), TEXT, NTEXT |
| **Booleano** | BIT |

---

### **2. Función JavaScript: onSqlTypeChange()**

**Ubicación**: `excel_multi_sheet_selector.html` (líneas ~1072-1110)

```javascript
function onSqlTypeChange(sheetName, columnName, counter, sheetSlug) {
    const typeSelector = document.getElementById(`type-${sheetSlug}-${counter}`);
    const defaultInput = document.getElementById(`default-${sheetSlug}-${counter}`);
    
    if (!typeSelector || !defaultInput) {
        console.error(`❌ No se encontraron elementos para tipo SQL`);
        return;
    }
    
    const selectedType = typeSelector.value;
    console.log(`🔄 Tipo SQL cambiado para "${columnName}": ${selectedType}`);
    
    // Actualizar el data attribute del input
    defaultInput.dataset.sqlType = selectedType;
    
    // Actualizar placeholder dinámicamente
    const newPlaceholder = getPlaceholderForType(selectedType);
    defaultInput.placeholder = newPlaceholder;
    
    // Validar valor default actual
    const currentValue = defaultInput.value.trim();
    if (currentValue && !isValidDefaultForType(currentValue, selectedType)) {
        if (confirm(`El valor por defecto "${currentValue}" no parece válido para el tipo ${selectedType}. ¿Deseas limpiarlo?`)) {
            defaultInput.value = '';
        }
    }
    
    console.log(`   ✅ Placeholder actualizado: "${newPlaceholder}"`);
}
```

**Comportamiento**:
1. ✅ Detecta cuando el usuario cambia el tipo SQL
2. ✅ Actualiza el placeholder del input de default_value
3. ✅ Valida si el valor default actual es compatible con el nuevo tipo
4. ✅ Pregunta al usuario si desea limpiar valores incompatibles

---

### **3. Función de Validación: isValidDefaultForType()**

```javascript
function isValidDefaultForType(value, sqlType) {
    const upperType = sqlType.toUpperCase();
    
    // Tipos numéricos
    if (upperType.includes('INT') || upperType.includes('FLOAT') || 
        upperType.includes('DECIMAL') || upperType.includes('MONEY')) {
        return !isNaN(value);
    }
    
    // Tipos de fecha
    if (upperType.includes('DATE') || upperType.includes('TIME')) {
        return value.toUpperCase() === 'GETDATE()' || !isNaN(Date.parse(value));
    }
    
    // Tipos de texto y booleanos siempre son válidos
    return true;
}
```

---

### **4. Integración con updateColumnSelection()**

**Modificaciones**:

```javascript
// Buscar el typeSelector junto con los demás elementos
const typeSelector = document.getElementById(`type-${sheetSlug}-${counter}`);

if (isChecked) {
    // Habilitar selector de tipo SQL
    if (typeSelector) {
        typeSelector.disabled = false;
    }
    
    // Tomar tipo del selector si está disponible
    const sqlType = typeSelector ? typeSelector.value : defaultInput.dataset.sqlType;
    const contextualPlaceholder = getPlaceholderForType(sqlType);
    defaultInput.placeholder = contextualPlaceholder;
} else {
    // Deshabilitar selector de tipo SQL
    if (typeSelector) {
        typeSelector.disabled = true;
    }
}
```

---

### **5. Integración con saveProcess()**

**Modificaciones**:

```javascript
function saveProcess(andRun = false, duplicateAction = null) {
    // Buscar el typeSelector para cada columna
    const typeSelector = document.querySelector(`select.column-type-selector[data-sheet="${sheetName}"][data-column="${originalName}"]`);
    
    // Tomar tipo SQL del selector en lugar del data attribute
    let sqlType = 'NVARCHAR(255)';  // Default fallback
    if (typeSelector && !typeSelector.disabled) {
        sqlType = typeSelector.value;  // ✅ Tipo seleccionado por el usuario
    } else if (defaultInput && defaultInput.dataset.sqlType) {
        sqlType = defaultInput.dataset.sqlType;  // Fallback al detectado
    }
    
    // Guardar en column_mappings
    columnMappings[sheetName][originalName] = {
        renamed_to: customName,
        sql_type: sqlType,  // ✅ Usa el tipo seleccionado
        nullable: nullable,
        default_value: nullable ? null : (defaultValue || getDefaultValueSuggestion(sqlType))
    };
}
```

---

## 📊 Flujo de Usuario

### **Escenario 1: Corregir Detección Incorrecta**

```
1. Usuario sube Excel con columna "edad" que tiene valores "18", "25", "30"
2. Sistema detecta: NVARCHAR(255) (porque están como texto en Excel)
3. Usuario ve el selector: [NVARCHAR(255) ▼]
4. Usuario cambia a: [INT ▼]
5. Placeholder de default se actualiza automáticamente: "0"
6. Sistema usa INT al crear la tabla SQL
```

### **Escenario 2: Optimizar Tipo de Datos**

```
1. Sistema detecta automáticamente: NVARCHAR(255)
2. Usuario sabe que los códigos son máximo 10 caracteres
3. Usuario cambia a: [VARCHAR(50) ▼]
4. Ahorra espacio en la base de datos
```

### **Escenario 3: Cambiar de Texto a Fecha**

```
1. Columna "fecha_texto" tiene: "2024-01-15", "2024-01-16"
2. Sistema detecta: NVARCHAR(255)
3. Usuario cambia a: [DATE ▼]
4. Placeholder se actualiza a: "GETDATE()"
5. Usuario deja default como "GETDATE()"
6. Sistema convierte las fechas correctamente
```

---

## 🎯 Beneficios

### **Para el Usuario**:

1. ✅ **Control Total**: Puede forzar el tipo SQL deseado
2. ✅ **Corrección Fácil**: Detectó mal el tipo? Cámbialo con un click
3. ✅ **Sugerencias Inteligentes**: Placeholder se actualiza automáticamente
4. ✅ **Validación**: Sistema alerta si el default no es compatible
5. ✅ **Optimización**: Puede elegir tipos más eficientes (ej: VARCHAR(50) en lugar de NVARCHAR(255))

### **Para el Sistema**:

1. ✅ **Normalización Precisa**: Usa el tipo correcto en `apply_default_values_from_mappings()`
2. ✅ **Menos Errores**: Usuario corrige antes de insertar
3. ✅ **Configuración Persistente**: El tipo seleccionado se guarda con el proceso
4. ✅ **Reutilizable**: Próximas ejecuciones usan el tipo configurado

---

## 🧪 Ejemplos de Uso

### **Ejemplo 1: Cambiar INT a VARCHAR**

```html
<!-- Usuario ve código numérico como 001, 002, 003 -->
<!-- Sistema detecta: INT -->
<!-- Usuario cambia a: VARCHAR(50) para mantener el 0 inicial -->

Antes:  001 → 1 (pierde el 0)
Ahora:  001 → "001" (mantiene formato)
```

### **Ejemplo 2: Cambiar NVARCHAR a INT**

```html
<!-- Excel tiene "10", "20", "30" como texto -->
<!-- Sistema detecta: NVARCHAR(255) -->
<!-- Usuario cambia a: INT -->

Antes:  "10" → insertaría como string "10"
Ahora:  "10" → convierte y inserta como número 10
```

### **Ejemplo 3: Optimizar Tamaño de Columna**

```html
<!-- Códigos siempre son 10 caracteres máximo -->
<!-- Sistema detecta: NVARCHAR(255) -->
<!-- Usuario cambia a: VARCHAR(50) -->

Beneficio: 
- Ahorra 205 caracteres por registro
- Mejora índices y consultas
- Evita almacenamiento innecesario
```

---

## 📝 Resumen de Cambios

### **Archivos Modificados**:

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `excel_multi_sheet_selector.html` | Selector HTML + funciones JS | ~100 líneas |

### **Funcionalidades Agregadas**:

1. ✅ Selector `<select>` con 20+ tipos SQL agrupados
2. ✅ Función `onSqlTypeChange()` para manejar cambios
3. ✅ Función `isValidDefaultForType()` para validar defaults
4. ✅ Integración con `updateColumnSelection()`
5. ✅ Integración con `saveProcess()`
6. ✅ Actualización automática de placeholders
7. ✅ Validación de valores incompatibles

### **Tipos SQL Soportados**:

- **Numéricos**: 8 tipos (INT, BIGINT, FLOAT, DECIMAL, etc.)
- **Fecha/Hora**: 5 tipos (DATE, DATETIME, DATETIME2, etc.)
- **Texto**: 7 tipos (VARCHAR, NVARCHAR con diferentes tamaños)
- **Booleano**: 1 tipo (BIT)

**Total**: 21 tipos SQL disponibles para el usuario

---

## 🚀 Próximos Pasos

1. **Testing**: Probar con diferentes archivos Excel
2. **Validación**: Verificar que los tipos seleccionados se aplican correctamente
3. **Documentación de Usuario**: Crear guía visual con screenshots

---

## 🎉 Conclusión

Ahora el usuario tiene **control total sobre los tipos SQL**, combinando:

1. ✅ **Detección Automática** (conveniente)
2. ✅ **Selección Manual** (flexible)
3. ✅ **Normalización Inteligente** (precisa)
4. ✅ **Validación de Datos** (segura)

**El sistema es más robusto, flexible y fácil de usar.** 🎊
