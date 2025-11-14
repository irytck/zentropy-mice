# %% [markdown]
"""
# ETL Pipeline - Calculadora de Entropía
## Transformación de datos de encuesta a congreso

Este notebook procesa datos de encuestas de visitantes a un congreso y genera
métricas agregadas por tipo de visitante para alimentar una calculadora de entropía.

### Etapas del pipeline:
1. Carga y validación de datos
2. Filtrado y limpieza
3. Clasificación de visitantes (tipo 1 y tipo 2)
4. Cálculo de métricas agregadas
5. Exportación de resultados

### Notas sobre decisiones:
- Se filtran cuestionarios incompletos (última página != 7)
- Se excluyen visitantes sin alojamiento (locales que no pernoctan)
- Visitor type 1: Clasifica por procedencia (Internacional/Nacional/Local)
- Visitor type 2: Clasifica por patrón de transporte dominante
"""

# %% [markdown]
"""
## 1. Configuración e Imports
"""

# %%
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, List
import warnings
from IPython.display import display

# Configuración
pd.set_option('display.max_columns', None)
pd.set_option('future.no_silent_downcasting', True)
warnings.filterwarnings('ignore', category=FutureWarning)

# %% [markdown]
"""
## 2. Configuración de Rutas y Parámetros
"""

# %%
# Configuración de rutas (usar rutas relativas)
DATA_DIR = Path("../data")
INPUT_FILE = DATA_DIR / "encuesta_procesada.xlsx"
OUTPUT_FILE = DATA_DIR / "encuesta_tansformada.xlsx"

# Parámetros de negocio
CONFIG = {
    "complete_survey_last_page": 7,
    "excluded_accommodation": "Ninguno, me desplacé desde mi lugar de residencia",
    "visitor_type1_categories": ["International", "National", "Local"],
    "visitor_type2_categories": ["Eco-conscious", "Standard", "Young professional/student"],
    "spain_code": "España",
    "valencia_code": "Valencia/València",
    "foreign_code": "Extranjero"
}

# %% [markdown]
"""
## 3. Funciones de Utilidad
"""

