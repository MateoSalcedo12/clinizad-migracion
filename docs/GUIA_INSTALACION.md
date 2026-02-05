# Guía de Instalación - Clinizad

## 📦 Opción 1: Instalación con Instalador (Recomendado)

### Requisitos Previos

- Windows 10 o superior
- Permisos de administrador (para instalar en Program Files)
- Espacio en disco: ~200 MB

### Pasos de Instalación

1. **Descargar el Instalador**
   - Ubica el archivo `Clinizad_Instalador.exe`
   - Haz clic derecho y selecciona "Ejecutar como administrador" (recomendado)

2. **Ejecutar el Instalador**
   - Haz doble clic en `Clinizad_Instalador.exe`
   - Si aparece una advertencia de Windows Defender, haz clic en "Más información" y luego "Ejecutar de todas formas"

3. **Asistente de Instalación**
   - **Bienvenida**: Haz clic en "Siguiente"
   - **Ruta de Instalación**: 
     - Por defecto: `C:\Program Files\Clinizad\`
     - Puedes cambiar la ruta si lo deseas
     - Haz clic en "Siguiente"
   - **Accesos Directos**:
     - Se creará un acceso directo en el escritorio
     - Se agregará al menú de inicio
     - Haz clic en "Siguiente"
   - **Confirmación**: Revisa la configuración y haz clic en "Instalar"
   - **Instalación**: Espera a que termine el proceso
   - **Finalización**: Haz clic en "Finalizar"

4. **Verificar Instalación**
   - Busca "Clinizad" en el menú de inicio
   - O haz doble clic en el acceso directo del escritorio
   - La aplicación debería abrirse correctamente

### Desinstalación

1. Ve a **Panel de Control** > **Programas y características**
2. Busca "Clinizad - Sistema de Migración de Datos"
3. Haz clic en "Desinstalar"
4. Sigue las instrucciones del desinstalador

---

## 💾 Opción 2: Versión Portátil (Sin Instalación)

### Requisitos

- Windows 10 o superior
- No requiere permisos de administrador
- Espacio en disco: ~200 MB

### Pasos

1. **Crear Carpeta**
   - Crea una carpeta donde quieras guardar la aplicación (ej: `C:\Clinizad\` o `D:\Aplicaciones\Clinizad\`)

2. **Copiar el Ejecutable**
   - Copia el archivo `Clinizad_Migracion_Datos.exe` a la carpeta creada

3. **Crear Acceso Directo (Opcional)**
   - Haz clic derecho en `Clinizad_Migracion_Datos.exe`
   - Selecciona "Crear acceso directo"
   - Arrastra el acceso directo al escritorio o al menú de inicio

4. **Ejecutar la Aplicación**
   - Haz doble clic en `Clinizad_Migracion_Datos.exe`
   - La aplicación se ejecutará directamente

### Ventajas de la Versión Portátil

- ✅ No requiere instalación
- ✅ Puede ejecutarse desde una memoria USB
- ✅ No deja rastros en el registro de Windows
- ✅ Fácil de eliminar (solo borrar la carpeta)

### Desinstalación

Simplemente elimina la carpeta donde copiaste el ejecutable.

---

## 🔧 Configuración Inicial Post-Instalación

Después de instalar o ejecutar la aplicación por primera vez:

1. **Configurar Base de Datos**
   - Abre la aplicación
   - Ve a la pestaña **⚙️ Configuración**
   - Ingresa los datos de conexión a PostgreSQL:
     - Host del servidor
     - Puerto (por defecto: 5432)
     - Nombre de la base de datos
     - Usuario
     - Contraseña
   - Haz clic en **"Probar Conexión"** para verificar

2. **Verificar Permisos**
   - Asegúrate de tener permisos de lectura y escritura en la base de datos
   - Verifica que el usuario tenga acceso a la tabla `solicitudes_servicios`

3. **Preparar Archivo Excel**
   - Asegúrate de tener un archivo Excel con las columnas requeridas
   - Consulta el `README_USUARIO.md` para ver la lista completa de columnas

---

## ⚠️ Solución de Problemas de Instalación

### Error: "Windows protegió tu PC"

**Causa**: Windows Defender SmartScreen bloquea ejecutables no firmados digitalmente.

**Solución**:
1. Haz clic en "Más información"
2. Haz clic en "Ejecutar de todas formas"
3. Si persiste, agrega una excepción en Windows Defender

### Error: "No se puede escribir en la carpeta de destino"

**Causa**: Falta de permisos de administrador o carpeta protegida.

**Solución**:
1. Ejecuta el instalador como administrador (clic derecho > "Ejecutar como administrador")
2. O elige una carpeta diferente donde tengas permisos de escritura

### Error: "El archivo está siendo usado por otro proceso"

**Causa**: La aplicación está ejecutándose o un antivirus la está escaneando.

**Solución**:
1. Cierra la aplicación si está abierta
2. Espera a que el antivirus termine de escanear
3. Intenta nuevamente

### El antivirus detecta el programa como amenaza

**Causa**: Falso positivo común con aplicaciones compiladas con PyInstaller.

**Solución**:
1. Agrega una excepción en tu antivirus para el ejecutable o la carpeta de instalación
2. Puedes verificar el archivo en VirusTotal si tienes dudas
3. Si el archivo proviene de una fuente confiable, es seguro agregar la excepción

---

## 📋 Verificación Post-Instalación

Después de instalar, verifica que todo funcione:

- [ ] La aplicación se abre correctamente
- [ ] No aparecen errores al iniciar
- [ ] Puedes acceder a todas las pestañas (Configuración, Autorizaciones, Consulta)
- [ ] El botón "Probar Conexión" funciona (aunque falle si no hay BD configurada)
- [ ] Puedes seleccionar un archivo Excel

---

## 🔄 Actualización

### Si instalaste con el Instalador:

1. Descarga la nueva versión del instalador
2. Ejecuta el nuevo instalador
3. Se detectará la instalación anterior y se actualizará automáticamente
4. Tu configuración se mantendrá

### Si usas la Versión Portátil:

1. Cierra la aplicación si está abierta
2. Reemplaza el archivo `Clinizad_Migracion_Datos.exe` con la nueva versión
3. Mantén la misma ubicación para conservar accesos directos

---

## 📞 Soporte

Si tienes problemas con la instalación:

1. Revisa esta guía completa
2. Verifica que cumplas con los requisitos del sistema
3. Consulta la sección de Solución de Problemas
4. Documenta el error con capturas de pantalla

---

**Última actualización**: Febrero 2026
