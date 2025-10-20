# 🎨 Visualización de Cambios: Normalización de Datos SQL

## 📍 Dónde Ver Los Efectos de la Normalización

La normalización de datos **NO tiene interfaz de usuario específica** durante la creación del proceso, pero **SÍ afecta** la calidad de los datos insertados. Aquí está dónde y cómo verás los resultados:

---

## 1️⃣ Durante la Creación del Proceso (Frontend)

### 🔧 **Vista: Selección de Columnas**
**URL**: `http://127.0.0.1:8000/automatizacion/sql/connection/XX/table/NOMBRE_TABLA/columns/`

**Lo que VES**:
```
┌─────────────────────────────────────────────┐
│  Columnas de dbo.TestNormalizacion          │
├─────────────────────────────────────────────┤
│  ☑ ID              → [Renombrar...]         │
│  ☑ Nombre          → [Renombrar...]         │
│  ☑ Edad            → [Renombrar...]         │
│  ☑ Salario         → [Renombrar...]         │
│  ☑ FechaIngreso    → [Renombrar...]         │
│  ☑ Activo          → [Renombrar...]         │
└─────────────────────────────────────────────┘
      [Guardar Proceso]  [Guardar y Ejecutar]
```

**Lo que NO VES**:
- ❌ No hay validación de tipos en este punto
- ❌ No se muestran advertencias sobre datos problemáticos
- ❌ No hay preview de normalización

**Por qué**: La normalización ocurre **durante la ejecución**, no durante la configuración.

---

## 2️⃣ Durante la Ejecución del Proceso (Logs del Servidor)

### 🖥️ **Vista: Terminal donde corre Django**

Cuando ejecutas un proceso, **LA CONSOLA DEL SERVIDOR** muestra:

```
🚀 Iniciando ejecución del proceso: Test Normalización Datos (ID: 123)
📋 Columnas seleccionadas: {'dbo.TestNormalizacion': ['ID', 'Nombre', 'Edad', ...]}
📋 Mapeos de columnas: None

🔍 DEBUG: Iniciando guardado de DataFrame 'Test_Normalizacion_dbo_TestNormalizacion'
🔍 DEBUG: DataFrame shape: (7, 6)
🔍 DEBUG: DataFrame columnas: ['ID', 'Nombre', 'Edad', 'Salario', 'FechaIngreso', 'Activo']

⚠️ Advertencias de normalización antes de insertar: [
    {'column': 'Edad', 'count': 1, 'example': 'abc'},
    {'column': 'Salario', 'count': 1, 'example': 'N/A'},
    {'column': 'FechaIngreso', 'count': 1, 'example': 'fecha_invalida'}
]

📋 Creando tabla 'Test_Normalizacion_dbo_TestNormalizacion' con estructura del DataFrame...
✅ Tabla 'Test_Normalizacion_dbo_TestNormalizacion' creada exitosamente
   📊 Columnas: ['ID', 'Nombre', 'Edad', 'Salario', 'FechaIngreso', 'Activo']
   📈 Filas a insertar: 7

🔍 SQL INSERT: INSERT INTO [Test_Normalizacion_dbo_TestNormalizacion] ...
   ✅ Inserción masiva exitosa. Registros afectados: 7
```

**Dónde verlo**:
```powershell
# En la terminal donde ejecutaste:
python manage.py runserver

# Deberías ver output en tiempo real cuando ejecutas un proceso
```

---

## 3️⃣ Después de la Ejecución (Frontend - Vista del Proceso)

### 📊 **Vista: Detalles del Proceso**
**URL**: `http://127.0.0.1:8000/automatizacion/process/123/`

**Lo que VES actualmente**:

```
┌─────────────────────────────────────────────────────────────┐
│  Proceso: Test Normalización Datos                          │
├─────────────────────────────────────────────────────────────┤
│  Estado: ✅ Completado                                      │
│  Última ejecución: 2025-10-17 15:30:00                     │
│  Registros procesados: 7                                    │
│  Duración: 2.5 segundos                                     │
└─────────────────────────────────────────────────────────────┘

         [Ejecutar Proceso]  [Ver Logs]  [Editar]
```

