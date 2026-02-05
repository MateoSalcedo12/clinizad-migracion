"""
Script para convertir logoMigracion.tiff a icono.ico
Requiere: pip install Pillow
"""
from PIL import Image
import os

def convertir_a_ico(ruta_origen, ruta_destino):
    """Convierte una imagen a formato .ico con múltiples tamaños."""
    print(f"Cargando imagen: {ruta_origen}")
    
    # Abrir la imagen
    img = Image.open(ruta_origen)
    
    # Convertir a RGBA si es necesario
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Tamaños estándar para iconos Windows
    tamaños = [16, 24, 32, 48, 64, 128, 256]
    
    # Crear versiones redimensionadas
    iconos = []
    for size in tamaños:
        # Redimensionar manteniendo aspecto y rellenando con transparente
        img_resized = img.copy()
        img_resized.thumbnail((size, size), Image.Resampling.LANCZOS)
        
        # Crear imagen cuadrada con fondo transparente
        img_cuadrada = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Centrar la imagen
        offset_x = (size - img_resized.width) // 2
        offset_y = (size - img_resized.height) // 2
        img_cuadrada.paste(img_resized, (offset_x, offset_y))
        
        iconos.append(img_cuadrada)
    
    # Guardar como .ico con múltiples tamaños
    iconos[0].save(
        ruta_destino,
        format='ICO',
        sizes=[(s, s) for s in tamaños],
        append_images=iconos[1:]
    )
    
    print(f"[OK] Icono creado: {ruta_destino}")
    print(f"  Tamaños incluidos: {tamaños}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    origen = os.path.join(script_dir, "logoMigracion.tiff")
    destino = os.path.join(script_dir, "icono.ico")
    
    if not os.path.exists(origen):
        print(f"ERROR: No se encontró {origen}")
        exit(1)
    
    try:
        convertir_a_ico(origen, destino)
        print("\n¡Conversión completada!")
        print("Ahora puedes recompilar la aplicación con: compilar.bat")
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
