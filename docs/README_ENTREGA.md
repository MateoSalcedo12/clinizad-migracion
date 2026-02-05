# 📦 Guía de Entrega Profesional - Clinizad

Esta guía explica cómo preparar y entregar la aplicación Clinizad de forma profesional.

## 📋 Contenido del Paquete de Entrega

### Archivos Principales

1. **Ejecutable de la Aplicación**
   - `dist\Clinizad_Migracion_Datos.exe` - Aplicación compilada lista para usar

2. **Instalador (Opcional pero Recomendado)**
   - `dist_installer\Clinizad_Instalador.exe` - Instalador profesional con Inno Setup

3. **Documentación**
   - `README_USUARIO.md` - Manual de usuario completo
   - `GUIA_INSTALACION.md` - Guía paso a paso de instalación
   - `INSTRUCCIONES_ICONO.md` - Cómo agregar un icono personalizado

### Archivos de Desarrollo (No Incluir en Entrega)

- `interfaz_emssanar.py` - Código fuente
- `Query.py` - Código fuente
- `read_data.py` - Código fuente
- `compilar.bat` - Script de compilación
- `installer.iss` - Script del instalador
- Carpetas `build\` y `__pycache__\`

---

## 🚀 Proceso de Preparación

### Paso 1: Compilar la Aplicación

1. Abre una terminal en la carpeta del proyecto
2. Ejecuta: `compilar.bat`
3. Espera a que termine la compilación (puede tardar varios minutos)
4. Verifica que exista `dist\Clinizad_Migracion_Datos.exe`

### Paso 2: Crear el Instalador (Opcional)

1. **Instalar Inno Setup**:
   - Descarga desde: https://jrsoftware.org/isdl.php
   - Instala en la ubicación predeterminada

2. **Compilar el Instalador**:
   - Ejecuta: `crear_instalador.bat`
   - O abre `installer.iss` en Inno Setup Compiler y compila manualmente

3. Verifica que exista `dist_installer\Clinizad_Instalador.exe`

### Paso 3: Agregar Icono Personalizado (Opcional)

1. Crea o consigue un archivo `.ico` (ver `INSTRUCCIONES_ICONO.md`)
2. Colócalo en la carpeta del proyecto como `icono.ico`
3. Actualiza `interfaz_emssanar.spec` línea 61: `icon='icono.ico',`
4. Recompila con `compilar.bat`

### Paso 4: Preparar el Paquete de Entrega

Crea una carpeta con el siguiente contenido:

```
Clinizad_Entrega_v1.0/
│
├── Instalador/
│   └── Clinizad_Instalador.exe
│
├── Version_Portatil/
│   └── Clinizad_Migracion_Datos.exe
│
└── Documentacion/
    ├── README_USUARIO.md
    ├── GUIA_INSTALACION.md
    └── INSTRUCCIONES_ICONO.md (opcional)
