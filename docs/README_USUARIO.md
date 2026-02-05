# Clinizad - Sistema de Migración de Datos Emssanar

## 📋 Descripción

**Clinizad** es una aplicación de escritorio diseñada para migrar datos de solicitudes de servicios médicos desde archivos Excel hacia una base de datos PostgreSQL. La aplicación incluye una interfaz gráfica intuitiva que facilita el proceso de migración y consulta de datos.

## ✨ Características Principales

- ✅ **Migración Automática**: Transfiere datos desde Excel a PostgreSQL de forma segura
- ✅ **Detección de Duplicados**: Evita insertar registros que ya existen en la base de datos
- ✅ **Interfaz Intuitiva**: Diseño moderno y fácil de usar
- ✅ **Consulta de Afiliados**: Busca información por documento de afiliado
- ✅ **Estadísticas en Tiempo Real**: Visualiza el progreso y resultados de la migración
- ✅ **Log Detallado**: Registro completo de todas las operaciones realizadas

## 🚀 Instalación

### Opción 1: Instalador (Recomendado)

1. Ejecuta el archivo `Clinizad_Instalador.exe`
2. Sigue las instrucciones del asistente de instalación
3. La aplicación se instalará en `C:\Program Files\Clinizad\` (o la ruta que elijas)
4. Se creará un acceso directo en el escritorio y en el menú de inicio

### Opción 2: Ejecutable Portátil

1. Copia el archivo `Clinizad_Migracion_Datos.exe` a cualquier carpeta
2. Ejecuta el archivo haciendo doble clic
3. No requiere instalación, puedes ejecutarlo desde cualquier ubicación

## 📖 Guía de Uso

### Primera Vez - Configuración Inicial

1. **Abrir la aplicación**
   - Busca "Clinizad" en el menú de inicio o haz doble clic en el acceso directo

2. **Configurar Base de Datos**
   - Ve a la pestaña **⚙️ Configuración**
   - Ingresa los datos de conexión:
     - **Host**: Dirección del servidor PostgreSQL (ej: 192.168.9.177)
     - **Puerto**: Puerto de PostgreSQL (por defecto: 5432)
     - **Base de datos**: Nombre de la base de datos
     - **Usuario**: Usuario de PostgreSQL
     - **Contraseña**: Contraseña del usuario
   - Haz clic en **"Probar Conexión"** para verificar que los datos sean correctos

3. **Seleccionar Archivo Excel**
   - Haz clic en **"Examinar..."** para seleccionar tu archivo Excel
   - El sistema verificará automáticamente que el archivo sea válido
   - Verás un mensaje confirmando que el archivo fue cargado correctamente

### Migrar Datos

1. **Preparación**
   - Asegúrate de haber configurado correctamente la base de datos y el archivo Excel
   - Verifica que tengas permisos de escritura en la base de datos

2. **Iniciar Migración**
   - Ve a la pestaña **🔄 Autorizaciones**
   - Haz clic en **"Iniciar Migración"**
   - Confirma que deseas proceder con la migración

3. **Monitorear el Proceso**
   - **Estadísticas**: Se actualizan en tiempo real mostrando:
     - Total de registros en Excel
     - Registros ya existentes en BD (duplicados)
     - Registros nuevos a insertar
     - Registros insertados exitosamente
     - Errores encontrados
   
   - **Barra de Progreso**: Muestra el avance porcentual del proceso
   
   - **Log de Operaciones**: Muestra mensajes detallados con códigos de color:
     - 🟢 **Verde**: Operaciones exitosas
     - 🔵 **Azul**: Información general
     - 🟡 **Amarillo**: Advertencias
     - 🔴 **Rojo**: Errores

4. **Finalización**
   - Cuando termine, recibirás un mensaje de confirmación
   - Revisa las estadísticas finales
   - Consulta el log si necesitas detalles adicionales

### Consultar Afiliados

1. **Buscar por Documento**
   - Ve a la pestaña **🔍 Consulta**
   - Ingresa el número de documento del afiliado (ej: 1089196373)
   - Haz clic en **"Buscar"**

2. **Ver Resultados**
   - Los resultados se muestran en una tabla interactiva
   - Puedes hacer scroll horizontal y vertical para ver todas las columnas
   - En la parte inferior verás cuántos registros se encontraron

## ⚙️ Requisitos del Sistema

- **Sistema Operativo**: Windows 10 o superior
- **Base de Datos**: PostgreSQL accesible desde la red
- **Permisos**: Acceso de lectura/escritura a la base de datos
- **Archivo Excel**: Formato .xlsx o .xls con las columnas requeridas

## 📋 Columnas Requeridas en el Excel

El archivo Excel debe contener las siguientes columnas (no es sensible a mayúsculas/minúsculas):

- `doc_afiliado` - Documento del afiliado
- `codigo_servicio_completo` - Código completo del servicio
- `cod_diag` - Código de diagnóstico
- `desc_diag` - Descripción del diagnóstico
- `clasificacion_servicios_acceso` - Clasificación del servicio
- `descr_servicio_1` - Descripción del servicio
- `estado_solicitud` - Estado de la solicitud
- `num_autorizacion` - Número de autorización
- `fecha_autorizacion_1` - Fecha de autorización
- `ips_asignada` - IPS asignada
- `numero_solicitud` - Número de solicitud (usado para detectar duplicados)
- `ciudad_ips_asignada` - Ciudad de la IPS asignada
- `cantidad` - Cantidad
- `primer_nom`, `segundo_nom` - Nombres del paciente
- `primer_ape`, `segundo_ape` - Apellidos del paciente
- `edad_anios` - Edad en años
- `estado_solicitud_2` - Estado secundario
- `ips_solicita` - IPS solicitante

## 🔧 Solución de Problemas

### Error: "No se puede conectar a la base de datos"

**Posibles causas:**
- Host o puerto incorrectos
- Usuario o contraseña incorrectos
- PostgreSQL no está ejecutándose
- Firewall bloqueando la conexión
- Problemas de red

**Soluciones:**
1. Verifica los datos de conexión en la pestaña Configuración
2. Usa "Probar Conexión" para diagnosticar el problema
3. Verifica que PostgreSQL esté activo y accesible
4. Comprueba las reglas de firewall
5. Verifica la conectividad de red

### Error: "No se puede leer el archivo Excel"

**Posibles causas:**
- Archivo corrupto o dañado
- Formato incorrecto (debe ser .xlsx o .xls)
- Archivo abierto en otro programa
- Faltan columnas requeridas

**Soluciones:**
1. Cierra el archivo Excel si está abierto en otro programa
2. Abre el Excel manualmente para verificar que no esté corrupto
3. Asegúrate de que tiene todas las columnas requeridas
4. Verifica que el formato sea .xlsx o .xls

### La migración es muy lenta

**Causas comunes:**
- Archivo Excel muy grande (miles de registros)
- Conexión lenta a la base de datos
- Primera ejecución (sin caché)

**Soluciones:**
- Espera a que se genere el caché (la segunda ejecución será más rápida)
- Verifica la velocidad de la red
- Considera procesar archivos más pequeños si es posible

### El antivirus marca el programa como sospechoso

**Causa:** Falso positivo común con aplicaciones compiladas con PyInstaller

**Soluciones:**
1. Agrega una excepción en tu antivirus para el ejecutable
2. Si tienes dudas, verifica que el archivo provenga de una fuente confiable
3. Puedes escanear el archivo con VirusTotal para verificar

## 💡 Consejos de Uso

1. **Siempre prueba la conexión** antes de iniciar una migración grande
2. **Revisa las estadísticas** antes de confirmar la migración
3. **Consulta el log** si algo no funciona como esperabas
4. **Mantén un respaldo** de tu base de datos antes de migraciones grandes
5. **No cierres la aplicación** durante una migración en curso
6. **Usa el botón Cancelar** si necesitas detener el proceso de forma segura

## 📞 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la sección de Solución de Problemas arriba
2. Consulta el log de operaciones en la aplicación
3. Documenta el error con:
   - Mensaje de error completo
   - Pasos para reproducir el problema
   - Captura de pantalla del log
   - Versión de Windows

## 📝 Notas Importantes

- La aplicación **no inserta registros duplicados** automáticamente
- La verificación de duplicados se basa en el campo `numero_solicitud`
- El sistema crea archivos de caché (.pkl) para optimizar lecturas repetidas
- Los archivos de caché se actualizan automáticamente si el Excel cambia
- La configuración de base de datos no se guarda entre sesiones (por seguridad)

## 🔒 Seguridad

- Las contraseñas no se guardan en disco
- Las conexiones a la base de datos son seguras
- Se recomienda usar usuarios de base de datos con permisos limitados
- No compartas archivos de configuración con credenciales

---

**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Desarrollado para:** Sistema de Migración Emssanar
