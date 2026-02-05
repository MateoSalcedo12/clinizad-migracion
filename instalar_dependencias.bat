@echo off
echo ========================================
echo Instalador de Dependencias
echo Sistema de Migracion Emssanar
echo ========================================
echo.

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)
echo.

echo Instalando dependencias...
echo.

echo [1/3] Instalando pandas...
pip install pandas
if errorlevel 1 (
    echo ERROR: No se pudo instalar pandas
    pause
    exit /b 1
)
echo.

echo [2/3] Instalando psycopg2-binary...
pip install psycopg2-binary
if errorlevel 1 (
    echo ERROR: No se pudo instalar psycopg2-binary
    pause
    exit /b 1
)
echo.

echo [3/3] Instalando openpyxl...
pip install openpyxl
if errorlevel 1 (
    echo ERROR: No se pudo instalar openpyxl
    pause
    exit /b 1
)
echo.

echo ========================================
echo Instalacion completada exitosamente!
echo ========================================
echo.
echo Ahora puedes ejecutar la aplicacion con:
echo    python interfaz_emssanar.py
echo.
pause
