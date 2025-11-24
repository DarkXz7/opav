# ✅ CHECKLIST DE PRUEBAS - SISTEMA DE VALIDACIÓN Y NORMALIZACIÓN

## 📋 PRUEBAS FUNCIONALES

### 1. Eliminación de Vista Intermedia `/sheets/`

- [ ] **Subir archivo Excel**
  - Acción: Subir un archivo Excel con múltiples hojas
  - Resultado esperado: Redirige directamente a `/excel/<id>/multi-config/` (NO a `/sheets/`)
  - ❌ Error si: Muestra vista intermedia de selección de hojas

- [ ] **Verificar URL en navegador**
  - Acción: Intentar acceder manualmente a `/automatizacion/excel/<id>/sheets/`
  - Resultado esperado: Error 404 (ruta no existe)
  - ❌ Error si: La ruta funciona

### 2. Renombrado de Hoja Activa

- [ ] **Input de renombrado visible**
  - Acción: Abrir multi-config
  - Resultado esperado: Se muestra sección "Renombrar Hoja Activa" con input
  - ❌ Error si: No aparece o está oculto

- [ ] **Validación de nombre válido**
  - Acción: Escribir `Ventas 2024` → Clic en "Validar"
  - Resultado esperado: Se normaliza a `ventas_2024`, muestra mensaje verde "✓ Nombre válido: ventas_2024"
  - ❌ Error si: Muestra error o no normaliza

- [ ] **Validación de nombre inválido (duplicado)**
  - Acción: Renombrar dos hojas con el mismo nombre
  - Resultado esperado: Muestra error "El nombre 'ventas_2024' ya existe"
  - ❌ Error si: Permite duplicados

- [ ] **Validación de caracteres especiales**
  - Acción: Escribir `Ventas#2024!`
  - Resultado esperado: Normaliza a `ventas_2024`
  - ❌ Error si: Acepta caracteres inválidos

- [ ] **Solo renombra hoja activa**
  - Acción: Renombrar "Hoja1" a "ventas", cambiar a "Hoja2"
  - Resultado esperado: Input cambia, muestra placeholder "Renombrar 'Hoja2'"
  - ❌ Error si: Renombra todas las hojas simultáneamente

### 3. Posición del Botón "Seleccionar Todas"

- [ ] **Botón debajo de "Columnas disponibles"**
  - Acción: Observar UI
  - Resultado esperado: Botón "Seleccionar todas" está DEBAJO del título "Columnas disponibles"
  - ❌ Error si: Está arriba o en otra posición

### 4. Checkbox de Columnas y Configuración

- [ ] **Seleccionar columna muestra configuración**
  - Acción: Marcar checkbox de una columna
  - Resultado esperado: Aparece sección expandible con: renombrar, tipo SQL, nullable, default value
  - ❌ Error si: No aparece o está oculta

- [ ] **Todos los campos habilitados al seleccionar**
  - Acción: Marcar checkbox
  - Resultado esperado: Input renombrar, selector tipo, checkbox nullable, input default → TODOS habilitados
  - ❌ Error si: Algún campo está desactivado (`disabled`)

- [ ] **Input default habilitado cuando nullable=FALSE**
  - Acción: Marcar columna → Desmarcar "Puede ser NULL"
  - Resultado esperado: Input "Valor por defecto" se HABILITA
  - ❌ Error si: Permanece deshabilitado

- [ ] **Input default deshabilitado cuando nullable=TRUE**
  - Acción: Marcar "Puede ser NULL"
  - Resultado esperado: Input "Valor por defecto" se DESHABILITA
  - ❌ Error si: Permanece habilitado

### 5. Inferencia Automática de Tipos

- [ ] **Columna con números enteros → INT**
  - Acción: Seleccionar columna con valores `[1, 2, 3, 4, 5]`
  - Resultado esperado: Selector muestra "INT", hint: "💡 Sugerido: INT (100% confianza)"
  - ❌ Error si: Sugiere otro tipo

