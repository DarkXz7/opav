# 🎯 Validación en Tiempo Real de Valores por Defecto

## 📋 Resumen

Se implementó un sistema de **validación en tiempo real** que previene que los usuarios escriban valores inválidos en los campos de "Default Value" según el tipo SQL seleccionado.

## ✨ Características Implementadas

### 1️⃣ Validación por Tipo SQL

#### 🔢 Tipos Numéricos Enteros
**Tipos afectados**: `INT`, `BIGINT`, `SMALLINT`, `TINYINT`

**Restricciones**:
- ✅ Solo permite dígitos (0-9)
- ✅ Permite signo negativo (-) solo al inicio
- ❌ Bloquea letras y caracteres especiales
- 📱 Activa teclado numérico en móviles

**Ejemplo**:
```
Usuario intenta escribir: "123abc"
Sistema bloquea: "abc"
Resultado: "123"
Tooltip: "❌ Solo números enteros permitidos"
```

---

#### 🔢 Tipos Decimales
**Tipos afectados**: `FLOAT`, `DECIMAL`, `NUMERIC`, `MONEY`, `REAL`

**Restricciones**:
- ✅ Solo permite dígitos (0-9)
- ✅ Permite signo negativo (-) solo al inicio
- ✅ Permite punto o coma decimal (solo uno)
- ❌ Bloquea letras y caracteres especiales
- 📱 Activa teclado decimal en móviles

**Ejemplo**:
```
Usuario intenta escribir: "12.50abc"
Sistema bloquea: "abc"
Resultado: "12.50"
Tooltip: "❌ Solo números decimales permitidos (ej: 12.50)"
```

---

#### 📅 Tipos de Fecha
**Tipos afectados**: `DATE`, `DATETIME`, `DATETIME2`, `TIME`, `TIMESTAMP`

**Restricciones**:
- ✅ Permite dígitos, guiones, barras, dos puntos
- ✅ Permite funciones SQL: `GETDATE()`, `NOW()`, `CURRENT_TIMESTAMP`
- ✅ Permite espacios (para separar fecha y hora)
- ❌ Bloquea letras que no formen funciones SQL válidas

**Ejemplo**:
```
✅ Válido: "2024-01-15"
✅ Válido: "2024/01/15 10:30:00"
✅ Válido: "GETDATE()"
✅ Válido: "NOW()"
❌ Inválido: "abc123"
Tooltip: "❌ Solo fechas (ej: 2024-01-15) o GETDATE()"
```

---

#### ✔️ Tipo Booleano
**Tipos afectados**: `BIT`

**Restricciones**:
- ✅ Permite: `0`, `1`, `true`, `false`, `yes`, `no`, `si`, `sí`
- ❌ Bloquea cualquier otro texto
- 🔄 Validación incremental (permite escribir "tru" antes de "true")

**Ejemplo**:
```
✅ Válido: "1"
✅ Válido: "true"
✅ Válido: "yes"
✅ Válido: "si"
❌ Inválido: "abc"
Tooltip: "❌ Solo: 0, 1, true, false, yes, no"
```

---

#### 📝 Tipos de Texto
**Tipos afectados**: `VARCHAR`, `NVARCHAR`, `CHAR`, `TEXT`, `NTEXT`

**Restricciones**:
- ✅ **Sin restricciones** - Permite cualquier carácter
- 📏 Solo validará longitud posteriormente

---

### 2️⃣ Funciones JavaScript Implementadas

#### `setupInputValidationForType(inputElement, sqlType)`
Configura la validación en tiempo real para un input específico según su tipo SQL.

**Parámetros**:
- `inputElement`: Elemento DOM del input de default value
- `sqlType`: Tipo SQL seleccionado (ej: "INT", "VARCHAR(100)")

**Funcionalidad**:
1. Remueve listeners anteriores (si existen)
2. Crea función de validación según tipo
3. Aplica validación a eventos `keypress` y `paste`
4. Configura atributos HTML (`inputmode`, `pattern`)
5. Guarda referencia del listener para limpieza posterior

**Ejemplo de uso**:
```javascript
const input = document.getElementById('default-ventas-5');
setupInputValidationForType(input, 'INT');
// Ahora el input solo acepta números enteros
```

---

