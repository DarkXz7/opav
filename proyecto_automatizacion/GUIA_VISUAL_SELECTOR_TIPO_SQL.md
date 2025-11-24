# 🎨 Guía Visual: Selector de Tipo SQL

## 📸 Interfaz ANTES vs DESPUÉS

### **ANTES: Tipo SQL Solo Lectura**

```
┌────────────────────────────────────────────────────────────────┐
│  CONFIGURACIÓN DE COLUMNAS                                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ☑ fecha                                                       │
│     Tipo: (NVARCHAR(255))  ← Solo lectura, no editable       │
│     └─ Renombrar: [fecha_________________]                    │
│                                                                │
│  ☑ codigo                                                      │
│     Tipo: (NVARCHAR(255))  ← Usuario no puede cambiar        │
│     └─ Renombrar: [codigo________________]                    │
│                                                                │
│  ☑ cantidad                                                    │
│     Tipo: (NVARCHAR(255))  ← Detectó mal pero no se puede    │
│                                  corregir manualmente          │
│     └─ Renombrar: [cantidad______________]                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### **AHORA: Tipo SQL Editable con Selector**

```
┌────────────────────────────────────────────────────────────────────┐
│  CONFIGURACIÓN DE COLUMNAS                                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ☑ fecha      [DATE ▼]                  [fecha_____________]      │
│               └─ Click para cambiar tipo SQL                      │
│                                                                    │
│     ├─ ☐ Permitir NULL                                           │
│     └─ Valor por defecto: [GETDATE()_____________] [Sugerir]     │
│                            └─ Sugerencia actualizada según tipo   │
│                                                                    │
│  ☑ codigo     [NVARCHAR(255) ▼]        [codigo_____________]      │
│                                                                    │
│     ├─ ☐ Permitir NULL                                           │
│     └─ Valor por defecto: ['PENDIENTE'___________] [Sugerir]     │
│                                                                    │
│  ☑ cantidad   [INT ▼]                   [cantidad___________]     │
│               └─ Usuario cambió de NVARCHAR a INT                │
│                                                                    │
│     ├─ ☐ Permitir NULL                                           │
│     └─ Valor por defecto: [0_____________________] [Sugerir]     │
│                            └─ Placeholder cambió a '0' automát.  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Selector de Tipo SQL Expandido

### **Vista del Dropdown (cuando haces click)**

```
┌─────────────────────────┐
│  [INT ▼]               │ ← Click aquí
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Numéricos              │
├─────────────────────────┤
│  INT                   │ ← Seleccionado
│  BIGINT                │
│  SMALLINT              │
│  TINYINT               │
│  FLOAT                 │
│  REAL                  │
│  DECIMAL(10,2)         │
│  MONEY                 │
├─────────────────────────┤
│ Fecha/Hora             │
├─────────────────────────┤
│  DATE                  │
│  DATETIME              │
│  DATETIME2             │
│  SMALLDATETIME         │
│  TIME                  │
├─────────────────────────┤
│ Texto                  │
├─────────────────────────┤
│  VARCHAR(50)           │
│  VARCHAR(255)          │
│  NVARCHAR(50)          │
│  NVARCHAR(255)         │
│  NVARCHAR(500)         │
│  TEXT                  │
│  NTEXT                 │
├─────────────────────────┤
│ Booleano               │
├─────────────────────────┤
│  BIT                   │
└─────────────────────────┘
```

---

## 🔄 Flujo de Interacción

### **Paso 1: Ver Tipo Detectado**

```
Usuario selecciona columna "cantidad"
↓
Sistema muestra: [NVARCHAR(255) ▼]  ← Tipo detectado automáticamente
                 Placeholder: "" (vacío)
```

### **Paso 2: Cambiar Tipo**

```
Usuario hace click en [NVARCHAR(255) ▼]
↓
Se abre dropdown con 21 opciones
↓
Usuario selecciona: INT
```

### **Paso 3: Actualización Automática**

```
🔄 Sistema detecta cambio de tipo
↓
✅ Actualiza selector: [INT ▼]
✅ Actualiza placeholder: "0"
✅ Actualiza data-attribute: data-sql-type="INT"
✅ Log en consola: "🔄 Tipo SQL cambiado para 'cantidad': INT"
                   "✅ Placeholder actualizado: '0'"
```

### **Paso 4: Validación (si hay valor previo)**

```
Si había un default anterior incompatible:
↓
⚠️ Alerta: "El valor por defecto 'abc' no parece válido para 
           el tipo INT. ¿Deseas limpiarlo?"
           
           [Sí] [No]
           
Si usuario hace click en "Sí":
  ✅ Input se limpia: [_____________________]
  
Si usuario hace click en "No":
  ⚠️ Mantiene valor: [abc_________________]
  (Podría causar error más tarde)
```

---

## 🎨 Estados Visuales del Selector

### **Estado 1: Deshabilitado (columna NO seleccionada)**

```
☐ cantidad    [INT ▼]  ← Gris, no clickeable
              └─ disabled
```

### **Estado 2: Habilitado (columna seleccionada)**

```
☑ cantidad    [INT ▼]  ← Azul, clickeable
              └─ enabled
```

### **Estado 3: Con Tooltip (hover)**