- [ ] **Columna con decimales → FLOAT**
  - Acción: Seleccionar columna con valores `[1.5, 2.3, 3.7]`
  - Resultado esperado: Selector muestra "FLOAT"
  - ❌ Error si: Sugiere INT o VARCHAR

- [ ] **Columna con fechas → DATE**
  - Acción: Seleccionar columna con valores `['2024-01-15', '2024-02-20']`
  - Resultado esperado: Selector muestra "DATE" o "DATETIME2"
  - ❌ Error si: Sugiere VARCHAR

- [ ] **Columna con booleanos → BIT**
  - Acción: Seleccionar columna con valores `['true', 'false', '1', '0']`
  - Resultado esperado: Selector muestra "BIT"
  - ❌ Error si: Sugiere VARCHAR o INT

- [ ] **Columna con texto → VARCHAR**
  - Acción: Seleccionar columna con valores `['Juan', 'María', 'Pedro']`
  - Resultado esperado: Selector muestra "NVARCHAR(50)" o similar
  - ❌ Error si: Sugiere tipo numérico

- [ ] **Valores mixtos muestran advertencia**
  - Acción: Seleccionar columna con valores `[1, 2, 'abc', 4]`
  - Resultado esperado: Hint muestra "⚠️ Tipos mixtos detectados"
  - ❌ Error si: No muestra advertencia

### 6. Placeholder Dinámico Según Tipo SQL

- [ ] **INT → Placeholder '0'**
  - Acción: Seleccionar tipo INT
  - Resultado esperado: Input default muestra placeholder "Ej: 0"
  - ❌ Error si: Muestra otro placeholder

- [ ] **FLOAT → Placeholder '0.0'**
  - Acción: Seleccionar tipo FLOAT
  - Resultado esperado: Input default muestra placeholder "Ej: 0.0"

- [ ] **DATE → Placeholder 'GETDATE()'**
  - Acción: Seleccionar tipo DATE
  - Resultado esperado: Input default muestra placeholder "Ej: 2025-01-01 o GETDATE()"

- [ ] **VARCHAR → Placeholder ''**
  - Acción: Seleccionar tipo NVARCHAR
  - Resultado esperado: Input default muestra placeholder "Ej: ''"

- [ ] **BIT → Placeholder '0'**
  - Acción: Seleccionar tipo BIT
  - Resultado esperado: Input default muestra placeholder "Ej: 0 o 1"

### 7. Normalización de Valores (Backend)

- [ ] **INT vacío + NO nullable → 0**
  - Acción: Configurar columna "edad" como INT, nullable=FALSE, subir Excel con celdas vacías
  - Resultado esperado: SQL Server recibe `0` en celdas vacías
  - ❌ Error si: Recibe NULL o error de constraint

- [ ] **FLOAT vacío + NO nullable → 0.0**
  - Acción: Configurar "salario" como FLOAT, nullable=FALSE, celdas vacías
  - Resultado esperado: SQL Server recibe `0.0`

- [ ] **VARCHAR vacío + NO nullable → ''**
  - Acción: Configurar "nombre" como VARCHAR, nullable=FALSE, celdas vacías
  - Resultado esperado: SQL Server recibe `''` (string vacío)

- [ ] **DATE vacío + NO nullable → GETDATE()**
  - Acción: Configurar "fecha" como DATE, nullable=FALSE, default='GETDATE()', celdas vacías
  - Resultado esperado: SQL Server inserta fecha actual
  - ❌ Error si: Inserta NULL o error

- [ ] **BIT 'true'/'yes'/'sí' → 1**
  - Acción: Subir Excel con valores `['true', 'yes', 'sí', '1']` en columna BIT
  - Resultado esperado: SQL Server recibe `1` en todos los casos

- [ ] **BIT 'false'/'no' → 0**
  - Acción: Valores `['false', 'no', '0']`
  - Resultado esperado: SQL Server recibe `0`

- [ ] **INT con string '123' → 123**
  - Acción: Subir Excel con "123" como texto en columna INT
  - Resultado esperado: SQL Server recibe `123` (convertido)

