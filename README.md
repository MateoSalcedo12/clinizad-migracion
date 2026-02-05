# Clinizad - Sistema de Migración de Datos Emssanar

Aplicación de escritorio para migrar datos de solicitudes de servicios médicos desde archivos Excel hacia PostgreSQL.

## 🚀 Inicio Rápido

### Para Usuarios
1. **Instalar**: Ejecuta `dist_installer\Clinizad_Instalador.exe`
2. **Usar**: Consulta `docs\README_USUARIO.md`

### Para Desarrolladores
1. **Instalar dependencias**: `instalar_dependencias.bat`
2. **Ejecutar**: `ejecutar.bat`
3. **Compilar**: `compilar.bat`
4. **Crear instalador**: `crear_instalador.bat`

## 📁 Estructura del Proyecto

```
LECTURA_MATRIZ/
├── 📝 Código Fuente
│   ├── interfaz_emssanar.py    # Interfaz principal
│   ├── Query.py                 # Gestión PostgreSQL
│   ├── read_data.py             # Lectura Excel Emssanar
│   ├── read_cups_data.py        # Lectura datos CUPS
│   ├── cups_query.py            # Consultas CUPS
│   └── load_cups_data.py        # Carga datos CUPS
│
├── 📚 docs/                      # Documentación
│   ├── README_USUARIO.md        # Manual de usuario
│   ├── GUIA_INSTALACION.md      # Guía de instalación
│   └── ...
│
├── 📊 data/                       # Archivos de datos
│   ├── datos_emssanar.xlsx
│   └── ...
│
├── ⚙️ Configuración
│   ├── interfaz_emssanar.spec   # PyInstaller
│   ├── installer.iss             # Inno Setup
│   └── requirements.txt         # Dependencias
│
└── 📦 Resultados
    ├── dist/                     # Ejecutable compilado
    └── dist_installer/           # Instalador compilado
```

## 📖 Documentación Completa

Consulta la carpeta `docs/` para:
- Manual de usuario
- Guía de instalación
- Instrucciones de compilación
- Guía de entrega

## 🔧 Requisitos

- Python 3.11+
- PostgreSQL
- Windows 10+

## 📝 Licencia

Uso interno para Emssanar.