**Lo que DEBERÍAS ver** (después de mis mejoras):

```
┌─────────────────────────────────────────────────────────────┐
│  Proceso: Test Normalización Datos                          │
├─────────────────────────────────────────────────────────────┤
│  Estado: ✅ Completado con advertencias                     │
│  Última ejecución: 2025-10-17 15:30:00                     │
│  Registros procesados: 7                                    │
│  Registros con errores normalizados: 3                      │
│  Duración: 2.5 segundos                                     │
│                                                              │
│  ⚠️ Advertencias de normalización:                          │
│    • Columna 'Edad': 1 valor inválido → NULL               │
│      Ejemplo: 'abc'                                         │
│    • Columna 'Salario': 1 valor inválido → NULL            │
│      Ejemplo: 'N/A'                                         │
│    • Columna 'FechaIngreso': 1 valor inválido → NULL       │
│      Ejemplo: 'fecha_invalida'                              │
└─────────────────────────────────────────────────────────────┘

         [Ejecutar Proceso]  [Ver Logs Completos]  [Editar]
```

---

## 4️⃣ En la Base de Datos Destino (SQL Server)

### 🗄️ **Lo más importante: Los DATOS reales**

**Antes de la normalización** (comportamiento antiguo):
```sql
-- El proceso fallaba o insertaba valores incorrectos
-- Columnas numéricas con strings causaban errores
-- Fechas inválidas rompían la inserción
```

**Después de la normalización** (comportamiento nuevo):
```sql
USE DestinoAutomatizacion;
GO

SELECT * FROM Test_Normalizacion_dbo_TestNormalizacion;
```

**Resultado**:
```
ID  | Nombre         | Edad  | Salario | FechaIngreso        | Activo
----|----------------|-------|---------|---------------------|--------
1   | Juan Pérez     | 25.0  | 1500.50 | 2020-01-15 00:00:00 | 1.0
2   | María López    | 30.0  | 2000.00 | 2021-06-20 00:00:00 | 1.0
3   | Carlos Gómez   | NULL  | NULL    | NULL                | NULL
4   | Ana Martínez   | NULL  | NULL    | NULL                | NULL
5   | Pedro Ruiz     | NULL  | NULL    | NULL                | NULL
6   | Laura Torres   | 45.5  | 3500.75 | 2023-03-10 00:00:00 | 0.0
7   | Roberto Díaz   | 50.0  | 4000.00 | 2024-05-01 00:00:00 | 0.0
```

**¡Los cambios importantes!**:
- ✅ **Fila 3**: `Edad='abc'` → `NULL` (antes: error o dato corrupto)
- ✅ **Fila 3**: `Salario='N/A'` → `NULL` (antes: error o '0')
- ✅ **Fila 3**: `FechaIngreso='fecha_invalida'` → `NULL` (antes: error o fecha incorrecta)
- ✅ **Fila 4**: Cadenas vacías `''` → `NULL` (antes: strings vacíos)
- ✅ **Fila 5**: `NULL` preservado (antes: podía convertirse a '0' o '')

---

## 🎬 Flujo Completo Visualizado

```
┌─────────────────┐
│   1. FRONTEND   │
│  Crear Proceso  │
└────────┬────────┘
         │
         │ Seleccionas columnas
         │ Guardas proceso
         ▼
┌─────────────────┐
│   2. BACKEND    │
│  Guardar Config │
└────────┬────────┘
         │
         │ Click "Ejecutar"
         ▼
┌─────────────────────────────────────┐
│   3. PROCESO DE MIGRACIÓN           │
│                                     │
│   a) Extraer datos de SQL origen   │
│      DataFrame con tipos mixtos    │
│                                     │
│   b) 🆕 NORMALIZACIÓN              │
│      normalize_df_for_sql()        │
│      - Detecta tipos               │
│      - Convierte valores           │
│      - Identifica problemas        │
│                                     │
│   c) Crear tabla destino           │
│      CREATE TABLE con tipos SQL    │
│                                     │
│   d) Insertar datos normalizados   │
│      INSERT con valores limpios    │
└────────┬────────────────────────────┘
         │
         │ Resultado
         ▼
┌─────────────────────────────────────┐
│   4. RESULTADOS VISIBLES            │
│                                     │
│   ✅ Consola Servidor:              │
│      - Advertencias de normaliz.   │
│                                     │
│   ✅ Base de Datos:                 │
│      - Datos limpios               │
│      - NULL donde corresponde      │
│                                     │
│   ✅ (FUTURO) Frontend:             │
│      - Badge con advertencias      │
│      - Sección de logs mejorada    │
└─────────────────────────────────────┘
```