```
☑ cantidad    [INT ▼] ← Mouse encima
              ↓
         ┌────────────────────────────────────┐
         │ Tipo de dato SQL. Puedes cambiarlo│
         │ si la detección automática no es  │
         │ correcta.                          │
         └────────────────────────────────────┘
```

---

## 📊 Ejemplos de Cambios Comunes

### **Ejemplo 1: Corregir Número Detectado como Texto**

```
ANTES:
☑ edad    (NVARCHAR(255))  [edad________]
          └─ No editable

AHORA:
☑ edad    [INT ▼]          [edad________]
          └─ Click → Cambio a INT
          
Placeholder: "" → "0"
```

### **Ejemplo 2: Cambiar Fecha de Texto a DATE**

```
ANTES:
☑ fecha   (NVARCHAR(255))  [fecha_______]

AHORA:
☑ fecha   [DATE ▼]         [fecha_______]
          └─ Click → Cambio a DATE
          
Placeholder: "" → "GETDATE()"
Default: [GETDATE()__________]
```

### **Ejemplo 3: Optimizar Tamaño de Columna**

```
ANTES:
☑ codigo  (NVARCHAR(255))  [codigo______]
          └─ Desperdicia 245 caracteres

AHORA:
☑ codigo  [VARCHAR(50) ▼]  [codigo______]
          └─ Click → Cambio a VARCHAR(50)
          
Ahorra: 205 caracteres por registro
```

---

## 🎬 Animación del Flujo Completo

```
1. Usuario selecciona columna
   ☐ → ☑ cantidad
   
2. Selector se habilita
   [NVARCHAR(255) ▼] (gris) → [NVARCHAR(255) ▼] (azul)
   
3. Usuario hace click
   [NVARCHAR(255) ▼] → Dropdown se abre
   
4. Usuario selecciona INT
   Dropdown cierra → [INT ▼]
   
5. Placeholder se actualiza
   [_____] → [0_____]
   
6. Usuario configura default
   [0_____] → [0]
   
7. Usuario desmarca nullable
   ☑ Permitir NULL → ☐ Permitir NULL
   
8. Usuario guarda proceso
   ✅ column_mappings guardado:
   {
     "cantidad": {
       "sql_type": "INT",  ← Tipo seleccionado por usuario
       "nullable": false,
       "default_value": "0"
     }
   }
```

---

## 🔍 Detalles Técnicos de la UI

### **HTML del Selector**

```html
<select class="form-select form-select-sm column-type-selector" 
        id="type-hoja-2-3"
        data-sheet="hoja 2"
        data-column="cantidad"
        onchange="onSqlTypeChange('hoja 2', 'cantidad', '3', 'hoja-2')"
        disabled>
    <optgroup label="Numéricos">
        <option value="INT" selected>INT</option>
        <!-- ... más opciones ... -->
    </optgroup>
</select>
```

### **Clases CSS**

```css
.column-type-selector {
    /* Bootstrap form-select-sm ya tiene estilos */
}

.column-type-selector:disabled {
    background-color: #e9ecef;
    cursor: not-allowed;
}

.column-type-selector:enabled {
    background-color: #fff;
    cursor: pointer;
}
```

### **Atributos Data**

```html
data-sheet="hoja 2"      ← Identifica la hoja
data-column="cantidad"   ← Identifica la columna
```

---

## 🎯 Tips de Uso

### **Tip 1: Tipos Numéricos**

```
Si tus datos son números enteros: INT, BIGINT
Si tus datos son decimales: FLOAT, DECIMAL(10,2)
Si tus datos son moneda: MONEY

Ejemplo:
  Edad: 18, 25, 30 → INT
  Precio: 99.99, 150.50 → DECIMAL(10,2)
  Población: 1500000 → BIGINT
```

### **Tip 2: Tipos de Texto**

```
Si todos son ASCII: VARCHAR
Si tienen caracteres especiales (ñ, á, ü): NVARCHAR

Tamaño según longitud:
  Códigos cortos (max 10 chars): VARCHAR(50)
  Nombres (max 100 chars): NVARCHAR(255)
  Descripciones largas: NVARCHAR(500) o TEXT

Ejemplo:
  Código: "A001" → VARCHAR(50)
  Nombre: "José García" → NVARCHAR(255)
  Descripción larga → NTEXT
```

### **Tip 3: Tipos de Fecha**

```
Solo fecha: DATE
Fecha + hora: DATETIME
Alta precisión: DATETIME2

Ejemplo:
  Fecha de nacimiento: 1990-01-15 → DATE
  Registro de timestamp: 2024-01-15 14:30:00 → DATETIME
```

---

## 📋 Checklist Visual

Al configurar cada columna, verifica:

- [ ] ✅ Tipo SQL seleccionado es correcto
- [ ] ✅ Placeholder de default_value tiene sentido
- [ ] ✅ Nullable está configurado apropiadamente
- [ ] ✅ Default value es válido para el tipo
- [ ] ✅ Nombre de columna es el correcto

---

## 🎉 Resumen Visual

**Antes**: Solo podías ver el tipo detectado
**Ahora**: Puedes ver, cambiar y validar el tipo

**Ventajas**:
✅ Control total
✅ Corrección fácil
✅ Sugerencias inteligentes
✅ Validación automática
✅ Feedback inmediato

**¡La interfaz es ahora mucho más flexible y poderosa!** 🚀
