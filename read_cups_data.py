import pandas as pd
import os
from typing import Optional, Tuple

class CupsDataReader:
    """
    Clase encargada de leer y procesar archivos Excel relacionados con códigos CUPS.
    Maneja dos tipos de archivos:
    1. Exámenes que requieren preparación especial
    2. Exámenes para remitir a laboratorios de referencia
    """

    def __init__(self, ruta_preparacion: str = None, ruta_remitidos: str = None):
        """
        Inicializa el lector de datos CUPS.
        
        Args:
            ruta_preparacion: Ruta al archivo "NOMBRES Y CUPS DE EXAMENES QUE REQUIEREN PREPARACION.xlsx"
            ruta_remitidos: Ruta al archivo "F-OS048 Exámenes para remitir a laboratorios de referencia.xlsx"
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if ruta_preparacion is None:
            ruta_preparacion = os.path.join(script_dir, "NOMBRES Y CUPS DE EXAMENES QUE REQUIEREN PREPARACION.xlsx")
        if ruta_remitidos is None:
            ruta_remitidos = os.path.join(script_dir, "F-OS048 Exámenes para remitir a laboratorios de referencia.xlsx")
        
        self.ruta_preparacion = ruta_preparacion
        self.ruta_remitidos = ruta_remitidos
        self._df_preparacion: Optional[pd.DataFrame] = None
        self._df_remitidos: Optional[pd.DataFrame] = None
        self._df_combinado: Optional[pd.DataFrame] = None

    def _cargar_preparacion(self) -> pd.DataFrame:
        """
        Carga el archivo de exámenes que requieren preparación especial.
        """
        if not os.path.exists(self.ruta_preparacion):
            print(f"Advertencia: No se encontró el archivo de preparación: {self.ruta_preparacion}")
            return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'preparacion_especial'])
        
        print(f"Cargando archivo de preparación: {self.ruta_preparacion}")
        
        try:
            # Leer el Excel sin encabezados
            df = pd.read_excel(self.ruta_preparacion, sheet_name=0, header=None)
            
            # Buscar la fila que contiene los encabezados (nombre_estudio, codigo_cups)
            fila_encabezados = None
            for idx in range(min(5, len(df))):  # Buscar en las primeras 5 filas
                fila = df.iloc[idx]
                valores_fila = [str(val).lower().strip() for val in fila.values if pd.notna(val)]
                if 'nombre' in ' '.join(valores_fila) and ('codigo' in ' '.join(valores_fila) or 'cups' in ' '.join(valores_fila)):
                    fila_encabezados = idx
                    break
            
            if fila_encabezados is None:
                # Si no encontramos encabezados, asumir que están en la fila 1
                fila_encabezados = 1
            
            # El archivo tiene encabezados en la fila encontrada
            # Las columnas son: nombre_estudio, codigo_cups
            if len(df.columns) >= 2 and len(df) > fila_encabezados:
                # Obtener los nombres de las columnas de la fila de encabezados
                fila_enc = df.iloc[fila_encabezados]
                nombres_columnas = [str(col).strip().lower() if pd.notna(col) else f'col_{i}' 
                                   for i, col in enumerate(fila_enc.values)]
                
                # Asignar nombres de columnas
                df.columns = nombres_columnas
                
                # Eliminar las filas hasta la fila de encabezados (incluyendo la fila de encabezados)
                df = df.iloc[fila_encabezados + 1:].reset_index(drop=True)
                
                # Normalizar nombres de columnas
                columnas_map = {}
                for col in df.columns:
                    col_lower = str(col).lower()
                    if 'codigo' in col_lower or 'cups' in col_lower:
                        columnas_map[col] = 'codigo_cups'
                    elif 'nombre' in col_lower or 'estudio' in col_lower:
                        columnas_map[col] = 'nombre_estudio'
                
                df.rename(columns=columnas_map, inplace=True)
                
                # Asegurar que tenemos las columnas necesarias
                if 'codigo_cups' in df.columns and 'nombre_estudio' in df.columns:
                    # Limpiar datos
                    df = df[['codigo_cups', 'nombre_estudio']].copy()
                    df['codigo_cups'] = df['codigo_cups'].astype(str).str.strip()
                    df['nombre_estudio'] = df['nombre_estudio'].astype(str).str.strip()
                    df['preparacion_especial'] = True  # Todos requieren preparación
                    
                    # Eliminar filas vacías
                    df = df[df['codigo_cups'].notna() & (df['codigo_cups'] != '')].copy()
                    df = df[df['nombre_estudio'].notna() & (df['nombre_estudio'] != '')].copy()
                    
                    print(f"  [OK] Cargados {len(df)} registros de preparacion")
                    return df
                else:
                    print(f"  [ERROR] No se encontraron las columnas esperadas. Columnas: {list(df.columns)}")
                    return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'preparacion_especial'])
            else:
                print(f"  [ERROR] El archivo no tiene suficientes columnas")
                return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'preparacion_especial'])
                
        except Exception as e:
            print(f"  [ERROR] Error al leer archivo de preparacion: {e}")
            return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'preparacion_especial'])

    def _cargar_remitidos(self) -> pd.DataFrame:
        """
        Carga el archivo de exámenes para remitir a laboratorios de referencia.
        """
        if not os.path.exists(self.ruta_remitidos):
            print(f"Advertencia: No se encontró el archivo de remitidos: {self.ruta_remitidos}")
            return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'remitido'])
        
        print(f"Cargando archivo de remitidos: {self.ruta_remitidos}")
        
        try:
            # Leer el Excel
            xls = pd.ExcelFile(self.ruta_remitidos)
            
            # Buscar la hoja correcta (puede ser "ACTUALIZACION" o similar)
            hoja_correcta = None
            for nombre_hoja in xls.sheet_names:
                df_temp = pd.read_excel(xls, sheet_name=nombre_hoja, nrows=10)
                # Buscar la fila que contiene "CUPS" en alguna columna
                for idx, row in df_temp.iterrows():
                    row_str = ' '.join([str(val) for val in row.values if pd.notna(val)]).upper()
                    if 'CUPS' in row_str and 'ESTUDIO' in row_str:
                        hoja_correcta = nombre_hoja
                        fila_encabezados = idx
                        break
                if hoja_correcta:
                    break
            
            if hoja_correcta is None:
                # Intentar con la primera hoja
                hoja_correcta = xls.sheet_names[0]
                fila_encabezados = 6  # Basado en la estructura observada
            
            print(f"  Usando hoja: {hoja_correcta}, fila de encabezados: {fila_encabezados}")
            
            # Leer desde la fila de encabezados
            df = pd.read_excel(xls, sheet_name=hoja_correcta, header=fila_encabezados)
            
            # Buscar columnas relevantes (CUPS y ESTUDIO)
            columnas_map = {}
            for col in df.columns:
                col_str = str(col).upper().strip()
                # Buscar columna CUPS
                if 'CUPS' in col_str:
                    columnas_map[col] = 'codigo_cups'
                # Buscar columna ESTUDIO (pero no PROCESO PRE-ANALITICO)
                elif 'ESTUDIO' in col_str and 'PRE' not in col_str and 'ANALITICO' not in col_str:
                    columnas_map[col] = 'nombre_estudio'
            
            # Si no encontramos las columnas, intentar buscar en los valores de la primera fila
            if not columnas_map and len(df) > 0:
                primera_fila = df.iloc[0]
                for idx, val in enumerate(primera_fila):
                    val_str = str(val).upper().strip() if pd.notna(val) else ''
                    col_name = df.columns[idx]
                    if 'CUPS' in val_str:
                        columnas_map[col_name] = 'codigo_cups'
                    elif 'ESTUDIO' in val_str and 'PRE' not in val_str:
                        columnas_map[col_name] = 'nombre_estudio'
            
            if columnas_map:
                df.rename(columns=columnas_map, inplace=True)
                
                # Asegurar que tenemos las columnas necesarias
                if 'codigo_cups' in df.columns and 'nombre_estudio' in df.columns:
                    df = df[['codigo_cups', 'nombre_estudio']].copy()
                    df['codigo_cups'] = df['codigo_cups'].astype(str).str.strip()
                    df['nombre_estudio'] = df['nombre_estudio'].astype(str).str.strip()
                    df['remitido'] = True  # Todos son remitidos
                    
                    # Eliminar filas vacías o con valores NaN
                    df = df[df['codigo_cups'].notna() & (df['codigo_cups'] != '') & (df['codigo_cups'] != 'nan')].copy()
                    df = df[df['nombre_estudio'].notna() & (df['nombre_estudio'] != '') & (df['nombre_estudio'] != 'nan')].copy()
                    
                    # Eliminar filas donde codigo_cups no sea numérico (filas de encabezado)
                    df = df[df['codigo_cups'].str.isdigit()].copy()
                    
                    print(f"  [OK] Cargados {len(df)} registros de remitidos")
                    return df
                else:
                    print(f"  [ERROR] No se encontraron las columnas esperadas. Columnas: {list(df.columns)}")
                    return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'remitido'])
            else:
                print(f"  [ERROR] No se pudieron mapear las columnas CUPS y ESTUDIO")
                return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'remitido'])
                
        except Exception as e:
            print(f"  [ERROR] Error al leer archivo de remitidos: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'remitido'])

    def cargar_datos(self) -> pd.DataFrame:
        """
        Carga ambos archivos y los combina en un solo DataFrame.
        Retorna un DataFrame con: codigo_cups, nombre_estudio, preparacion_especial, remitido
        """
        print("=" * 60)
        print("Cargando datos de códigos CUPS...")
        print("=" * 60)
        
        # Cargar ambos archivos
        df_prep = self._cargar_preparacion()
        df_rem = self._cargar_remitidos()
        
        # Combinar los DataFrames
        # Primero, crear DataFrames completos con todas las columnas
        if not df_prep.empty:
            df_prep['remitido'] = False  # Por defecto False, se actualizará si está en remitidos
        else:
            df_prep = pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'preparacion_especial', 'remitido'])
        
        if not df_rem.empty:
            df_rem['preparacion_especial'] = False  # Por defecto False, se actualizará si está en preparación
        else:
            df_rem = pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'preparacion_especial', 'remitido'])
        
        # Combinar usando codigo_cups como clave
        if not df_prep.empty and not df_rem.empty:
            # Hacer merge para combinar información
            df_combinado = pd.merge(
                df_prep,
                df_rem,
                on='codigo_cups',
                how='outer',
                suffixes=('_prep', '_rem')
            )
            
            # Consolidar columnas
            df_combinado['nombre_estudio'] = df_combinado['nombre_estudio_prep'].fillna(df_combinado['nombre_estudio_rem'])
            
            # Preparación especial: TRUE si está en prep, FALSE si no
            prep_prep = df_combinado['preparacion_especial_prep'].fillna(False).astype(bool)
            prep_rem = df_combinado.get('preparacion_especial_rem', pd.Series([False] * len(df_combinado))).fillna(False).astype(bool)
            df_combinado['preparacion_especial'] = prep_prep | prep_rem
            
            # Remitido: TRUE si está en rem, FALSE si no
            rem_prep = df_combinado.get('remitido_prep', pd.Series([False] * len(df_combinado))).fillna(False).astype(bool)
            rem_rem = df_combinado['remitido_rem'].fillna(False).astype(bool)
            df_combinado['remitido'] = rem_prep | rem_rem
            
            # Seleccionar solo las columnas finales
            df_combinado = df_combinado[['codigo_cups', 'nombre_estudio', 'preparacion_especial', 'remitido']].copy()
            
        elif not df_prep.empty:
            df_combinado = df_prep.copy()
            df_combinado['remitido'] = False
        elif not df_rem.empty:
            df_combinado = df_rem.copy()
            df_combinado['preparacion_especial'] = False
        else:
            df_combinado = pd.DataFrame(columns=['codigo_cups', 'nombre_estudio', 'preparacion_especial', 'remitido'])
        
        # Eliminar duplicados basados en codigo_cups (mantener el primero)
        df_combinado = df_combinado.drop_duplicates(subset=['codigo_cups'], keep='first')
        
        # Convertir booleanos a Python bool (no numpy bool)
        df_combinado['preparacion_especial'] = df_combinado['preparacion_especial'].astype(bool)
        df_combinado['remitido'] = df_combinado['remitido'].astype(bool)
        
        self._df_combinado = df_combinado
        
        print("=" * 60)
        print(f"Total de registros únicos: {len(df_combinado)}")
        print(f"  - Con preparación especial: {df_combinado['preparacion_especial'].sum()}")
        print(f"  - Para remitir: {df_combinado['remitido'].sum()}")
        print("=" * 60)
        
        return df_combinado

    @property
    def df(self) -> pd.DataFrame:
        """Retorna el DataFrame combinado, cargándolo si es necesario."""
        if self._df_combinado is None:
            self.cargar_datos()
        return self._df_combinado