- [ ] **INT con 'abc' + NO nullable → 0**
  - Acción: Subir "abc" en columna INT con nullable=FALSE
  - Resultado esperado: Convierte a `0`, muestra warning en logs

- [ ] **VARCHAR trunca si excede longitud**
  - Acción: Subir texto de 100 caracteres en columna NVARCHAR(50)
  - Resultado esperado: Inserta primeros 50 caracteres, warning en logs

### 8. Validación en Tiempo Real

- [ ] **Renombrar columna con caracteres inválidos**
  - Acción: Escribir `columna#1` en input de renombrar
  - Resultado esperado: Muestra advertencia "Caracteres inválidos: #"
  - ❌ Error si: Acepta sin validar

- [ ] **Renombrar columna con nombre duplicado**
  - Acción: Renombrar dos columnas con el mismo nombre
  - Resultado esperado: Muestra error "El nombre 'columna' ya existe"

### 9. Logging Mejorado

- [ ] **Log muestra SQL generado**
  - Acción: Ejecutar proceso → Ver logs
  - Resultado esperado: Logs muestran `INSERT INTO tabla (col1, col2) VALUES (?, ?)`
  - ❌ Error si: No muestra SQL

- [ ] **Log muestra filas afectadas**
  - Acción: Procesar 100 filas
  - Resultado esperado: Logs muestran "Insertados 100/100 registros"

- [ ] **Log muestra columnas problemáticas**
  - Acción: Subir valores inválidos
  - Resultado esperado: Logs muestran "Columna 'edad': Error al convertir 'abc' a INT"

- [ ] **Log muestra stacktrace en errores**
  - Acción: Provocar error (ej: tabla no existe)
  - Resultado esperado: Logs muestran traceback completo

### 10. Persistencia de Configuración

- [ ] **Guardar configuración de tipos**
  - Acción: Configurar tipos → Ejecutar proceso
  - Resultado esperado: Tabla `ProcesosGuardados` contiene JSON con tipos configurados
  - ❌ Error si: No se guarda o JSON está vacío

- [ ] **Reutilizar configuración en siguiente ejecución**
  - Acción: Ejecutar mismo proceso dos veces
  - Resultado esperado: Segunda ejecución usa tipos guardados, no vuelve a inferir
  - ❌ Error si: Pierde configuración

---

## 🧪 PRUEBAS UNITARIAS

### Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest automatizacion/tests/test_validation_system.py -v

# Ejecutar test específico
pytest automatizacion/tests/test_validation_system.py::TestNormalizeName::test_basic_normalization -v

# Ver cobertura
pytest automatizacion/tests/test_validation_system.py --cov=automatizacion.utils --cov-report=html
```

### Resultados Esperados

- [ ] **test_normalize_name**: 5/5 tests pasan
  - `test_basic_normalization`: ✅
  - `test_special_characters`: ✅
  - `test_starts_with_number`: ✅
  - `test_avoid_duplicates`: ✅
  - `test_empty_name`: ✅

- [ ] **test_infer_sql_type**: 7/7 tests pasan
  - `test_integer_type`: ✅
  - `test_float_type`: ✅
  - `test_boolean_type`: ✅
  - `test_date_type`: ✅
  - `test_varchar_type`: ✅
  - `test_mixed_types_warning`: ✅
  - `test_nullable_detection`: ✅

- [ ] **test_normalize_value_by_type**: 10/10 tests pasan
  - `test_int_empty_not_nullable`: ✅
  - `test_int_empty_nullable`: ✅
  - `test_int_valid_conversion`: ✅
  - `test_float_requires_decimal`: ✅
  - `test_varchar_empty_not_nullable`: ✅
  - `test_varchar_truncation`: ✅
  - `test_date_getdate`: ✅
  - `test_date_string_conversion`: ✅
  - `test_bit_true_values`: ✅
  - `test_bit_false_values`: ✅

- [ ] **test_normalize_dataframe**: 2/2 tests pasan
  - `test_basic_normalization`: ✅
  - `test_mixed_type_handling`: ✅

---

## 🔍 PRUEBAS DE INTEGRACIÓN

### Caso 1: Flujo Completo con Excel Simple

**Archivo de prueba**: `datos_prueba_simple.xlsx`

| ID  | Nombre | Edad | Activo | Fecha Ingreso |
|-----|--------|------|--------|---------------|
| 1   | Juan   | 25   | true   | 2024-01-15    |
| 2   | María  | 30   | false  | 2024-02-20    |
| 3   | Pedro  |      | 1      |               |

**Pasos**:
1. Subir archivo
2. Renombrar hoja "Hoja1" → "empleados"
3. Seleccionar todas las columnas
4. Configurar:
   - ID: INT, nullable=FALSE, default=0
   - Nombre: NVARCHAR(100), nullable=TRUE
   - Edad: INT, nullable=TRUE
   - Activo: BIT, nullable=FALSE, default=0
   - Fecha Ingreso: DATE, nullable=TRUE
5. Ejecutar proceso

**Resultado esperado en SQL Server**:

```sql
SELECT * FROM empleados;

