import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd
from typing import Dict, Optional, List
from contextlib import contextmanager


class CupsQuery:
    """
    Clase para manejar operaciones de base de datos relacionadas con códigos CUPS.
    Permite insertar nuevos registros y actualizar existentes.
    """
    
    # Campos estándar para evitar repetición
    _CAMPOS_SELECT = "id, codigo_cups, nombre_estudio, preparacion_especial, remitido"

    def __init__(self, host: str = "192.168.9.177", port: int = 5432, 
                 database: str = "practica", user: str = "postgres", 
                 password: str = "postgres"):
        """Inicializa la conexión a la base de datos."""
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    @contextmanager
    def _cursor(self):
        """Context manager para cursores con auto-commit y rollback en error."""
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cursor.close()

    def _row_to_dict(self, row: tuple) -> Dict:
        """Convierte una fila de resultado a diccionario."""
        return {
            'id': row[0],
            'codigo_cups': row[1],
            'nombre_estudio': row[2],
            'preparacion_especial': row[3],
            'remitido': row[4]
        }

    def _rows_to_list(self, rows: list) -> List[Dict]:
        """Convierte múltiples filas a lista de diccionarios."""
        return [self._row_to_dict(row) for row in rows]

    def obtener_codigos_existentes(self) -> Dict[str, Dict]:
        """
        Obtiene todos los códigos CUPS existentes en la base de datos.
        Retorna un diccionario con codigo_cups como clave y los datos como valor.
        """
        try:
            with self._cursor() as cursor:
                cursor.execute(f"SELECT {self._CAMPOS_SELECT} FROM codigos_cups;")
                return {str(row[1]): self._row_to_dict(row) for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error obteniendo códigos existentes: {e}")
            return {}

    def procesar_dataframe(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Procesa un DataFrame completo de códigos CUPS usando batch operations.
        Inserta nuevos registros y actualiza existentes de forma eficiente.
        
        Retorna un diccionario con estadísticas:
        - insertados: cantidad de registros nuevos insertados
        - actualizados: cantidad de registros existentes actualizados
        - errores: cantidad de errores
        """
        if df is None or df.empty:
            return {'insertados': 0, 'actualizados': 0, 'errores': 0, 'total': 0}
        
        # Obtener códigos existentes una sola vez
        codigos_existentes = set(self.obtener_codigos_existentes().keys())
        
        estadisticas = {
            'insertados': 0,
            'actualizados': 0,
            'errores': 0,
            'total': len(df)
        }
        
        print(f"\nProcesando {len(df)} registros...")
        print(f"Códigos existentes en BD: {len(codigos_existentes)}")
        
        # Preparar datos para batch insert/update
        registros_nuevos = []
        registros_actualizar = []
        
        for _, row in df.iterrows():
            codigo = str(row['codigo_cups']).strip()
            nombre = str(row['nombre_estudio']).strip() if pd.notna(row['nombre_estudio']) else None
            prep_esp = bool(row['preparacion_especial']) if pd.notna(row['preparacion_especial']) else False
            remitido = bool(row['remitido']) if pd.notna(row['remitido']) else False
            
            datos = (codigo, nombre, prep_esp, remitido)
            
            if codigo in codigos_existentes:
                registros_actualizar.append((nombre, prep_esp, remitido, codigo))
            else:
                registros_nuevos.append(datos)
                codigos_existentes.add(codigo)  # Evitar duplicados en el mismo batch
        
        # Ejecutar batch insert
        if registros_nuevos:
            try:
                with self._cursor() as cursor:
                    execute_batch(
                        cursor,
                        """INSERT INTO codigos_cups (codigo_cups, nombre_estudio, preparacion_especial, remitido)
                           VALUES (%s, %s, %s, %s);""",
                        registros_nuevos,
                        page_size=100
                    )
                estadisticas['insertados'] = len(registros_nuevos)
                print(f"  Insertados: {len(registros_nuevos)} registros")
            except Exception as e:
                print(f"Error en batch insert: {e}")
                estadisticas['errores'] += len(registros_nuevos)
        
        # Ejecutar batch update
        if registros_actualizar:
            try:
                with self._cursor() as cursor:
                    execute_batch(
                        cursor,
                        """UPDATE codigos_cups
                           SET nombre_estudio = %s, preparacion_especial = %s, remitido = %s
                           WHERE codigo_cups = %s;""",
                        registros_actualizar,
                        page_size=100
                    )
                estadisticas['actualizados'] = len(registros_actualizar)
                print(f"  Actualizados: {len(registros_actualizar)} registros")
            except Exception as e:
                print(f"Error en batch update: {e}")
                estadisticas['errores'] += len(registros_actualizar)
        
        return estadisticas

    def insertar_o_actualizar_codigo(self, codigo_cups: str, nombre_estudio: str, 
                                     preparacion_especial: bool, remitido: bool,
                                     codigos_existentes: dict = None) -> bool:
        """
        Inserta un nuevo código CUPS o actualiza uno existente (UPSERT).
        
        Args:
            codigo_cups: Código CUPS
            nombre_estudio: Nombre del estudio
            preparacion_especial: Si requiere preparación especial
            remitido: Si debe ser remitido
            codigos_existentes: Diccionario con códigos existentes (opcional)
        
        Retorna True si se insertó/actualizó correctamente, False en caso de error.
        """
        try:
            codigo = str(codigo_cups).strip()
            nombre = str(nombre_estudio).strip() if nombre_estudio else None
            prep = bool(preparacion_especial)
            rem = bool(remitido)
            
            with self._cursor() as cursor:
                # Verificar si existe
                existe = (codigos_existentes and codigo in codigos_existentes)
                if not existe:
                    cursor.execute("SELECT 1 FROM codigos_cups WHERE codigo_cups = %s LIMIT 1;", (codigo,))
                    existe = cursor.fetchone() is not None
                
                if existe:
                    cursor.execute(
                        """UPDATE codigos_cups SET nombre_estudio = %s, preparacion_especial = %s, remitido = %s
                           WHERE codigo_cups = %s;""",
                        (nombre, prep, rem, codigo)
                    )
                else:
                    cursor.execute(
                        """INSERT INTO codigos_cups (codigo_cups, nombre_estudio, preparacion_especial, remitido)
                           VALUES (%s, %s, %s, %s);""",
                        (codigo, nombre, prep, rem)
                    )
            return True
            
        except Exception as e:
            print(f"Error insertando/actualizando código CUPS {codigo_cups}: {e}")
            return False

    def actualizar_codigo_existente(self, codigo_cups: str, nombre_estudio: Optional[str] = None,
                                    preparacion_especial: Optional[bool] = None,
                                    remitido: Optional[bool] = None) -> bool:
        """
        Actualiza un código CUPS existente, solo los campos proporcionados.
        """
        updates, values = [], []
        
        if nombre_estudio is not None:
            updates.append("nombre_estudio = %s")
            values.append(str(nombre_estudio).strip())
        
        if preparacion_especial is not None:
            updates.append("preparacion_especial = %s")
            values.append(bool(preparacion_especial))
        
        if remitido is not None:
            updates.append("remitido = %s")
            values.append(bool(remitido))
        
        if not updates:
            return False
        
        values.append(str(codigo_cups).strip())
        
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    f"UPDATE codigos_cups SET {', '.join(updates)} WHERE codigo_cups = %s;",
                    values
                )
            return True
        except Exception as e:
            print(f"Error actualizando código CUPS {codigo_cups}: {e}")
            return False

    def _construir_where(self, codigo_cups: str = None, nombre_busqueda: str = None,
                         preparacion_especial: Optional[bool] = None,
                         remitido: Optional[bool] = None) -> tuple:
        """Construye la cláusula WHERE para las búsquedas."""
        condiciones, valores = [], []
        
        if codigo_cups:
            condiciones.append("codigo_cups = %s")
            valores.append(str(codigo_cups).strip())
        
        if nombre_busqueda:
            condiciones.append("LOWER(nombre_estudio) LIKE LOWER(%s)")
            valores.append(f"%{nombre_busqueda.strip()}%")
        
        if preparacion_especial is not None:
            condiciones.append("preparacion_especial = %s")
            valores.append(bool(preparacion_especial))
        
        if remitido is not None:
            condiciones.append("remitido = %s")
            valores.append(bool(remitido))
        
        return " AND ".join(condiciones) if condiciones else "1=1", valores

    def buscar_por_codigo(self, codigo_cups: str) -> Optional[Dict]:
        """Busca un código CUPS por su código exacto."""
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    f"SELECT {self._CAMPOS_SELECT} FROM codigos_cups WHERE codigo_cups = %s;",
                    (str(codigo_cups).strip(),)
                )
                resultado = cursor.fetchone()
                return self._row_to_dict(resultado) if resultado else None
        except Exception as e:
            print(f"Error buscando código CUPS {codigo_cups}: {e}")
            return None

    def buscar_por_nombre(self, nombre_busqueda: str, limite: int = 100) -> List[Dict]:
        """Busca códigos CUPS por nombre de estudio (búsqueda parcial, case-insensitive)."""
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    f"""SELECT {self._CAMPOS_SELECT} FROM codigos_cups
                        WHERE LOWER(nombre_estudio) LIKE LOWER(%s)
                        ORDER BY nombre_estudio LIMIT %s;""",
                    (f"%{nombre_busqueda.strip()}%", limite)
                )
                return self._rows_to_list(cursor.fetchall())
        except Exception as e:
            print(f"Error buscando por nombre: {e}")
            return []

    def buscar_con_filtros(self, codigo_cups: str = None, nombre_busqueda: str = None,
                           preparacion_especial: Optional[bool] = None,
                           remitido: Optional[bool] = None,
                           limite: int = 500) -> List[Dict]:
        """
        Busca códigos CUPS con múltiples filtros.
        """
        try:
            where_clause, valores = self._construir_where(
                codigo_cups, nombre_busqueda, preparacion_especial, remitido
            )
            valores.append(limite)
            
            with self._cursor() as cursor:
                cursor.execute(
                    f"""SELECT {self._CAMPOS_SELECT} FROM codigos_cups
                        WHERE {where_clause} ORDER BY codigo_cups LIMIT %s;""",
                    valores
                )
                return self._rows_to_list(cursor.fetchall())
        except Exception as e:
            print(f"Error en búsqueda con filtros: {e}")
            return []

    def obtener_todos(self, limite: int = 1000, offset: int = 0) -> List[Dict]:
        """Obtiene todos los códigos CUPS con paginación."""
        try:
            with self._cursor() as cursor:
                cursor.execute(
                    f"""SELECT {self._CAMPOS_SELECT} FROM codigos_cups
                        ORDER BY codigo_cups LIMIT %s OFFSET %s;""",
                    (limite, offset)
                )
                return self._rows_to_list(cursor.fetchall())
        except Exception as e:
            print(f"Error obteniendo todos los códigos: {e}")
            return []

    def contar_registros(self, codigo_cups: str = None, nombre_busqueda: str = None,
                         preparacion_especial: Optional[bool] = None,
                         remitido: Optional[bool] = None) -> int:
        """Cuenta el número de registros que coinciden con los filtros."""
        try:
            where_clause, valores = self._construir_where(
                codigo_cups, nombre_busqueda, preparacion_especial, remitido
            )
            
            with self._cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM codigos_cups WHERE {where_clause};", valores)
                resultado = cursor.fetchone()
                return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Error contando registros: {e}")
            return 0
