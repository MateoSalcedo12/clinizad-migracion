# Sistema de Carga de Códigos CUPS

Este sistema permite cargar y actualizar códigos CUPS desde archivos Excel a la base de datos PostgreSQL.

## Archivos del Sistema

1. **read_cups_data.py**: Clase para leer y procesar los archivos Excel
2. **cups_query.py**: Clase para manejar operaciones de base de datos
3. **load_cups_data.py**: Script principal para ejecutar la carga
4. **setup_codigos_cups_table.sql**: Script SQL para crear/verificar la tabla

## Requisitos Previos

1. **Tabla en PostgreSQL**: La tabla `codigos_cups` debe existir con la siguiente estructura:
   ```sql
   CREATE TABLE codigos_cups (
       id SERIAL PRIMARY KEY,
       codigo_cups VARCHAR(20) NOT NULL UNIQUE,
       nombre_estudio VARCHAR,
       preparacion_especial BOOLEAN DEFAULT FALSE,
       remitido BOOLEAN DEFAULT FALSE
   );
   ```

2. **Archivos Excel**: Deben estar en la misma carpeta que los scripts:
   - `NOMBRES Y CUPS DE EXAMENES QUE REQUIEREN PREPARACION.xlsx`
   - `F-OS048 Exámenes para remitir a laboratorios de referencia.xlsx`

## Instalación

1. Ejecutar el script SQL en pgAdmin para crear/verificar la tabla:
   ```bash
   # En pgAdmin, ejecutar:
   setup_codigos_cups_table.sql
   ```

2. Verificar que los archivos Excel estén en la misma carpeta.

## Uso

### Carga Básica

Ejecutar el script principal:
```bash
python load_cups_data.py
```

### Uso Programático

```python
from read_cups_data import CupsDataReader
from cups_query import CupsQuery

# 1. Cargar datos desde Excel
reader = CupsDataReader()
df = reader.cargar_datos()

# 2. Conectar a base de datos
db = CupsQuery()

# 3. Procesar y cargar
estadisticas = db.procesar_dataframe(df)

# 4. Ver resultados
print(f"Insertados: {estadisticas['insertados']}")
print(f"Actualizados: {estadisticas['actualizados']}")
print(f"Errores: {estadisticas['errores']}")

# 5. Cerrar conexión
db.cerrar_conexion()
```

## Funcionalidades

### 1. Detección de Duplicados
- El sistema identifica registros existentes basándose en `codigo_cups`
- Los registros existentes se **actualizan** con la nueva información
- Los registros nuevos se **insertan**

### 2. Combinación de Archivos
- **Archivo de Preparación**: Marca `preparacion_especial = TRUE`
- **Archivo de Remitidos**: Marca `remitido = TRUE`
- Si un código aparece en ambos archivos, ambas banderas se activan

### 3. Actualización Inteligente
- Si un código ya existe, se actualizan todos sus campos:
  - `nombre_estudio`
  - `preparacion_especial`
  - `remitido`
- Los valores se combinan lógicamente (si está en preparación, se marca como TRUE)

## Estructura de los Archivos Excel

### Archivo 1: Preparación
- **Columna 1**: `nombre_estudio`
- **Columna 2**: `codigo_cups`
- Los encabezados están en la primera fila

### Archivo 2: Remitidos
- **Columna "CUPS"**: `codigo_cups`
- **Columna "ESTUDIO"**: `nombre_estudio`
- Los encabezados están en la fila 6 (índice 6)

## Configuración de Base de Datos

Por defecto, el sistema se conecta a:
- **Host**: 192.168.9.177
- **Puerto**: 5432
- **Base de datos**: practica
- **Usuario**: postgres
- **Contraseña**: postgres

Para cambiar estos valores, modificar el constructor de `CupsQuery`:

```python
db = CupsQuery(
    host="tu_host",
    port=5432,
    database="tu_base",
    user="tu_usuario",
    password="tu_contraseña"
)
```

## Salida del Sistema

El sistema muestra:
1. Progreso de carga de archivos
2. Cantidad de registros encontrados
3. Progreso de inserción/actualización
4. Resumen final con estadísticas

Ejemplo de salida:
```
============================================================
CARGA DE CÓDIGOS CUPS A BASE DE DATOS
============================================================

PASO 1: Cargando datos desde archivos Excel...
------------------------------------------------------------
Cargando archivo de preparación: ...
  ✓ Cargados 50 registros de preparación
Cargando archivo de remitidos: ...
  ✓ Cargados 200 registros de remitidos
============================================================
Total de registros únicos: 220
  - Con preparación especial: 50
  - Para remitir: 200
============================================================

PASO 2: Conectando a la base de datos...
------------------------------------------------------------
✓ Conexión establecida

PASO 3: Procesando y cargando datos...
------------------------------------------------------------
Procesando 220 registros...
Códigos existentes en BD: 100
  Procesados 50/220 registros... (Insertados: 30, Actualizados: 20, Errores: 0)
  ...

============================================================
RESUMEN DEL PROCESO
============================================================
Total de registros procesados: 220
  ✓ Registros nuevos insertados: 120
  ↻ Registros existentes actualizados: 100
  ✗ Errores: 0
============================================================
```

## Solución de Problemas

### Error: "No se encontró el archivo"
- Verificar que los archivos Excel estén en la misma carpeta
- Verificar que los nombres de archivo sean exactos (incluyendo mayúsculas/minúsculas)

### Error: "No se encontraron las columnas esperadas"
- Verificar que los archivos Excel tengan el formato correcto
- El archivo de preparación debe tener `nombre_estudio` y `codigo_cups` en la primera fila
- El archivo de remitidos debe tener `CUPS` y `ESTUDIO` en la fila 6

### Error de conexión a base de datos
- Verificar que PostgreSQL esté ejecutándose
- Verificar credenciales de conexión
- Verificar que la tabla `codigos_cups` exista

### Error: "duplicate key value violates unique constraint"
- La tabla ya tiene una restricción UNIQUE en `codigo_cups` (correcto)
- El sistema debería manejar esto automáticamente con UPDATE

## Notas Importantes

- El campo `codigo_cups` es la clave única para identificar registros
- Si un código aparece en ambos archivos, se combinan las propiedades
- Los valores booleanos se actualizan con OR lógico (si uno es TRUE, queda TRUE)
- El sistema es idempotente: puedes ejecutarlo múltiples veces sin problemas
