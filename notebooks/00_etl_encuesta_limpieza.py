# %% [markdown]
"""
=============================================================================
ETL Pipeline: Procesamiento de Encuesta Congresistas
=============================================================================

DESCRIPCIÓN GENERAL:
Este módulo implementa un pipeline ETL completo para procesar datos de encuestas
de congresistas. El flujo incluye:

1. Carga y validación de datos
2. Limpieza y filtrado de respuestas incompletas
3. Renombrado estandarizado de columnas
4. Conversión de tipos de datos
5. Tratamiento de valores categóricos y numéricos
6. Generación de reportes y exportación

DEPENDENCIAS:
- pandas>=1.5.0
- numpy>=1.23.0
- openpyxl>=3.0.0
- unidecode>=1.3.0

AUTOR: Iuliia Rytck Molodykh
FECHA: 13/10/2025
"""
# %%
import pandas as pd
import numpy as np
import re
import openpyxl
from unidecode import unidecode
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# %% [markdown]
# =============================================================================
# 1. FUNCIONES DE CARGA Y VALIDACIÓN
# =============================================================================
# %%
def cargar_datos(ruta_archivo: str) -> pd.DataFrame:
    """
    Carga datos desde archivo Excel y realiza validación básica.
    
    Args:
        ruta_archivo: Ruta al archivo Excel
        
    Returns:
        DataFrame con datos cargados
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo está vacío
    """
    logger.info(f"Cargando datos desde: {ruta_archivo}")
    
    if not Path(ruta_archivo).exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
    
    df = pd.read_excel(ruta_archivo)
    
    if df.empty:
        raise ValueError("El archivo está vacío")
    
    logger.info(f"Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
    return df


def limpiar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia nombres de columnas eliminando espacios extra.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame con columnas limpias
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
    )
    logger.info("Nombres de columnas limpiados")
    return df

# %% [markdown]
# =============================================================================
# 2. FUNCIONES DE FILTRADO Y LIMPIEZA
# =============================================================================
# %%
def filtrar_respuestas_completas(
    df: pd.DataFrame,
    columna_ultima_pagina: str = 'Última página',
    valor_completo: int = 7
) -> Tuple[pd.DataFrame, int]:
    """
    Filtra respuestas que llegaron a la última página (completas).
    
    Args:
        df: DataFrame original
        columna_ultima_pagina: Nombre de la columna indicadora
        valor_completo: Valor que indica encuesta completa
        
    Returns:
        Tupla (DataFrame filtrado, número de filas eliminadas)
    """
    filas_inicial = len(df)
    
    if columna_ultima_pagina not in df.columns:
        logger.warning(f"Columna '{columna_ultima_pagina}' no encontrada. Saltando filtrado.")
        return df, 0
    
    df_filtrado = df[df[columna_ultima_pagina] == valor_completo].copy()
    filas_eliminadas = filas_inicial - len(df_filtrado)
    
    logger.info(f"Respuestas filtradas: {filas_eliminadas} incompletas eliminadas")
    logger.info(f"Respuestas válidas: {len(df_filtrado)}")
    
    return df_filtrado, filas_eliminadas