# %%
def load_survey_data(file_path: Path) -> pd.DataFrame:
    """
    Carga datos de encuesta desde Excel con manejo de encoding.
    
    Args:
        file_path: Ruta al archivo Excel
        
    Returns:
        DataFrame con los datos cargados
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no puede ser leído
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        print(f"✓ Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
        return df
    except Exception as e:
        raise ValueError(f"Error al cargar el archivo: {e}")


def validate_data(df: pd.DataFrame) -> None:
    """
    Valida que el DataFrame tenga las columnas esperadas y formato correcto.
    
    Args:
        df: DataFrame a validar
        
    Raises:
        AssertionError: Si falla alguna validación
    """
    required_cols = [
        "Última página", "alojamiento", "residencia", 
        "pais", "provincia", "noches_valencia"
    ]
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise AssertionError(f"Columnas faltantes: {missing_cols}")
    
    assert df["Última página"].notna().any(), "No hay datos en 'Última página'"
    assert df["Última página"].max() <= 10, f"Valor inesperado en 'Última página': {df['Última página'].max()}"
    
    print("✓ Validación de datos completada")


def classify_visitor_type1(row: pd.Series) -> str:
    """
    Clasifica visitantes por procedencia geográfica.
    
    Criterios:
    - Internacional: residencia = Extranjero O país != España
    - Local: residencia = España Y provincia = Valencia
    - Nacional: residencia = España Y provincia != Valencia
    
    Args:
        row: Fila del DataFrame con datos de visitante
        
    Returns:
        Categoría de visitor type 1
    """
    if row["residencia"] == CONFIG["foreign_code"] or \
       (pd.notna(row["pais"]) and row["pais"] != CONFIG["spain_code"]):
        return "International"
    elif row["residencia"] == CONFIG["spain_code"] and \
         row["provincia"] == CONFIG["valencia_code"]:
        return "Local"
    elif row["residencia"] == CONFIG["spain_code"]:
        return "National"
    else:
        return np.nan


def classify_visitor_type2(row: pd.Series) -> str:
    """
    Clasifica visitantes por patrón de transporte al congreso.
    
    Criterios (en orden de prioridad para desempates):
    1. Eco-conscious: Uso dominante de bici/pie
    2. Young professional/student: Uso dominante de transporte público
    3. Standard: Uso dominante de coche/taxi
    
    Nota: La jerarquía para desempates favorece opciones más sostenibles
    
    Args:
        row: Fila del DataFrame con datos de transporte
        
    Returns:
        Categoría de visitor type 2
    """
    public = row["public_transport_use_congreso"]
    car = row["car_use_congreso"]
    walk_bike = row["walk_bike_use_congreso"]
    
    # Si no hay viajes registrados
    if public == 0 and car == 0 and walk_bike == 0:
        return "No transport reported"
    
    # Determinar transporte dominante (con jerarquía para empates)
    max_val = max(public, car, walk_bike)
    
    if walk_bike == max_val:
        return "Eco-conscious"
    elif public == max_val:
        return "Young professional/student"
    else:
        return "Standard"


def create_transport_variables(df: pd.DataFrame, context: str) -> pd.DataFrame:
    """
    Crea variables agregadas de uso de transporte.
    
    Agrupa modos de transporte en tres categorías:
    - Transporte público: bus + metro
    - Vehículo privado: taxi + coche
    - Movilidad activa: bici + pie
    
    Args:
        df: DataFrame con datos de transporte
        context: Contexto del transporte ('congreso' o 'ocio')
        
    Returns:
        DataFrame con nuevas columnas de transporte agregado
    """
    df[f"public_transport_use_{context}"] = (
        df[f"uso_bus_{context}"].fillna(0) + 
        df[f"uso_metro_{context}"].fillna(0)
    )
    df[f"car_use_{context}"] = (
        df[f"uso_taxi_{context}"].fillna(0) + 
        df[f"uso_coche_{context}"].fillna(0)
    )
    df[f"walk_bike_use_{context}"] = (
        df[f"uso_bici_{context}"].fillna(0) + 
        df[f"uso_pie_{context}"].fillna(0)
    )
    
    print(f"✓ Variables de transporte creadas para contexto: {context}")
    return df


def create_food_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea variables agregadas de consumo de alimentos.
    
    Agrega por:
    - Tipo de alimento: carne roja, ave/pescado, marisco
    - Lugar de consumo: restaurante, fastfood, domicilio, casera
    
    Args:
        df: DataFrame con datos de alimentación
        
    Returns:
        DataFrame con nuevas columnas de alimentación agregada
    """
    # Agregación por tipo de alimento
    food_types = {
        "carne_roja": ["carne_roja_restaurante", "carne_roja_fastfood", 
                       "carne_roja_domicilio", "carne_roja_casera"],
        "avepescado": ["avepescado_restaurante", "avepescado_fastfood", 
                       "avepescado_domicilio", "avepescado_casera"],
        "marisco": ["marisco_restaurante", "marisco_domicilio", "marisco_casera"]
    }
    
    for food_type, cols in food_types.items():
        existing_cols = [c for c in cols if c in df.columns]
        if existing_cols:
            df[f"total_{food_type}"] = df[existing_cols].sum(axis=1)
    
    # Agregación por lugar de consumo
    place_types = {
        "restaurante": ["carne_roja_restaurante", "avepescado_restaurante", "marisco_restaurante"],
        "fastfood": ["carne_roja_fastfood", "avepescado_fastfood"],
        "domicilio": ["carne_roja_domicilio", "avepescado_domicilio", "marisco_domicilio"],
        "casera": ["carne_roja_casera", "avepescado_casera", "marisco_casera"]
    }
    
    for place, cols in place_types.items():
        existing_cols = [c for c in cols if c in df.columns]
        if existing_cols:
            df[f"total_{place}"] = df[existing_cols].sum(axis=1)
    
    print("✓ Variables de alimentación creadas")
    return df


