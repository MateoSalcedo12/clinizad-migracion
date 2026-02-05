"""
Script para cargar códigos CUPS desde archivos Excel a la base de datos PostgreSQL.
Maneja dos archivos:
1. NOMBRES Y CUPS DE EXAMENES QUE REQUIEREN PREPARACION.xlsx
2. F-OS048 Exámenes para remitir a laboratorios de referencia.xlsx

El script inserta nuevos registros y actualiza los existentes basándose en codigo_cups.
"""

from read_cups_data import CupsDataReader
from cups_query import CupsQuery
import sys

def main():
    print("=" * 70)
    print("CARGA DE CÓDIGOS CUPS A BASE DE DATOS")
    print("=" * 70)
    print()
    
    try:
        # 1. Cargar datos desde los archivos Excel
        print("PASO 1: Cargando datos desde archivos Excel...")
        print("-" * 70)
        reader = CupsDataReader()
        df = reader.cargar_datos()
        
        if df is None or df.empty:
            print("\n[ERROR] No se pudieron cargar datos de los archivos Excel.")
            print("   Verifica que los archivos existan y tengan el formato correcto.")
            return
        
        print(f"\n[OK] Datos cargados exitosamente: {len(df)} registros unicos")
        print()
        
        # 2. Conectar a la base de datos
        print("PASO 2: Conectando a la base de datos...")
        print("-" * 70)
        db = CupsQuery()
        print("[OK] Conexion establecida")
        print()
        
        # 3. Procesar y cargar datos
        print("PASO 3: Procesando y cargando datos en la base de datos...")
        print("-" * 70)
        estadisticas = db.procesar_dataframe(df)
        
        # 4. Mostrar resultados
        print()
        print("=" * 70)
        print("RESUMEN DEL PROCESO")
        print("=" * 70)
        print(f"Total de registros procesados: {estadisticas['total']}")
        print(f"  [OK] Registros nuevos insertados: {estadisticas['insertados']}")
        print(f"  [ACTUALIZADOS] Registros existentes actualizados: {estadisticas['actualizados']}")
        print(f"  [ERRORES] Errores: {estadisticas['errores']}")
        print("=" * 70)
        
        # Cerrar conexión
        db.cerrar_conexion()
        print("\n[OK] Proceso completado exitosamente")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] No se encontro el archivo: {e}")
        print("\nAsegúrate de que los siguientes archivos estén en la misma carpeta:")
        print("  - NOMBRES Y CUPS DE EXAMENES QUE REQUIEREN PREPARACION.xlsx")
        print("  - F-OS048 Exámenes para remitir a laboratorios de referencia.xlsx")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