def eliminar_columnas_innecesarias(
    df: pd.DataFrame,
    columnas_a_eliminar: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Elimina columnas administrativas o de temporización innecesarias.
    
    Args:
        df: DataFrame original
        columnas_a_eliminar: Lista de columnas a eliminar (opcional)
        
    Returns:
        DataFrame sin columnas innecesarias
    """
    if columnas_a_eliminar is None:
        # Patrón para columnas de temporización
        patron_tiempo = r'^Temporización de la pregunta:'
        columnas_a_eliminar = [
            col for col in df.columns 
            if re.match(patron_tiempo, col)
        ] + ['Dirección IP', 'Semilla', 'URL de referencia']
    
    # Filtrar solo columnas existentes
    columnas_existentes = [col for col in columnas_a_eliminar if col in df.columns]
    
    df_limpio = df.drop(columns=columnas_existentes)
    logger.info(f"Eliminadas {len(columnas_existentes)} columnas innecesarias")
    
    return df_limpio

# %% [markdown]
# =============================================================================
# 3. FUNCIONES DE RENOMBRADO
# =============================================================================
# %%
def obtener_diccionario_renombres() -> Dict[str, str]:
    """
    Retorna diccionario estándar de renombres de columnas.
    
    Returns:
        Diccionario {nombre_original: nombre_nuevo}
    """
    return {
        # Perfil
        'Indica, por favor, su lugar de residencia habitual': 'residencia',
        'Indique provincia': 'provincia',
        'Indique País de residencia': 'pais',
        '¿Desde dónde viajó para venir a Valencia?': 'origen_viaje',
        '¿Qué medios de transporte utilizó para llegar a Valencia? [Avión]': 'transporte_llegada_avion',
        '¿Qué medios de transporte utilizó para llegar a Valencia? [Tren]': 'transporte_llegada_tren',
        '¿Qué medios de transporte utilizó para llegar a Valencia? [Autobus]': 'transporte_llegada_bus',
        '¿Qué medios de transporte utilizó para llegar a Valencia? [Vehículo propio/alquilado]': 'transporte_llegada_coche',
        '¿Qué medios de transporte utilizó para llegar a Valencia? [Barco]': 'transporte_llegada_barco',
        '¿Qué medios de transporte utilizó para llegar a Valencia? [Otro]': 'transporte_llegada_otro',
        '¿Vino a Valencia con algún acompañante que no participó en el Congreso?': 'acompanante',
        '¿Cuántas personas le acompañaron que no participaron el el Congreso?': 'num_acompanantes',
        '¿En qué rango de edad se encuentra?': 'edad_rango',
        '¿Cuál es su género?': 'genero',
        '¿Cuál es su género? [Otro]': 'genero_otro',
        'Por favor, seleccione la categoría que mejor describe su profesión principal.': 'profesion',
        'Por favor, seleccione la categoría que mejor describe su profesión principal. [Otro]': 'profesion_otro',
        '¿Qué rol desempeña principalmente en su actividad profesional?': 'rol_profesional',
        '¿Qué rol desempeña principalmente en su actividad profesional? [Otro]': 'rol_profesional_otro',
        '¿Cuál fue su rol en el Congreso?': 'rol_congreso',
        '¿Cuál fue su rol en el Congreso? [Otro]': 'rol_congreso_otro',
        '¿Ha asistido anteriormente a Congresos en Valencia?': 'asistencia_previa',
        
        # Alojamiento
        '¿Su estancia en Valencia se limitó a los días del congreso o se amplió más allá?': 'duracion_estancia',
        '¿Cuántas noches, en total, se quedó en Valencia?': 'noches_valencia',
        '¿Qué tipo de alojamiento utilizó durante su estancia (en caso de haber pernoctado fuera de su domicilio habitual)?': 'alojamiento',
        '¿Qué tipo de alojamiento utilizó durante su estancia (en caso de haber pernoctado fuera de su domicilio habitual)? [Otro]': 'alojamiento_otro',
        '¿Podría indicarnos dónde se hospedó durante su estancia en Valencia?': 'ubicacion_alojamiento',
        
        # Desplazamientos
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Taxi o VTC (Cabify, Uber)][Para asistir al congreso]': 'uso_taxi_congreso',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Taxi o VTC (Cabify, Uber)][Para actividades fuera del congreso]': 'uso_taxi_ocio',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Autobus][Para asistir al congreso]': 'uso_bus_congreso',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Autobus][Para actividades fuera del congreso]': 'uso_bus_ocio',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Metro/Tranvía][Para asistir al congreso]': 'uso_metro_congreso',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Metro/Tranvía][Para actividades fuera del congreso]': 'uso_metro_ocio',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Coche particular o de alquiler][Para asistir al congreso]': 'uso_coche_congreso',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Coche particular o de alquiler][Para actividades fuera del congreso]': 'uso_coche_ocio',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Bicicleta o patinete][Para asistir al congreso]': 'uso_bici_congreso',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Bicicleta o patinete][Para actividades fuera del congreso]': 'uso_bici_ocio',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Lanzadera][Para asistir al congreso]': 'uso_lanzadera_congreso',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [Lanzadera][Para actividades fuera del congreso]': 'uso_lanzadera_ocio',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [A pie][Para asistir al congreso]': 'uso_pie_congreso',
        '¿Cuántas veces utilizó cada uno de los siguientes medios de transporte durante su estancia en Valencia para: 1. Asistir al congreso 2. Realizar actividades fuera del Congreso (ocio, turismo, cenas, etc) [A pie][Para actividades fuera del congreso]': 'uso_pie_ocio',
        
        # Alimentación
        '¿Cuántas veces comió fuera del congreso? [Carne roja (Vacuno, cordero, cerdo)][Restaurante local]': 'carne_roja_restaurante',
        '¿Cuántas veces comió fuera del congreso? [Carne roja (Vacuno, cordero, cerdo)][Cadena de comida rápida]': 'carne_roja_fastfood',
        '¿Cuántas veces comió fuera del congreso? [Carne roja (Vacuno, cordero, cerdo)][Pedidos a domicilio]': 'carne_roja_domicilio',
        '¿Cuántas veces comió fuera del congreso? [Carne roja (Vacuno, cordero, cerdo)][Cociné en el alojamiento]': 'carne_roja_casera',
        '¿Cuántas veces comió fuera del congreso? [Carne de ave o pescado][Restaurante local]': 'avepescado_restaurante',
        '¿Cuántas veces comió fuera del congreso? [Carne de ave o pescado][Cadena de comida rápida]': 'avepescado_fastfood',
        '¿Cuántas veces comió fuera del congreso? [Carne de ave o pescado][Pedidos a domicilio]': 'avepescado_domicilio',
        '¿Cuántas veces comió fuera del congreso? [Carne de ave o pescado][Cociné en el alojamiento]': 'avepescado_casera',
        '¿Cuántas veces comió fuera del congreso? [Marisco (Bogavante, Langostinos, etc)][Restaurante local]': 'marisco_restaurante',
        '¿Cuántas veces comió fuera del congreso? [Marisco (Bogavante, Langostinos, etc)][Cadena de comida rápida]': 'marisco_fastfood',
        '¿Cuántas veces comió fuera del congreso? [Marisco (Bogavante, Langostinos, etc)][Pedidos a domicilio]': 'marisco_domicilio',
        '¿Cuántas veces comió fuera del congreso? [Marisco (Bogavante, Langostinos, etc)][Cociné en el alojamiento]': 'marisco_casera',

        # Turismo (simplificado - se pueden agregar más)
        '¿Realizó visitas turísticas durante su estancia en Valencia?': 'visitas_turisticas',

        # Compras
        '¿Realizó compras durante su estancia en Valencia?': 'compras_realizo',
        'Por favor, para cada tipo de producto adquirido, indique la cantidad y, si lo conoce, su lugar de origen. [Productos textiles (ropa, pañuelos, etc.)][Eje 1]': 'compras_textiles_cantidad',
        'Por favor, para cada tipo de producto adquirido, indique la cantidad y, si lo conoce, su lugar de origen. [Artesanía (cerámica, madera, artículos de piel, etc.)][Eje 1]': 'compras_artesania_cantidad',
        'Por favor, para cada tipo de producto adquirido, indique la cantidad y, si lo conoce, su lugar de origen. [Productos alimenticios locales (vino, aceite, dulces, etc.)][Eje 1]': 'compras_alimentacion_cantidad',
        'Por favor, para cada tipo de producto adquirido, indique la cantidad y, si lo conoce, su lugar de origen. [Souvenirs de producción masiva (imanes, llaveros, réplicas, etc.)][Eje 1]': 'compras_souvenirs_cantidad',

        # Sugerencias
        '¿Hay algo más que nos quiera comentar? Puede utilizar este espacio para compartir sugerencias, incidencias o cualquier otra observación relacionada con su experiencia.': 'sugerencias'
    }


def renombrar_columnas(
    df: pd.DataFrame,
    diccionario_renombres: Optional[Dict[str, str]] = None
) -> Tuple[pd.DataFrame, int]:
    """
    Renombra columnas según diccionario estándar o personalizado.
    
    Args:
        df: DataFrame original
        diccionario_renombres: Diccionario de renombres (opcional)
        
    Returns:
        Tupla (DataFrame renombrado, número de columnas renombradas)
    """
    if diccionario_renombres is None:
        diccionario_renombres = obtener_diccionario_renombres()
    
    # Filtrar solo columnas existentes
    renombres_aplicables = {
        k: v for k, v in diccionario_renombres.items() 
        if k in df.columns
    }
    
    df_renombrado = df.rename(columns=renombres_aplicables)
    logger.info(f"Renombradas {len(renombres_aplicables)} columnas")
    
    return df_renombrado, len(renombres_aplicables)

# %% [markdown]
# =============================================================================
# 4. FUNCIONES DE CONVERSIÓN DE TIPOS DE DATOS
# =============================================================================
# %%
def convertir_fechas(df: pd.DataFrame, columnas_fecha: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Convierte columnas de fecha a tipo datetime.
    
    Args:
        df: DataFrame original
        columnas_fecha: Lista de columnas fecha (opcional)
        
    Returns:
        DataFrame con fechas convertidas
    """
    if columnas_fecha is None:
        columnas_fecha = ['Fecha de envío', 'Fecha de inicio', 'Fecha de la última acción']
    
    df = df.copy()
    for col in columnas_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            logger.info(f"Columna '{col}' convertida a datetime")
    
    return df


def convertir_binarias(
    df: pd.DataFrame,
    columnas_binarias: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Convierte variables binarias Sí/No a 1/0.
    
    Args:
        df: DataFrame original
        columnas_binarias: Lista de columnas binarias (opcional)
        
    Returns:
        DataFrame con binarias convertidas
    """
    df = df.copy()
    
    if columnas_binarias is None:
        # Detectar automáticamente columnas binarias
        yes_values = {'Sí', 'Si', 'si', 'sí'}
        no_values = {'No', 'no'}
        
        columnas_binarias = []
        for col in df.select_dtypes(include='object').columns:
            valores_unicos = set(df[col].dropna().unique())
            if valores_unicos and valores_unicos.issubset(yes_values.union(no_values)):
                columnas_binarias.append(col)
    
    def convertir_valor(valor):
        """Convierte valor individual Sí/No a 1/0."""
        if pd.isna(valor):
            return np.nan
        val_norm = unidecode(str(valor).strip().lower())
        if val_norm in {'si', 'sí'}:
            return 1
        elif val_norm == 'no':
            return 0
        return np.nan
    
    for col in columnas_binarias:
        if col in df.columns:
            df[col] = df[col].apply(convertir_valor).astype('Int8')
            logger.info(f"Columna binaria '{col}' convertida a 0/1")
    
    return df


def mapear_columnas_categoricas_ordenadas(
    df: pd.DataFrame,
    mapeos: Optional[Dict[str, Dict]] = None
) -> pd.DataFrame:
    """
    Mapea columnas categóricas ordenadas a valores numéricos.
    
    Args:
        df: DataFrame original
        mapeos: Diccionario {nombre_columna: {valor_original: valor_numerico}}
        
    Returns:
        DataFrame con columnas mapeadas
    """
    if mapeos is None:
        mapeos = {
            'noches_valencia': {
                '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                '6': 6, '7': 7, '8': 8, '9': 9, 'más de 10': 10
            },
            'compras_textiles_cantidad': {
                '1': 1, '2': 2, '3': 3, '4': 4, 'más de 5': 5
            },
            'compras_artesania_cantidad': {
                '1': 1, '2': 2, '3': 3, '4': 4, 'más de 5': 5
            },
            'compras_alimentacion_cantidad': {
                '1': 1, '2': 2, '3': 3, '4': 4, 'más de 5': 5
            },
            'compras_souvenirs_cantidad': {
                '1': 1, '2': 2, '3': 3, '4': 4, 'más de 5': 5
            }
        }
    
    df = df.copy()
    
    for col, mapeo in mapeos.items():
        if col not in df.columns:
            continue
        
        # Normalizar columna
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].apply(lambda x: unidecode(x.lower()))
        
        # Normalizar claves del mapeo
        mapeo_norm = {unidecode(k.lower()): v for k, v in mapeo.items()}
        
        # Aplicar mapeo
        df[col] = df[col].map(mapeo_norm).fillna(0).astype(int)
        logger.info(f"Columna '{col}' mapeada a valores numéricos")
    
    return df

# %% [markdown]
# =============================================================================
# 5. FUNCIONES DE CALIDAD Y REPORTE
# =============================================================================
# %%
def generar_reporte_calidad(
    df_original: pd.DataFrame,
    df_procesado: pd.DataFrame,
    filas_eliminadas: int
) -> pd.DataFrame:
    """
    Genera reporte de calidad del procesamiento.
    
    Args:
        df_original: DataFrame original
        df_procesado: DataFrame procesado
        filas_eliminadas: Número de filas eliminadas
        
    Returns:
        DataFrame con métricas de calidad
    """
    reporte = pd.DataFrame({
        'Métrica': [
            'Filas originales',
            'Filas procesadas',
            'Filas eliminadas',
            'Columnas originales',
            'Columnas procesadas',
            'Valores nulos totales',
            'Porcentaje completitud'
        ],
        'Valor': [
            len(df_original),
            len(df_procesado),
            filas_eliminadas,
            len(df_original.columns),
            len(df_procesado.columns),
            df_procesado.isnull().sum().sum(),
            f"{((df_procesado.notna().sum().sum() / df_procesado.size) * 100):.2f}%"
        ]
    })
    
    return reporte


def generar_reporte_nulos(df: pd.DataFrame, umbral: float = 0.0) -> pd.DataFrame:
    """
    Genera reporte de valores nulos por columna.
    
    Args:
        df: DataFrame a analizar
        umbral: Umbral mínimo de nulos para incluir en reporte (0-1)
        
    Returns:
        DataFrame con reporte de nulos
    """
    nulos = df.isnull().sum()
    porcentaje = (nulos / len(df)) * 100
    
    reporte = pd.DataFrame({
        'Columna': nulos.index,
        'Nulos': nulos.values,
        'Porcentaje': porcentaje.values
    })
    
    reporte = reporte[reporte['Porcentaje'] > umbral * 100]
    reporte = reporte.sort_values('Porcentaje', ascending=False)
    
    return reporte

# %% [markdown]
# =============================================================================
# 6. FUNCIÓN PRINCIPAL DE PIPELINE
# =============================================================================
# %%
def ejecutar_pipeline_etl(
    ruta_entrada: str,
    ruta_salida: str,
    guardar_backup: bool = True
) -> Tuple[pd.DataFrame, Dict]:
    """
    Ejecuta pipeline ETL completo.
    
    Args:
        ruta_entrada: Ruta del archivo Excel de entrada
        ruta_salida: Ruta del archivo Excel de salida
        guardar_backup: Si se guarda copia de datos originales
        
    Returns:
        Tupla (DataFrame procesado, diccionario con métricas)
    """
    logger.info("=" * 80)
    logger.info("INICIANDO PIPELINE ETL")
    logger.info("=" * 80)
    
    # 1. Cargar datos
    df = cargar_datos(ruta_entrada)
    df_backup = df.copy()
    
    # 2. Limpieza inicial
    df = limpiar_nombres_columnas(df)
    
    # 3. Filtrar respuestas completas
    df, filas_eliminadas = filtrar_respuestas_completas(df)
    
    # 4. Eliminar columnas innecesarias
    df = eliminar_columnas_innecesarias(df)
    
    # 5. Renombrar columnas
    df, num_renombres = renombrar_columnas(df)
    
    # 6. Conversión de tipos
    df = convertir_fechas(df)
    df = convertir_binarias(df)
    df = mapear_columnas_categoricas_ordenadas(df)
    
    # 7. Generar reportes
    reporte_calidad = generar_reporte_calidad(df_backup, df, filas_eliminadas)
    reporte_nulos = generar_reporte_nulos(df, umbral=0.3)
    
    # 8. Guardar resultados
    logger.info(f"Guardando resultados en: {ruta_salida}")
    with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Datos_Procesados', index=False)
        reporte_calidad.to_excel(writer, sheet_name='Reporte_Calidad', index=False)
        reporte_nulos.to_excel(writer, sheet_name='Reporte_Nulos', index=False)
        
        if guardar_backup:
            df_backup.to_excel(writer, sheet_name='Datos_Originales', index=False)
    
    # 9. Métricas finales
    metricas = {
        'filas_original': len(df_backup),
        'filas_final': len(df),
        'filas_eliminadas': filas_eliminadas,
        'columnas_renombradas': num_renombres,
        'completitud': (df.notna().sum().sum() / df.size) * 100
    }
    
    logger.info("=" * 80)
    logger.info("PIPELINE ETL COMPLETADO")
    logger.info(f"Filas procesadas: {metricas['filas_final']}")
    logger.info(f"Completitud: {metricas['completitud']:.2f}%")
    logger.info("=" * 80)
    
    return df, metricas

# %% [markdown]
# =============================================================================
# 7. EJECUCIÓN PRINCIPAL
# =============================================================================
# %%
if __name__ == "__main__":
    # Configuración de rutas
    DATA_DIR = Path("../data")
    RUTA_ENTRADA = DATA_DIR /"results-survey798946.xlsx"
    RUTA_SALIDA = DATA_DIR /"encuesta_procesada.xlsx"
    
    try:
        df_procesado, metricas = ejecutar_pipeline_etl(
            ruta_entrada=RUTA_ENTRADA,
            ruta_salida=RUTA_SALIDA,
            guardar_backup=True
        )
        
        print("\n✅ Procesamiento exitoso!")
        print(f"📊 Dataset final: {metricas['filas_final']} filas")
        
    except Exception as e:
        logger.error(f"Error en el pipeline ETL: {e}")
        print(f"\n❌ Error: {e}")