---

## 🔍 Cómo Verificar que Funciona

### Prueba Práctica en 5 Pasos:

1. **Crea tabla de prueba en SQL Server**:
   ```sql
   CREATE TABLE TestNormalizacion (
       ID INT,
       Edad NVARCHAR(50),  -- String que debería ser número
       Salario NVARCHAR(50)
   );
   
   INSERT INTO TestNormalizacion VALUES
       (1, '25', '1500.50'),      -- ✅ Válido
       (2, 'abc', 'N/A'),         -- ❌ Inválido
       (3, '', '');               -- ❌ Vacío
   ```

2. **Crea proceso en Django**:
   - Ve a: `http://127.0.0.1:8000/automatizacion/`
   - Selecciona conexión
   - Navega a tabla `TestNormalizacion`
   - Selecciona todas las columnas
   - Guarda como "Test Normalización"

3. **Abre la consola del servidor**:
   - Terminal donde ejecutaste `python manage.py runserver`
   - Mantén visible

4. **Ejecuta el proceso**:
   - Click en "Ejecutar Proceso"
   - **Observa la consola**: Deberías ver advertencias sobre 'abc' y 'N/A'

5. **Verifica resultados en SQL Server**:
   ```sql
   SELECT * FROM DestinoAutomatizacion.dbo.[Test Normalización_TestNormalizacion];
   
   -- Deberías ver:
   -- ID=1, Edad=25.0, Salario=1500.5       ✅
   -- ID=2, Edad=NULL, Salario=NULL         ✅ (abc y N/A convertidos)
   -- ID=3, Edad=NULL, Salario=NULL         ✅ (vacíos convertidos)
   ```

---

## 🎯 Resumen: ¿Dónde Ver Los Cambios?

| Ubicación | Qué Ver | Cuándo |
|-----------|---------|--------|
| **Terminal Django** | ⚠️ Advertencias de normalización | Durante ejecución |
| **SQL Server Destino** | 🗄️ NULL en valores inválidos | Después de ejecución |
| **Frontend (actual)** | ✅ "Proceso completado" | Después de ejecución |
| **Frontend (mejorado)** | ⚠️ Badge con advertencias | Próximamente |

---

## 💡 Mejora Futura: Mostrar en Frontend

Si quieres ver las advertencias directamente en la interfaz web, puedo implementar:

1. **Badge en vista de proceso**:
   ```html
   <span class="badge bg-warning">3 valores normalizados</span>
   ```

2. **Sección expandible con detalles**:
   ```html
   <div class="alert alert-warning">
       <h6>⚠️ Advertencias de normalización:</h6>
       <ul>
           <li>Columna 'Edad': 1 valor inválido (ejemplo: 'abc')</li>
           <li>Columna 'Salario': 1 valor inválido (ejemplo: 'N/A')</li>
       </ul>
   </div>
   ```

3. **Tabla de logs mejorada** con filtro por tipo de mensaje.

**¿Quieres que implemente estas mejoras visuales en el frontend?**

---

## ✅ Conclusión

**Los cambios SÍ están funcionando**, pero son principalmente en:
1. 🖥️ **Backend** (consola del servidor)
2. 🗄️ **Base de datos** (datos limpios con NULL)
3. 📋 **Logs del sistema** (registros de eventos)

Para verlos mejor en el **frontend**, necesitamos agregar componentes visuales adicionales.

¿Te ayudo a implementar la visualización en el frontend?