#### `showTemporaryTooltip(element, message)`
Muestra un tooltip temporal sobre el input cuando se intenta escribir un valor inválido.

**Parámetros**:
- `element`: Elemento DOM sobre el que mostrar el tooltip
- `message`: Mensaje de error a mostrar

**Características**:
- 🎨 Fondo rojo (`#dc3545`)
- ⏱️ Desaparece automáticamente después de 2 segundos
- 🎭 Animación de fade in/out
- 📍 Posicionado debajo del input
- 🔝 `z-index: 10000` para estar siempre visible

**Ejemplo**:
```javascript
showTemporaryTooltip(inputElement, '❌ Solo números enteros permitidos');
```

---

#### Integración con `onSqlTypeChange()`
Cuando el usuario cambia el tipo SQL, automáticamente:
1. Actualiza el placeholder del input
2. **Aplica la validación en tiempo real** → `setupInputValidationForType()`
3. Valida el valor existente (si hay uno)
4. Ofrece limpiar el valor si es inválido

**Antes**:
```javascript
function onSqlTypeChange(...) {
    // Solo actualizaba placeholder
    defaultInput.placeholder = newPlaceholder;
}
```

**Ahora**:
```javascript
function onSqlTypeChange(...) {
    // Actualiza placeholder
    defaultInput.placeholder = newPlaceholder;
    
    // 🆕 Aplica validación en tiempo real
    setupInputValidationForType(defaultInput, selectedType);
    
    // Valida valor existente
    if (!isValidDefaultForType(currentValue, selectedType)) {
        // Ofrecer limpiar...
    }
}
```

---

#### Integración con `updateColumnSelection()`
Cuando el usuario selecciona una columna, automáticamente:
1. Muestra la configuración de la columna
2. Obtiene el tipo SQL actual del selector
3. **Aplica la validación en tiempo real** → `setupInputValidationForType()`

**Código agregado**:
```javascript
if (defaultInput) {
    const sqlType = typeSelector ? typeSelector.value : defaultInput.dataset.sqlType;
    const contextualPlaceholder = getPlaceholderForType(sqlType);
    defaultInput.placeholder = contextualPlaceholder;
    
    // 🆕 APLICAR VALIDACIÓN EN TIEMPO REAL
    setupInputValidationForType(defaultInput, sqlType);
}
```

---

### 3️⃣ Validación de Pegado (Paste)

Cuando el usuario pega contenido con `Ctrl+V`:
1. Se permite el pegado inicial
2. Después de 10ms se valida el contenido pegado
3. Si es inválido:
   - Muestra tooltip de error
   - **Limpia el campo automáticamente**

**Código**:
```javascript
inputElement.addEventListener('paste', (e) => {
    setTimeout(() => {
        const pastedValue = inputElement.value;
        if (!isValidDefaultForType(pastedValue, sqlType)) {
            showTemporaryTooltip(inputElement, `❌ Valor pegado no es válido para tipo ${sqlType}`);
            inputElement.value = ''; // Limpiar si no es válido
        }
    }, 10);
});
```

---

### 4️⃣ Atributos HTML Dinámicos

#### `inputmode`
Controla el tipo de teclado en dispositivos móviles:

| Tipo SQL | inputmode | Teclado Móvil |
|----------|-----------|---------------|
| INT, SMALLINT, etc. | `numeric` | Solo números |
| FLOAT, DECIMAL, etc. | `decimal` | Números + punto decimal |
| Otros | (ninguno) | Teclado completo |

#### `pattern`
Proporciona validación HTML5 nativa:

| Tipo SQL | pattern | Validación |
|----------|---------|------------|
| INT, SMALLINT, etc. | `-?[0-9]*` | Números enteros |
| FLOAT, DECIMAL, etc. | `-?[0-9]*[.,]?[0-9]*` | Decimales |

---

### 5️⃣ Estilos CSS Agregados

```css
@keyframes fadeInOut {
    0% { opacity: 0; transform: translateY(-5px); }
    10% { opacity: 1; transform: translateY(0); }
    90% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-5px); }
}

.validation-tooltip {
    pointer-events: none;
}
```

---

## 🎬 Flujo de Usuario