-- Resultado:
-- ID | Nombre | Edad | Activo | Fecha_Ingreso
-- 1  | Juan   | 25   | 1      | 2024-01-15
-- 2  | María  | 30   | 0      | 2024-02-20
-- 3  | Pedro  | NULL | 1      | NULL
```

- [ ] **Fila 1**: ✅ Todos los valores correctos
- [ ] **Fila 2**: ✅ Activo convertido a 0
- [ ] **Fila 3**: ✅ Edad NULL, Fecha NULL (porque nullable=TRUE)

### Caso 2: Valores Mixtos con Normalización

**Archivo de prueba**: `datos_prueba_mixtos.xlsx`

| Cantidad | Precio  | Estado   |
|----------|---------|----------|
| 10       | 150.50  | activo   |
| abc      | 200     | 1        |
| 30       | xyz     | inactivo |

**Configuración**:
- Cantidad: INT, nullable=FALSE, default=0
- Precio: FLOAT, nullable=FALSE, default=0.0
- Estado: BIT, nullable=FALSE, default=0

**Resultado esperado en SQL Server**:

```sql
SELECT * FROM productos;

-- Resultado:
-- Cantidad | Precio | Estado
-- 10       | 150.50 | 1
-- 0        | 200.00 | 1
-- 30       | 0.00   | 0
```

- [ ] **Fila 2**: ✅ 'abc' convertido a 0, 200 convertido a 200.0, '1' convertido a 1
- [ ] **Fila 3**: ✅ 'xyz' convertido a 0.0, 'inactivo' no reconocido → 0
- [ ] **Logs**: ✅ Muestran warnings de conversiones

### Caso 3: Fechas con GETDATE()

**Archivo de prueba**: `datos_prueba_fechas.xlsx`

| Nombre  | Fecha Registro |
|---------|----------------|
| Evento1 | 2024-01-15     |
| Evento2 |                |

**Configuración**:
- Nombre: NVARCHAR(50), nullable=FALSE, default=''
- Fecha Registro: DATE, nullable=FALSE, default='GETDATE()'

**Resultado esperado en SQL Server**:

```sql
SELECT * FROM eventos;

-- Resultado:
-- Nombre  | Fecha_Registro
-- Evento1 | 2024-01-15
-- Evento2 | 2025-05-15  -- (fecha actual al momento de inserción)
```

- [ ] **Fila 2**: ✅ Fecha vacía reemplazada por fecha actual

---

## 🐛 BUGS CONOCIDOS CORREGIDOS

### Bug 1: Input Default Value Desactivado al Inicio

**Antes**:
```javascript
// ❌ Input desactivado aunque nullable=FALSE
<input ... disabled>
```

**Después**:
```javascript
// ✅ Habilitado correctamente según nullable
if (defaultInput) {
    const isNullable = nullableCheckbox ? nullableCheckbox.checked : true;
    defaultInput.disabled = isNullable;
}
```

**Prueba**:
- [ ] Seleccionar columna → Desmarcar "Puede ser NULL"
- [ ] Verificar: Input default DEBE estar habilitado

### Bug 2: Checkbox Nullable No Visible por Campo

**Antes**:
```html
<!-- ❌ Checkbox solo al seleccionar todo -->
<div id="global-nullable-checkbox">
```

**Después**:
```html
<!-- ✅ Checkbox POR CADA columna -->
<div class="column-config">
    <input type="checkbox" id="nullable-{{ forloop.counter }}" ...>
