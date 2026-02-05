@echo off
chcp 65001 >nul
echo ========================================
echo Compilador PyInstaller - Clinizad
echo Sistema de Migracion de Datos Emssanar
echo ========================================
echo.

REM Verificar que Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Verificando instalacion de PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no esta instalado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
    echo PyInstaller instalado correctamente.
) else (
    echo PyInstaller ya esta instalado.
)

echo.
echo [2/4] Verificando archivos necesarios...
if not exist "interfaz_emssanar.py" (
    echo ERROR: No se encontro interfaz_emssanar.py
    pause
    exit /b 1
)

if not exist "Query.py" (
    echo ERROR: No se encontro Query.py
    pause
    exit /b 1
)

if not exist "read_data.py" (
    echo ERROR: No se encontro read_data.py
    pause
    exit /b 1
)

echo Todos los archivos necesarios estan presentes.
echo.

echo [3/4] Limpiando compilaciones anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__
echo Limpieza completada.
echo.

echo [4/4] Compilando aplicacion con PyInstaller...
echo Esto puede tomar varios minutos...
echo.

REM Compilar usando el archivo .spec
python -m PyInstaller interfaz_emssanar.spec

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion fallo. Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Compilacion completada exitosamente!
echo ========================================
echo.
echo El ejecutable se encuentra en: dist\Clinizad_Migracion_Datos.exe
echo.
echo Puedes copiar el ejecutable a cualquier ubicacion y ejecutarlo directamente.
echo NOTA: Asegurate de tener los permisos necesarios para conectarte a la base de datos.
echo.
pause