def convert_shopping_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte columnas de cantidad de compras a numéricas.
    
    Nota: En futuras versiones de la encuesta, estas variables 
    ya vendrán como enteros desde la fuente.
    
    Args:
        df: DataFrame con datos de compras
        
    Returns:
        DataFrame con columnas de compras numéricas
    """
    shopping_cols = [
        "compras_textiles_cantidad",
        "compras_artesania_cantidad",
        "compras_alimentacion_cantidad",
        "compras_souvenirs_cantidad"
    ]
    
    existing_cols = [col for col in shopping_cols if col in df.columns]
    
    for col in existing_cols:
        # Convertir a numérico, tratando NaN apropiadamente
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    print("✓ Conversión de compras a numéricas completada")
    return df


# %% [markdown]
"""
## 4. Carga y Validación de Datos
"""

# %%
# Cargar datos
df = load_survey_data(INPUT_FILE)

# Validar estructura
validate_data(df)

# Mostrar información básica
print(f"\nInformación del dataset:")
print(f"- Período de datos: {df['Fecha de inicio'].min()} a {df['Fecha de inicio'].max()}")
print(f"- Total de respuestas: {df.shape[0]}")
print(f"- Cuestionarios completos: {(df['Última página'] == CONFIG['complete_survey_last_page']).sum()}")

# %% [markdown]
"""
## 5. Filtrado y Limpieza
"""

# %%
print("Aplicando filtros...")

# Filtrar cuestionarios completos
df_filtered = df[df["Última página"] == CONFIG["complete_survey_last_page"]].copy()
print(f"✓ Cuestionarios completos: {df_filtered.shape[0]}")

# Filtrar visitantes con alojamiento (excluir locales que no pernoctan)
df_filtered = df_filtered[
    df_filtered["alojamiento"] != CONFIG["excluded_accommodation"]
]
print(f"✓ Con alojamiento turístico: {df_filtered.shape[0]}")

# Verificar que quedan datos suficientes
if df_filtered.shape[0] < 10:
    warnings.warn(f"Advertencia: Solo quedan {df_filtered.shape[0]} observaciones después del filtrado")

# %% [markdown]
"""
## 6. Clasificación de Visitantes
"""

# %%
# Clasificar visitor type 1 (procedencia geográfica)
df_filtered["visitor_type_1"] = df_filtered.apply(classify_visitor_type1, axis=1)

print("\nDistribución de Visitor Type 1:")
print(df_filtered["visitor_type_1"].value_counts())
print(f"\nValores faltantes: {df_filtered['visitor_type_1'].isna().sum()}")

# Verificar que la columna se creó correctamente
assert "visitor_type_1" in df_filtered.columns, "Error: visitor_type_1 no se creó"
print(f"✓ Columna visitor_type_1 creada correctamente")

# %%
# Crear variables de transporte
df_filtered = create_transport_variables(df_filtered, "congreso")
df_filtered = create_transport_variables(df_filtered, "ocio")

# Verificar que las columnas de transporte existen
required_transport_cols = [
    "public_transport_use_congreso",
    "car_use_congreso", 
    "walk_bike_use_congreso"
]
for col in required_transport_cols:
    assert col in df_filtered.columns, f"Error: {col} no se creó"

print(f"✓ Todas las columnas de transporte creadas")

# Clasificar visitor type 2 (patrón de transporte)
df_filtered["visitor_type_2"] = df_filtered.apply(classify_visitor_type2, axis=1)

print("\nDistribución de Visitor Type 2:")
print(df_filtered["visitor_type_2"].value_counts())
print(f"\nValores faltantes: {df_filtered['visitor_type_2'].isna().sum()}")

# Verificar que la columna se creó correctamente
assert "visitor_type_2" in df_filtered.columns, "Error: visitor_type_2 no se creó"
print(f"✓ Columna visitor_type_2 creada correctamente")


# %% [markdown]
"""
## 7. Crear Variables Agregadas
"""

# %%
# Variables de alimentación
df_filtered = create_food_variables(df_filtered)

# Variables de compras
df_filtered = convert_shopping_to_numeric(df_filtered)

print("\n✓ Todas las variables agregadas creadas exitosamente")

# %% [markdown]
"""
## 8. Cálculo de Métricas Agregadas
"""

# %%
def calculate_summary_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas agregadas por tipo de visitante.
    
    Args:
        df: DataFrame filtrado con clasificaciones
        
    Returns:
        DataFrame con métricas agregadas
    """
    # Convertir noches_valencia a numérico (excluyendo valores problemáticos)
    df["noches_valencia_num"] = pd.to_numeric(df["noches_valencia"], errors='coerce')
    
    # Convertir dist_km a numérico si no lo es
    if "dist_km" in df.columns:
        df["dist_km_num"] = pd.to_numeric(df["dist_km"], errors='coerce')
        print(f"  ✓ dist_km convertido a numérico: {df['dist_km_num'].notna().sum()} valores válidos")
    else:
        print("  ⚠️ WARNING: dist_km no encontrado en DataFrame")
        df["dist_km_num"] = np.nan
    
    # Agrupar por visitor type 1 y 2
    summary = (
        df.groupby(["visitor_type_1", "visitor_type_2"])
        .agg(
            count_visitors=("visitor_type_1", "size"),
            avg_nights=("noches_valencia_num", "mean"),
            avg_public_transport_congress=("public_transport_use_congreso", "mean"),
            avg_car_congress=("car_use_congreso", "mean"),
            avg_walk_bike_congress=("walk_bike_use_congreso", "mean"),
            avg_public_transport_leisure=("public_transport_use_ocio", "mean"),
            avg_car_leisure=("car_use_ocio", "mean"),
            avg_walk_bike_leisure=("walk_bike_use_ocio", "mean"),
            avg_red_meat=("total_carne_roja", "mean"),
            avg_poultry_fish=("total_avepescado", "mean"),
            avg_seafood=("total_marisco", "mean"),
            avg_restaurant=("total_restaurante", "mean"),
            avg_fastfood=("total_fastfood", "mean"),
            avg_delivery=("total_domicilio", "mean"),
            avg_homemade=("total_casera", "mean"),
            dist_km_congress=("dist_km_num", "mean")  # CAMBIO: Usar dist_km_num y renombrar
        )
        .reset_index()
    )

   
    
 # Calcular porcentajes
    total_visitors = df.shape[0]
    type1_counts = df["visitor_type_1"].value_counts()
    summary["pct_visitor_type_1"] = (
        summary["visitor_type_1"].map(type1_counts) / total_visitors * 100
    ).round(2)
    
    # Porcentaje dentro de cada tipo 1
    summary["pct_visitor_type_2"] = (
        summary.groupby("visitor_type_1")["count_visitors"]
        .transform(lambda x: x / x.sum() * 100)
    ).round(2)
    
    return summary


