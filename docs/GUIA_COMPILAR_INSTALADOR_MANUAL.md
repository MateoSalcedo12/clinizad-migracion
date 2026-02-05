# 🔧 Guía: Compilar el Instalador Manualmente

Esta guía te explica cómo compilar el instalador usando Inno Setup Compiler de forma manual.

## 📋 Requisitos Previos

1. **Inno Setup instalado**
   - Descarga desde: https://jrsoftware.org/isdl.php
   - Instala la versión más reciente (6.x recomendada)
   - Durante la instalación, asegúrate de marcar "Add Inno Setup Preprocessor to PATH" (opcional pero útil)

2. **Ejecutable compilado**
   - Debes haber ejecutado `compilar.bat` primero
   - Verifica que exista: `dist\Clinizad_Migracion_Datos.exe`

---

## 🚀 Pasos para Compilar Manualmente

### Paso 1: Abrir Inno Setup Compiler

1. **Busca "Inno Setup Compiler"** en el menú de inicio de Windows
2. O navega a la carpeta de instalación (típicamente):
   - `C:\Program Files (x86)\Inno Setup 6\`
   - Y ejecuta `Compil32.exe`

### Paso 2: Abrir el Archivo installer.iss

1. En Inno Setup Compiler, ve a **File > Open**
2. Navega a la carpeta de tu proyecto
3. Selecciona el archivo **`installer.iss`**
4. Haz clic en **Abrir**

### Paso 3: Revisar la Configuración (Opcional)

Antes de compilar, puedes revisar y ajustar:

- **AppName**: Nombre de la aplicación
- **AppVersion**: Versión actual
- **DefaultDirName**: Carpeta de instalación por defecto
- **OutputDir**: Carpeta donde se guardará el instalador (debe ser `dist_installer`)
- **OutputBaseFilename**: Nombre del archivo instalador

### Paso 4: Compilar el Instalador

Tienes **3 formas** de compilar:

#### Opción A: Menú (Recomendado)
1. Ve a **Build > Compile** (o presiona **F9**)
2. Espera a que termine la compilación
3. Verás el progreso en la ventana inferior

#### Opción B: Botón de la Barra de Herramientas
1. Haz clic en el botón **▶ Compile** (icono de play)
2. Espera a que termine

#### Opción C: Atajo de Teclado
1. Presiona **F9**
2. Espera a que termine

### Paso 5: Verificar el Resultado

1. **Revisa la ventana de compilación** en la parte inferior:
   - Si dice "Successfully compiled" → ✅ Todo bien
   - Si hay errores → Revisa los mensajes de error

2. **Verifica el archivo generado**:
   - Debe estar en: `dist_installer\Clinizad_Instalador.exe`
   - El tamaño será similar al ejecutable (~150-250 MB)

---

## ⚠️ Solución de Problemas

### Error: "Cannot find file dist\Clinizad_Migracion_Datos.exe"

**Causa**: El ejecutable no está compilado o está en otra ubicación.

**Solución**:
1. Ejecuta primero `compilar.bat` para crear el ejecutable
2. Verifica que exista `dist\Clinizad_Migracion_Datos.exe`
3. Si está en otra ubicación, actualiza la línea en `installer.iss`:
   ```
   Source: "dist\Clinizad_Migracion_Datos.exe"; DestDir: "{app}"; Flags: ignoreversion
   ```
   Cambia `dist\` por la ruta correcta.

### Error: "Output directory does not exist"

**Causa**: La carpeta `dist_installer` no existe.

**Solución**:
1. Crea la carpeta `dist_installer` manualmente en la carpeta del proyecto
2. O cambia `OutputDir=dist_installer` en `installer.iss` por una ruta que exista

### Error: "Cannot find file README_USUARIO.md"

**Causa**: Los archivos de documentación no están en la carpeta del proyecto.

**Solución**:
1. Verifica que existan `README_USUARIO.md` y `GUIA_INSTALACION.md`
2. O comenta/elimina esas líneas en `installer.iss` si no quieres incluirlas:
   ```
   ; Source: "README_USUARIO.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
   ; Source: "GUIA_INSTALACION.md"; DestDir: "{app}"; Flags: ignoreversion
   ```

### El instalador se compila pero es muy pequeño (< 1 MB)

**Causa**: No está incluyendo el ejecutable correctamente.

**Solución**:
1. Verifica que la ruta en `installer.iss` sea correcta
2. Asegúrate de que `dist\Clinizad_Migracion_Datos.exe` existe
3. Revisa que no haya errores en la ventana de compilación

---

## 📝 Verificación Post-Compilación

Después de compilar, verifica:

- [ ] El archivo `dist_installer\Clinizad_Instalador.exe` existe
- [ ] El tamaño es razonable (~150-250 MB)
- [ ] Puedes ejecutar el instalador (haz doble clic)
- [ ] El instalador muestra la interfaz correcta
- [ ] La instalación funciona correctamente

---

## 🎯 Compilación Rápida (Resumen)

1. Abre **Inno Setup Compiler**
2. **File > Open** → Selecciona `installer.iss`
3. Presiona **F9** (o Build > Compile)
4. Espera a que termine
5. Encuentra el instalador en `dist_installer\Clinizad_Instalador.exe`

---

## 💡 Consejos Adicionales

### Previsualizar el Instalador

Antes de compilar, puedes previsualizar cómo se verá:
- Ve a **Build > Test** (o presiona **F5**)
- Se ejecutará el instalador en modo de prueba

### Compilar en Modo Silencioso

Si quieres compilar sin la interfaz gráfica:
1. Abre una terminal en la carpeta del proyecto
2. Ejecuta:
   ```
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

### Ver Logs Detallados

Para ver más información durante la compilación:
- Ve a **View > Compiler Output** en Inno Setup Compiler
- Verás todos los detalles del proceso

---

## 📞 ¿Necesitas Ayuda?

Si encuentras problemas:
1. Revisa la ventana de compilación para mensajes de error específicos
2. Verifica que todos los archivos fuente existan
3. Asegúrate de que Inno Setup esté correctamente instalado
4. Consulta la documentación oficial: https://jrsoftware.org/ishelp/

---

**Última actualización**: Febrero 2026