</div>
```

**Prueba**:
- [ ] Seleccionar UNA columna
- [ ] Verificar: Se muestra checkbox "Puede ser NULL" para ESA columna

### Bug 3: Vista `/sheets/` Innecesaria

**Antes**:
```python
# ❌ Ruta intermedia que causa confusión
path('excel/<int:source_id>/sheets/', views.excel_sheet_selector, ...)
```

**Después**:
```python
# ✅ Ruta comentada/eliminada
# path('excel/<int:source_id>/sheets/', ...)  # ELIMINADO
```

**Prueba**:
- [ ] Subir Excel
- [ ] Verificar: Redirige directamente a `/multi-config/`, NO pasa por `/sheets/`

---

## 📊 MÉTRICAS DE ÉXITO

### Cobertura de Código

```bash
pytest --cov=automatizacion.utils --cov-report=term-missing
```

**Objetivos**:
- [ ] `validators.py`: >90% cobertura
- [ ] `models.py` (métodos modificados): >80% cobertura
- [ ] `views.py` (vistas modificadas): >75% cobertura

### Rendimiento

- [ ] **Inferencia de tipos**: <500ms para archivo de 10,000 filas
- [ ] **Normalización de DataFrame**: <1s para 50,000 filas
- [ ] **Validación AJAX**: <200ms por request

### UX

- [ ] **Clicks reducidos**: Eliminación de vista `/sheets/` reduce 1 click
- [ ] **Feedback instantáneo**: Validación en tiempo real (<300ms)
- [ ] **Mensajes claros**: Errores descriptivos (no técnicos)

---

## 🚀 DEPLOYMENT

### Pre-Deployment

- [ ] Ejecutar todos los tests unitarios
- [ ] Verificar migraciones aplicadas
- [ ] Backup de base de datos
- [ ] Verificar logs funcionan correctamente

### Post-Deployment

- [ ] Monitorear logs por 24h
- [ ] Revisar reportes de errores
- [ ] Solicitar feedback de usuarios beta

---

## 📝 NOTAS ADICIONALES

### Dependencias Nuevas

```python
# requirements.txt (verificar)
pandas>=1.5.0
pyodbc>=4.0.35
pytest>=7.0.0
pytest-cov>=4.0.0
```

### Variables de Entorno

```bash
# .env (si aplica)
DEBUG=True  # Para ver logs detallados en desarrollo
SQL_SERVER_LOG_LEVEL=INFO
```

### Comandos Útiles

```bash
# Limpiar cache de pytest
pytest --cache-clear

# Ejecutar solo tests fallidos
pytest --lf

# Ver output completo
pytest -v -s

# Generar reporte HTML de cobertura
pytest --cov=automatizacion.utils --cov-report=html
# Abrir: htmlcov/index.html
```

---

## ✅ APROBACIÓN FINAL

Una vez completadas TODAS las casillas:

- [ ] **Funcionalidad**: 10/10 pruebas funcionales pasan
- [ ] **Tests unitarios**: 24/24 tests pasan
- [ ] **Integración**: 3/3 casos completos pasan
- [ ] **Bugs corregidos**: 3/3 bugs solucionados
- [ ] **Cobertura**: >85% en módulos críticos
- [ ] **Performance**: Cumple métricas
- [ ] **Documentación**: `IMPLEMENTACION_COMPLETA.md` actualizado

**Firmado por**: _________________  
**Fecha**: _________________  
**Versión**: 1.0.0
