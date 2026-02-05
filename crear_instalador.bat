@echo off
chcp 65001 >nul
echo ========================================
echo Creador de Instalador - Clinizad
echo Sistema de Migracion de Datos Emssanar
echo ========================================
echo.

REM Verificar que el ejecutable existe
if not exist "dist\Clinizad_Migracion_Datos.exe" (
    echo ERROR: No se encontro el ejecutable compilado.
    echo Por favor, ejecuta primero compilar.bat para crear el ejecutable.
    echo.
    pause
    exit /b 1
)

echo [1/3] Verificando Inno Setup...

REM Intentar ejecutar iscc directamente
iscc installer.iss >nul 2>&1
if not errorlevel 1 (
    echo Inno Setup encontrado en el PATH.
    echo.
    echo [2/3] Creando carpeta para el instalador...
    if not exist "dist_installer" mkdir dist_installer
    echo Carpeta creada.
    echo.
    echo [3/3] Compilando instalador...
    echo Esto puede tomar unos minutos...
    echo.
    iscc installer.iss
    goto :end
)

REM Si no está en PATH, intentar rutas comunes
echo Intentando ubicaciones comunes...
echo.

echo [2/3] Creando carpeta para el instalador...
if not exist "dist_installer" mkdir dist_installer
echo Carpeta creada.
echo.

echo [3/3] Compilando instalador...
echo Esto puede tomar unos minutos...
echo.

REM Intentar ejecutar desde ubicaciones comunes
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss 2>nul
if not errorlevel 1 goto :end

"C:\Program Files\Inno Setup 6\ISCC.exe" installer.iss 2>nul
if not errorlevel 1 goto :end

REM Si llegamos aquí, no se encontró Inno Setup
echo.
echo ERROR: Inno Setup no esta instalado o no esta en el PATH.
echo.
echo Por favor:
echo 1. Descarga Inno Setup desde: https://jrsoftware.org/isdl.php
echo 2. Instalalo en la ubicacion predeterminada
echo 3. O agrega la carpeta de Inno Setup al PATH del sistema
echo.
echo La carpeta tipica es: C:\Program Files (x86)\Inno Setup 6\
echo.
pause
exit /b 1

:end
if errorlevel 1 (
    echo.
    echo ERROR: La compilacion del instalador fallo.
    echo Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Instalador creado exitosamente!
echo ========================================
echo.
echo El instalador se encuentra en: dist_installer\Clinizad_Instalador.exe
echo.
echo Puedes distribuir este archivo para instalar la aplicacion.
echo.
pause
