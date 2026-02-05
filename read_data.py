import pandas as pd
import os
from typing import Optional, Union


class EmssanarDataReader:
    """
    Clase encargada de leer y filtrar información del archivo de datos Emssanar.
    Optimizada con caché binaria y carga eficiente.
    """

    COLUMNAS_REQUERIDAS = (
        "doc_afiliado", "codigo_servicio_completo", "cod_diag", "desc_diag",
        "clasificacion_servicios_acceso", "descr_servicio_1", "estado_solicitud",
        "num_autorizacion", "fecha_autorizacion_1", "ips_asignada", "numero_solicitud",
        "ciudad_ips_asignada", "cantidad", "primer_nom", "segundo_nom",
        "primer_ape", "segundo_ape", "edad_anios", "estado_solicitud_2", "ips_solicita"
    )
    
    # Columnas que deben leerse como texto
    _COLS_TEXTO = frozenset({"doc_afiliado", "num_autorizacion", "numero_solicitud", "codigo_servicio_completo"})

    def __init__(self, ruta_archivo: str = None):
        if ruta_archivo is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_archivo = os.path.join(script_dir, "datos_emssanar.xlsx")
            
        self.ruta_archivo = ruta_archivo
        self._df: Optional[pd.DataFrame] = None
        self._ruta_cache = f"{ruta_archivo}.pkl"

    def _cargar_datos(self) -> None:
        """Carga el archivo Excel en memoria solo con las columnas necesarias."""
        if not os.path.exists(self.ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo: {self.ruta_archivo}")
        
        # Verificar caché
        if self._cargar_desde_cache():
            return

        print("Leyendo archivo Excel, por favor espere...")
        self._cargar_desde_excel()

    def _cargar_desde_cache(self) -> bool:
        """Intenta cargar desde caché pickle si es válida."""
        if (os.path.exists(self._ruta_cache) and 
            os.path.getmtime(self._ruta_cache) > os.path.getmtime(self.ruta_archivo)):
            try:
                print("Cargando datos desde caché optimizada...")
                self._df = pd.read_pickle(self._ruta_cache)
                return True
            except Exception:
                print("Caché inválida, leyendo Excel original...")
        return False

    def _cargar_desde_excel(self) -> None:
        """Carga datos desde el archivo Excel original."""
        try:
            with pd.ExcelFile(self.ruta_archivo, engine='openpyxl') as xls:
                hoja, cols_finales, mapa_cols = self._encontrar_hoja_correcta(xls)
                
                if hoja is None:
                    raise ValueError("No se encontraron las columnas requeridas en ninguna hoja.")
                
                print(f"Datos encontrados en la hoja: '{hoja}'")
                
                # Determinar tipos de datos
                dtypes = {mapa_cols.get(c.lower()): str 
                          for c in self._COLS_TEXTO 
                          if mapa_cols.get(c.lower()) in cols_finales}
                
                # Leer datos
                self._df = pd.read_excel(xls, sheet_name=hoja, usecols=cols_finales, dtype=dtypes)
                
                # Renombrar columnas
                mapa_renombre = {mapa_cols[c.lower()]: c for c in self.COLUMNAS_REQUERIDAS}
                self._df.rename(columns=mapa_renombre, inplace=True)
                
                # Preparar índice para búsquedas rápidas
                self._df['doc_afiliado'] = self._df['doc_afiliado'].astype(str).str.strip()
                self._df.set_index('doc_afiliado', drop=False, inplace=True)
                self._df.sort_index(inplace=True)
                
                # Guardar caché
                self._df.to_pickle(self._ruta_cache)
                
        except Exception as e:
            raise RuntimeError(f"Error al leer el archivo Excel: {e}")

    def _encontrar_hoja_correcta(self, xls: pd.ExcelFile) -> tuple:
        """Busca la hoja que contiene las columnas requeridas."""
        columnas_req_lower = {c.lower() for c in self.COLUMNAS_REQUERIDAS}
        
        for nombre_hoja in xls.sheet_names:
            df_header = pd.read_excel(xls, sheet_name=nombre_hoja, nrows=0)
            cols_excel = list(df_header.columns)
            
            if not cols_excel:
                continue
            
            mapa_cols = {str(c).strip().lower(): c for c in cols_excel}
            cols_encontradas = columnas_req_lower & set(mapa_cols.keys())
            
            if cols_encontradas == columnas_req_lower:
                cols_finales = [mapa_cols[c.lower()] for c in self.COLUMNAS_REQUERIDAS]
                return nombre_hoja, cols_finales, mapa_cols
        
        return None, [], {}

    def consultar_por_afiliado(self, doc_afiliado: Union[str, int]) -> pd.DataFrame:
        """Filtra los datos buscando coincidencias exactas con doc_afiliado."""
        if self._df is None:
            self._cargar_datos()

        doc_str = str(doc_afiliado).strip()
        
        try:
            resultado = self._df.loc[[doc_str]]
            return resultado if not resultado.empty else pd.DataFrame(columns=self._df.columns)
        except KeyError:
            return pd.DataFrame(columns=self._df.columns)


if __name__ == "__main__":
    lector = EmssanarDataReader()
    doc_test = "1089196373"
    
    try:
        print(f"Buscando información para el afiliado: {doc_test}...")
        resultados = lector.consultar_por_afiliado(doc_test)
        print(f"Registros encontrados: {len(resultados)}")
        print(resultados.to_json(orient='records', indent=4, force_ascii=False))
    except Exception as e:
        print(f"Ocurrió un error: {e}")