# Calcular métricas
# Calcular métricas
summary_df = calculate_summary_metrics(df_filtered)

# AÑADIR ESTA VERIFICACIÓN:
print("\n🔍 Verificación de dist_km_congress en summary:")
if "dist_km_congress" in summary_df.columns:
    print(f"  ✓ Columna dist_km_congress creada")
    print(f"  - Valores no-nulos: {summary_df['dist_km_congress'].notna().sum()}")
    print(f"  - Promedio general: {summary_df['dist_km_congress'].mean():.2f}")
else:
    print("  ❌ ERROR: dist_km_congress NO se creó")
    print(f"  Columnas disponibles: {summary_df.columns.tolist()}")

print("\nResumen de métricas calculadas:")
print(summary_df[["visitor_type_1", "visitor_type_2", "count_visitors", 
                  "pct_visitor_type_1", "pct_visitor_type_2"]].to_string())

# %% [markdown]
"""
## 9. Añadir Métricas de Alojamiento
"""

# %%
def add_accommodation_metrics(df: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    """
    Añade métricas promedio de noches por tipo de alojamiento.
    
    Args:
        df: DataFrame filtrado con datos completos
        summary: DataFrame con métricas agregadas
        
    Returns:
        DataFrame summary con columnas de alojamiento
    """
    # Calcular promedio de noches por tipo de alojamiento
    accommodation_avg = (
        df.groupby(["visitor_type_1", "visitor_type_2", "alojamiento"])
        ["noches_valencia_num"]
        .mean()
        .reset_index()
    )
    
    # Pivotar para tener columnas por tipo de alojamiento
    accommodation_pivot = accommodation_avg.pivot(
        index=["visitor_type_1", "visitor_type_2"],
        columns="alojamiento",
        values="noches_valencia_num"
    ).reset_index()
    
    # Renombrar columnas
    accommodation_pivot.columns = [
        f"avg_nights_{col}" if col not in ["visitor_type_1", "visitor_type_2"] else col
        for col in accommodation_pivot.columns
    ]
    
    # Merge con summary
    summary = pd.merge(
        summary,
        accommodation_pivot,
        on=["visitor_type_1", "visitor_type_2"],
        how="left"
    )
    
    print("✓ Métricas de alojamiento añadidas")
    return summary


summary_df = add_accommodation_metrics(df_filtered, summary_df)

def group_accommodation_categories(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa tipos de alojamiento en categorías consolidadas.
    
    Agrupaciones:
    - 
    - Airbnb: Alojamiento local sin coste + Apartamento de alquiler (AirBnb)
    - Hotel 3 estrellas: Hotel 3 estrellas
    - Hotel 4 estrellas: Hotel 4 estrellas
    - Hotel 5 estrellas: Hotel 5 estrellas  
    - Pensión o Hostal: Hotel 2 estrellas + Pensión o hostal
    
    Args:
        summary: DataFrame con métricas de alojamiento individuales
        
    Returns:
        DataFrame con columnas de alojamiento agrupadas
    """
    # Mapeo de columnas originales (ajustar nombres según tus datos reales)
    groupings = {
        "avg_nights_Airbnb": [
            "avg_nights_Alojamiento local sin coste",
            "avg_nights_Apartamento de alquiler (AirBnb)"
        ],
        "avg_nights_Hotel 3 estrellas": [
            "avg_nights_Hotel 3 estrellas"
        ],
        "avg_nights_Hotel 4 estrellas": [
            "avg_nights_Hotel 4 estrellas"
        ],
        "avg_nights_Hotel 5 estrellas": [
            "avg_nights_Hotel 5 estrellas"
        ],
        "avg_nights_Pension o Hostal": [
            "avg_nights_Hotel 2 estrellas",
            "avg_nights_Pensión o hostal"
        ]
    }
    
    # Crear nuevas columnas agrupadas
    for new_col, source_cols in groupings.items():
        # Filtrar columnas que existen en el DataFrame
        existing_cols = [col for col in source_cols if col in summary.columns]
        
        if existing_cols:
            # Sumar/promediar las columnas existentes (usando mean porque son promedios)
            # Si quieres suma ponderada, necesitarías los counts
            summary[new_col] = summary[existing_cols].mean(axis=1)
        else:
            # Si no existen, crear columna con NaN
            summary[new_col] = np.nan
    
    print("✓ Categorías de alojamiento agrupadas")
    print(f"  Nuevas columnas creadas: {list(groupings.keys())}")
    
    return summary

summary_df = group_accommodation_categories(summary_df)
# %% [markdown]
"""
## 10. Añadir Métricas de Compras
"""

# %%
def add_shopping_metrics(df: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    """
    Añade métricas promedio de cantidad de compras por categoría.
    
    Args:
        df: DataFrame filtrado con datos completos
        summary: DataFrame con métricas agregadas
        
    Returns:
        DataFrame summary con columnas de compras
    """
    shopping_cols = [
        "compras_textiles_cantidad",
        "compras_artesania_cantidad",
        "compras_alimentacion_cantidad",
        "compras_souvenirs_cantidad"
    ]
    
    existing_cols = [col for col in shopping_cols if col in df.columns]
    
    if not existing_cols:
        print("⚠ No se encontraron columnas de compras")
        return summary
    
    # Calcular promedios
    shopping_avg = (
        df.groupby(["visitor_type_1", "visitor_type_2"])
        [existing_cols]
        .mean()
        .reset_index()
    )
    
    # Renombrar columnas para consistencia
    rename_dict = {col: f"avg_{col}" for col in existing_cols}
    shopping_avg = shopping_avg.rename(columns=rename_dict)
    
    # Merge con summary
    summary = pd.merge(
        summary,
        shopping_avg,
        on=["visitor_type_1", "visitor_type_2"],
        how="left"
    )
    
    print("✓ Métricas de compras añadidas")
    return summary


summary_df = add_shopping_metrics(df_filtered, summary_df)

# %% [markdown]
"""
## 11. Completar Matriz con Todas las Combinaciones
"""

# %%
def complete_visitor_matrix(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Completa la matriz con todas las combinaciones posibles de visitor types.
    
    Rellena con NaN (no con 0) las combinaciones sin datos para distinguir
    "no hay datos" de "el valor es cero".
    
    Args:
        summary: DataFrame con métricas calculadas
        
    Returns:
        DataFrame con todas las combinaciones posibles
    """
    # Crear MultiIndex con todas las combinaciones
    all_combinations = pd.MultiIndex.from_product(
        [
            CONFIG["visitor_type1_categories"],
            CONFIG["visitor_type2_categories"]
        ],
        names=["visitor_type_1", "visitor_type_2"]
    )
    
    # Reindexar
    summary = summary.set_index(["visitor_type_1", "visitor_type_2"])
    summary = summary.reindex(all_combinations).reset_index()
    
    # Los count_visitors sin datos deberían ser 0
    summary["count_visitors"] = summary["count_visitors"].fillna(0)
    
    # Los porcentajes sin datos deberían ser 0
    summary["pct_visitor_type_1"] = summary["pct_visitor_type_1"].fillna(0)
    summary["pct_visitor_type_2"] = summary["pct_visitor_type_2"].fillna(0)
    
    print("✓ Matriz completada con todas las combinaciones")
    print(f"  Total de combinaciones: {summary.shape[0]}")
    print(f"  Combinaciones con datos: {(summary['count_visitors'] > 0).sum()}")
    
    return summary


summary_df = complete_visitor_matrix(summary_df)

# %% [markdown]
"""
## 12. Reordenar y Formatear Columnas
"""

# %%
# Reordenar columnas para mejor legibilidad
base_cols = [
    "visitor_type_1",
    "visitor_type_2", 
    "count_visitors",
    "pct_visitor_type_1",
    "pct_visitor_type_2",
    "avg_nights",
    "dist_km_congress"
]

transport_cols = [col for col in summary_df.columns if col.startswith("avg_") and "transport" in col or "car" in col or "walk" in col]
food_cols = [col for col in summary_df.columns if any(x in col for x in ["meat", "poultry", "seafood", "restaurant", "fastfood", "delivery", "homemade"])]

# Solo mostrar columnas agrupadas
grouped_accommodation = [
    "avg_nights_Airbnb",
    "avg_nights_Hotel 3 estrellas",
    "avg_nights_Hotel 4 estrellas", 
    "avg_nights_Hotel 5 estrellas",
    "avg_nights_Pension o Hostal"
]
accommodation_cols = [col for col in grouped_accommodation if col in summary_df.columns]

shopping_cols = [col for col in summary_df.columns if "compras" in col]

# Ordenar columnas
ordered_cols = base_cols + transport_cols + food_cols + accommodation_cols + shopping_cols
summary_df = summary_df[[col for col in ordered_cols if col in summary_df.columns]]

# Redondear valores numéricos
numeric_cols = summary_df.select_dtypes(include=[np.number]).columns
summary_df[numeric_cols] = summary_df[numeric_cols].round(2)

print("✓ Columnas reordenadas y formateadas")
print(f"\nColumnas finales: {summary_df.shape[1]}")

# %% [markdown]
"""
## 13. Validación Final y Estadísticas
"""

# %%
print("=" * 60)
print("RESUMEN FINAL DEL PROCESAMIENTO")
print("=" * 60)

print(f"\n📊 Datos procesados:")
print(f"  - Respuestas iniciales: {df.shape[0]}")
print(f"  - Respuestas filtradas: {df_filtered.shape[0]}")
print(f"  - Tasa de filtrado: {(1 - df_filtered.shape[0]/df.shape[0])*100:.1f}%")

print(f"\n👥 Distribución de visitantes:")
for vtype in CONFIG["visitor_type1_categories"]:
    count = (summary_df["visitor_type_1"] == vtype).sum()
    total_visitors = summary_df[summary_df["visitor_type_1"] == vtype]["count_visitors"].sum()
    print(f"  - {vtype}: {int(total_visitors)} visitantes ({count} subcategorías)")

print(f"\n📈 Métricas calculadas:")
print(f"  - Promedio de noches (general): {df_filtered['noches_valencia_num'].mean():.2f}")
print(f"  - Uso promedio transporte público: {df_filtered['public_transport_use_congreso'].mean():.2f}")
print(f"  - Uso promedio coche: {df_filtered['car_use_congreso'].mean():.2f}")
print(f"  - Uso promedio bici/pie: {df_filtered['walk_bike_use_congreso'].mean():.2f}")

if 'dist_km_num' in df_filtered.columns:
    print(f"  - Distancia promedio al congreso: {df_filtered['dist_km_num'].mean():.2f} km")

print(f"\n✓ Procesamiento completado exitosamente")

# Mostrar primeras filas del resultado
print("\n" + "=" * 60)
print("VISTA PREVIA DEL RESULTADO")
print("=" * 60)
display(summary_df.head(10))

# %% [markdown]
"""
## 14. Exportación de Resultados
"""

# %%
def export_results(summary: pd.DataFrame, full_data: pd.DataFrame, output_path: Path) -> None:
    """
    Exporta resultados a Excel con múltiples hojas.
    
    Args:
        summary: DataFrame con métricas agregadas
        full_data: DataFrame con todos los datos transformados
        output_path: Ruta del archivo de salida
    """
    # Crear directorio si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Hoja 1: Resumen agregado
        summary.to_excel(writer, sheet_name="visitor_summary", index=False)
        
        # Hoja 2: Datos completos transformados
        full_data.to_excel(writer, sheet_name="full_data", index=False)
        
        # Hoja 3: Metadata
        metadata = pd.DataFrame({
            "Metric": [
                "Date Processed",
                "Total Responses",
                "Filtered Responses",
                "Visitor Type 1 Categories",
                "Visitor Type 2 Categories",
                "Complete Survey Last Page"
            ],
            "Value": [
                pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                df.shape[0],
                full_data.shape[0],
                ", ".join(CONFIG["visitor_type1_categories"]),
                ", ".join(CONFIG["visitor_type2_categories"]),
                CONFIG["complete_survey_last_page"]
            ]
        })
        metadata.to_excel(writer, sheet_name="metadata", index=False)
    
    print(f"\n✓ Resultados exportados a: {output_path}")
    print(f"  - Hojas creadas: visitor_summary, full_data, metadata")


# Exportar
export_results(summary_df, df_filtered, OUTPUT_FILE)

print("\n" + "=" * 60)
print("PIPELINE COMPLETADO")
print("=" * 60)
