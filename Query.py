import psycopg2
import pandas as pd
import numpy as np
from read_data import EmssanarDataReader

class Query:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="192.168.9.177",
            port=5432,
            database="practica",
            user="postgres",
            password="postgres"
        )

    def cerrar_conexion(self):
        if self.conn:
            self.conn.close()

    def obtener_solicitudes_existentes(self) -> set:
        """
        Obtiene todos los números de solicitud que ya existen en la base de datos.
        Retorna un conjunto (set) para búsquedas rápidas.
        """
        try:
            cursor = self.conn.cursor()
            query = "SELECT numero_solicitud FROM solicitudes_servicios;"
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()
            # Convertir a set de strings para búsqueda rápida
            return {str(row[0]) for row in resultados if row[0] is not None}
        except Exception as e:
            print(f"Error obteniendo solicitudes existentes: {e}")
            return set()

    def insertar_solicitud_servicio(self, data: dict, solicitudes_existentes: set = None) -> bool:
        """
        Inserta una solicitud de servicio solo si no existe previamente.
        Retorna True si se insertó, False si ya existía.
        
        Args:
            data: Diccionario con los datos de la solicitud
            solicitudes_existentes: Set con los números de solicitud existentes (opcional, para optimización)
        """
        numero_solicitud = str(data.get("numero_solicitud"))
        
        # Verificar si ya existe (usando el set si se proporciona, o consultando directamente)
        if solicitudes_existentes is not None:
            if numero_solicitud in solicitudes_existentes:
                return False
        else:
            # Fallback: consulta individual si no se proporciona el set
            if self.existe_solicitud(numero_solicitud):
                return False
        
        try:
            cursor = self.conn.cursor()

            query = """
                INSERT INTO solicitudes_servicios (
                    codigo_servicio_completo,
                    doc_afiliado,
                    numero_solicitud,
                    cod_diag,
                    desc_diag,
                    clasificacion_servicios_acceso,
                    descr_servicio_1,
                    estado_solicitud,
                    num_autorizacion,
                    fecha_autorizacion_1,
                    ips_asignada,
                    ciudad_ips_asignada,
                    cantidad,
                    primer_nom,
                    segundo_nom,
                    primer_ape,
                    segundo_ape,
                    edad_anios,
                    estado_solicitud_2,
                    ips_solicitante
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s,%s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """

            values = (
                data.get("codigo_servicio_completo"),
                data.get("doc_afiliado"),
                data.get("numero_solicitud"),
                data.get("cod_diag"),
                data.get("desc_diag"),
                data.get("clasificacion_servicios_acceso"),
                data.get("descr_servicio_1"),
                data.get("estado_solicitud"),
                data.get("num_autorizacion"),
                data.get("fecha_autorizacion_1"),
                data.get("ips_asignada"),
                data.get("ciudad_ips_asignada"),
                data.get("cantidad"),
                data.get("primer_nom"),
                data.get("segundo_nom"),
                data.get("primer_ape"),
                data.get("segundo_ape"),
                data.get("edad_anios"),
                data.get("estado_solicitud_2"),
                data.get("ips_solicita"),
            )

            cursor.execute(query, values)
            self.conn.commit()
            cursor.close()
            return True

        except Exception as e:
            print(f"Error insertando solicitud {numero_solicitud}:", e)
            self.conn.rollback()
            return False
    
    def existe_solicitud(self, numero_solicitud: str) -> bool:
        """
        Verifica si una solicitud ya existe en la base de datos.
        (Método de respaldo, se prefiere usar obtener_solicitudes_existentes)
        """
        try:
            cursor = self.conn.cursor()
            query = "SELECT COUNT(*) FROM solicitudes_servicios WHERE numero_solicitud = %s;"
            cursor.execute(query, (str(numero_solicitud),))
            resultado = cursor.fetchone()
            cursor.close()
            return resultado[0] > 0
        except Exception as e:
            print(f"Error verificando existencia de solicitud {numero_solicitud}:", e)
            return False

if __name__ == "__main__":
    print("Iniciando proceso de migración Excel -> Base de Datos...")
    
    # 1. Instanciar el lector de datos
    lector = EmssanarDataReader()
    
    try:
        # 2. Cargar los datos (accedemos al método interno para forzar carga completa)
        lector._cargar_datos()
        df = lector._df
        
        if df is not None and not df.empty:
            print(f"Se encontraron {len(df)} registros para procesar.")
            
            
            df = df.where(pd.notnull(df), None)
            
            # 4. Conectar a Base de Datos y obtener solicitudes existentes
            db = Query()
            print("Verificando registros existentes en la base de datos...")
            solicitudes_existentes = db.obtener_solicitudes_existentes()
            print(f"Se encontraron {len(solicitudes_existentes)} registros ya existentes en la base de datos.")
            
            # 5. Filtrar registros nuevos (que no existen en la BD)
            print("Filtrando registros nuevos...")
            df['numero_solicitud_str'] = df['numero_solicitud'].astype(str)
            df_nuevos = df[~df['numero_solicitud_str'].isin(solicitudes_existentes)].copy()
            df_nuevos = df_nuevos.drop(columns=['numero_solicitud_str'])
            
            duplicados = len(df) - len(df_nuevos)
            print(f"Registros nuevos a insertar: {len(df_nuevos)}")
            print(f"Registros duplicados (omitidos): {duplicados}")
            
            # 6. Insertar solo los registros nuevos
            if not df_nuevos.empty:
                contador = 0
                insertados = 0
                
                for index, row in df_nuevos.iterrows():
                    # Convertimos la fila a diccionario
                    data = row.to_dict()
                    
                    # Insertar (ya sabemos que no existe, pero mantenemos la verificación por seguridad)
                    if db.insertar_solicitud_servicio(data, solicitudes_existentes):
                        insertados += 1
                    
                    contador += 1
                    if contador % 100 == 0:
                        print(f"Procesados {contador}/{len(df_nuevos)} registros nuevos...")
                
                print(f"\n¡Proceso completado!")
                print(f"Total registros en Excel: {len(df)}")
                print(f"Registros nuevos insertados: {insertados}")
                print(f"Registros duplicados (omitidos): {duplicados}")
            else:
                print(f"\n¡Proceso completado!")
                print(f"Todos los registros ({len(df)}) ya existen en la base de datos.")
                print(f"No se insertaron nuevos registros.")
            
            db.cerrar_conexion()
        else:
            print("El archivo Excel parece estar vacío o no se cargaron datos.")
            
    except Exception as e:
        print(f"Ocurrió un error crítico: {e}")