```

---

## 📤 Opciones de Entrega

### Opción A: Instalador (Recomendado para Usuarios Finales)

**Ventajas:**
- ✅ Instalación profesional con asistente
- ✅ Accesos directos automáticos
- ✅ Desinstalación fácil desde Panel de Control
- ✅ Se instala en ubicación estándar

**Incluir:**
- `Clinizad_Instalador.exe`
- `README_USUARIO.md`
- `GUIA_INSTALACION.md`

**Instrucciones para el usuario:**
1. Ejecutar `Clinizad_Instalador.exe`
2. Seguir el asistente de instalación
3. Consultar `GUIA_INSTALACION.md` si hay problemas

### Opción B: Versión Portátil (Para Usuarios Avanzados)

**Ventajas:**
- ✅ No requiere instalación
- ✅ Puede ejecutarse desde USB
- ✅ No deja rastros en el sistema

**Incluir:**
- `Clinizad_Migracion_Datos.exe`
- `README_USUARIO.md`

**Instrucciones para el usuario:**
1. Copiar el ejecutable a cualquier carpeta
2. Ejecutar haciendo doble clic
3. Consultar `README_USUARIO.md` para uso

### Opción C: Paquete Completo (Recomendado)

**Incluir ambos** (Instalador + Portátil) más toda la documentación.

---

## ✅ Checklist de Entrega

Antes de entregar, verifica:

### Ejecutable
- [ ] El ejecutable se ejecuta sin errores
- [ ] La interfaz se muestra correctamente
- [ ] Todas las pestañas funcionan
- [ ] El icono personalizado aparece (si se agregó)

### Instalador (si aplica)
- [ ] El instalador se ejecuta correctamente
- [ ] La instalación completa sin errores
- [ ] Se crean los accesos directos
- [ ] La aplicación se ejecuta después de instalar
- [ ] La desinstalación funciona

### Documentación
- [ ] `README_USUARIO.md` está completo y actualizado
- [ ] `GUIA_INSTALACION.md` tiene instrucciones claras
- [ ] Los archivos están en formato legible (Markdown o PDF)

### Pruebas
- [ ] Probar en un equipo limpio (sin Python instalado)
- [ ] Verificar conexión a base de datos
- [ ] Probar migración con datos de prueba
- [ ] Probar consulta de afiliados
- [ ] Verificar que no aparezcan errores en el log

---

## 🔒 Consideraciones de Seguridad

### Antivirus

Los ejecutables compilados con PyInstaller a veces son marcados como falsos positivos por antivirus. Para minimizar esto:

1. **Firma Digital** (Recomendado para producción):
   - Obtén un certificado de firma de código
   - Firma el ejecutable antes de distribuir
   - Reduce significativamente las alertas de antivirus

2. **Verificación en VirusTotal**:
   - Sube el ejecutable a https://www.virustotal.com
   - Verifica que no haya detecciones maliciosas reales
   - Si solo hay 1-2 detecciones, probablemente son falsos positivos

3. **Comunicación al Usuario**:
   - Informa que pueden aparecer advertencias del antivirus
   - Indica que es seguro agregar una excepción
   - Proporciona instrucciones en la documentación

---

## 📊 Tamaños Esperados

- **Ejecutable**: ~150-250 MB (incluye todas las dependencias)
- **Instalador**: ~150-250 MB (comprimido)
- **Documentación**: < 1 MB

---

## 🎯 Recomendaciones Finales

1. **Versionado**: Incluye el número de versión en el nombre del paquete
   - Ejemplo: `Clinizad_Entrega_v1.0.zip`

2. **Comprimir**: Comprime todo en un archivo ZIP o RAR para facilitar la entrega

3. **Notas de Versión**: Crea un archivo `CHANGELOG.txt` o `NOTAS_VERSION.txt` con:
   - Versión actual
   - Fecha de lanzamiento
   - Cambios principales
   - Problemas conocidos (si los hay)

4. **Soporte**: Incluye información de contacto o canal de soporte

5. **Licencia**: Si aplica, incluye un archivo de licencia

---

## 📝 Ejemplo de Estructura Final

```
Clinizad_v1.0_Entrega.zip
│
├── Clinizad_Instalador.exe
├── Clinizad_Migracion_Datos.exe (versión portátil)
│
├── Documentacion/
│   ├── README_USUARIO.pdf (o .md)
│   ├── GUIA_INSTALACION.pdf (o .md)
│   └── NOTAS_VERSION.txt
│
└── LEEME_PRIMERO.txt
```

Contenido de `LEEME_PRIMERO.txt`:
```
CLINIZAD - Sistema de Migración de Datos Emssanar
Versión 1.0

INSTRUCCIONES RÁPIDAS:
1. Para instalación: Ejecutar Clinizad_Instalador.exe
2. Para uso portátil: Ejecutar Clinizad_Migracion_Datos.exe directamente
3. Consultar Documentacion/README_USUARIO.pdf para más información

SOPORTE:
[Información de contacto]
```

---

## 🎉 ¡Listo para Entregar!

Con estos pasos, tendrás un paquete profesional y completo listo para distribuir.

**Última actualización**: Febrero 2026
