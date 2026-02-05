@echo off
echo ========================================
echo Sistema de Migracion Emssanar
echo Iniciando interfaz grafica...
echo ========================================
echo.

REM Verificar que existen los archivos necesarios
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

REM Ejecutar la aplicación
python interfaz_emssanar.py

if errorlevel 1 (
    echo.
    echo ERROR: La aplicacion termino con errores
    pause
)