### Escenario 1: Cambiar tipo SQL
1. Usuario selecciona tipo SQL: **INT**
2. Sistema actualiza placeholder: "Ej: 0"
3. Sistema aplica validación en tiempo real
4. Usuario intenta escribir "123abc"
5. Sistema permite "123" pero bloquea "abc"
6. Tooltip aparece: "❌ Solo números enteros permitidos"

### Escenario 2: Pegar contenido inválido
1. Usuario selecciona tipo SQL: **FLOAT**
2. Usuario copia "abc123" de otro lugar
3. Usuario pega con Ctrl+V
4. Sistema detecta contenido inválido después de 10ms
5. Sistema limpia el campo automáticamente
6. Tooltip aparece: "❌ Valor pegado no es válido para tipo FLOAT"

### Escenario 3: Escribir fecha
1. Usuario selecciona tipo SQL: **DATE**
2. Sistema permite escribir: "GETDATE()"
3. Sistema permite escribir: "2024-01-15"
4. Sistema bloquea: "fecha invalida"
5. Tooltip aparece: "❌ Solo fechas (ej: 2024-01-15) o GETDATE()"

---

## 🔧 Archivos Modificados

### `excel_multi_sheet_selector.html`

#### Función Nueva: `setupInputValidationForType()`
- **Líneas**: ~1115-1280
- **Tamaño**: ~165 líneas
- **Propósito**: Configurar validación según tipo SQL

#### Función Nueva: `showTemporaryTooltip()`
- **Líneas**: ~1282-1308
- **Propósito**: Mostrar tooltips de error temporales

#### Función Modificada: `onSqlTypeChange()`
- **Línea agregada**: ~1103
- **Cambio**: Llama a `setupInputValidationForType()`

#### Función Modificada: `updateColumnSelection()`
- **Líneas agregadas**: ~1450-1453
- **Cambio**: Aplica validación al inicializar columna

#### Estilos CSS Agregados
- **Líneas**: ~1310-1325
- **Contenido**: Animación `fadeInOut` y clase `.validation-tooltip`

---

## ✅ Ventajas

1. **Prevención Temprana**: Evita que usuarios escriban valores inválidos desde el inicio
2. **Feedback Inmediato**: Tooltips visuales explican por qué se bloqueó la entrada
3. **Experiencia Móvil**: Teclados optimizados según tipo de dato
4. **Validación HTML5**: Atributos `pattern` e `inputmode` para validación nativa
5. **Sin Dependencias**: Solo JavaScript vanilla, sin librerías externas
6. **Reutilizable**: Funciones se pueden aplicar a cualquier input

---

## 🔮 Mejoras Futuras Opcionales

1. **Validación de Rangos**:
   - TINYINT: advertir si valor > 255
   - SMALLINT: advertir si valor > 32,767
   - INT: advertir si valor > 2,147,483,647

2. **Sugerencias Inteligentes**:
   - Detectar si usuario escribió "verdadero" → sugerir "true"
   - Detectar formatos de fecha alternativos → normalizar

3. **Validación de Longitud para VARCHAR**:
   - VARCHAR(50): advertir si valor > 50 caracteres
   - Sugerir aumentar tamaño si es necesario

4. **Historial de Valores**:
   - Recordar valores por defecto usados previamente
   - Ofrecer autocompletado con valores comunes

---

## 📊 Impacto

### Antes
```
❌ Usuario escribe "abc123" en campo INT
❌ Sistema lo acepta
❌ Error aparece al ejecutar proceso
❌ Usuario no sabe qué está mal
❌ Debe revisar todo el archivo nuevamente
```

### Ahora
```
✅ Usuario intenta escribir "abc123" en campo INT
✅ Sistema bloquea "abc" y solo permite "123"
✅ Tooltip explica: "Solo números enteros permitidos"
✅ Usuario corrige de inmediato
✅ Proceso se ejecuta sin errores
```

---

## 🎓 Conclusión

Esta mejora implementa **validación preventiva** que guía al usuario en tiempo real, evitando errores costosos durante la ejecución del proceso. El sistema ahora no solo detecta errores, sino que **previene que se cometan desde el inicio**.

**Fecha de implementación**: 22 de octubre de 2025
**Archivos afectados**: 1 (`excel_multi_sheet_selector.html`)
**Líneas agregadas**: ~250 líneas
**Tests requeridos**: Pendientes (validación manual exitosa)
