"""
ETL 00 — Survey CLEAN
Proyecto: Zentropy MICE
Objetivo:
- Limpiar encuesta completa
- Renombrar columnas largas a nombres canónicos
- Tipar correctamente los datos
- Eliminar basura técnica
- Calcular distancia observada alojamiento → PdC
- Generar datasets RAW_NORMALIZED y CLEAN en CSV
"""

import pandas as pd
import numpy as np
from pathlib import Path
from unidecode import unidecode
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

INPUT_FILE = "results-survey798946-4.xlsx"

BASE_DIR = Path("etl")
RAW_DIR = BASE_DIR / "raw"
CLEAN_DIR = BASE_DIR / "clean"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

RAW_OUT = RAW_DIR / "survey_v2_raw_normalized.csv"
CLEAN_OUT = CLEAN_DIR / "survey_v2_clean.csv"
SCHEMA_OUT = CLEAN_DIR / "survey_v2_clean_schema.txt"

# Palacio de Congresos de Valencia
PDC_LAT = 39.496239
PDC_LON = -0.402092

# =====================================================
# HELPERS
# =====================================================

def normalize_col(col: str) -> str:
    col = unidecode(col)
    col = col.lower()
    for ch in ["¿", "?", "(", ")", ".", ",", ":", ";"]:
        col = col.replace(ch, "")
    col = col.replace("/", "_").replace(" ", "_")
    col = col.replace("__", "_")
    return col.strip("_")


def haversine_km(lat1, lon1, lat2, lon2):
    if pd.isna(lat1) or pd.isna(lon1):
        return np.nan
    r = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


# =====================================================
# RENAME MAP (CONTRATO CLEAN)
# =====================================================

RENAME_MAP = {

    # ---------- META ----------
    "id_de_respuesta": "meta_response_id",
    "fecha_de_envio": "meta_submitted_at",
    "ultima_pagina": "meta_last_page",
    "lenguaje_inicial": "meta_language",
    "fecha_de_inicio": "meta_started_at",
    "fecha_de_la_ultima_accion": "meta_last_action_at",
    "tiempo_total": "meta_total_time_sec",

    # ---------- PERFIL ----------
    "indica_por_favor_su_lugar_de_residencia_habitual": "profile_residence_type",
    "indique_provincia": "profile_province",
    "indique_pais_de_residencia": "profile_country",
    "en_que_rango_de_edad_se_encuentra": "profile_age_range",
    "cual_es_su_genero": "profile_gender",
    "cual_es_su_genero_otro": "profile_gender_other",
    "cual_fue_su_rol_en_el_congreso": "profile_congress_role",

    # ---------- ESTANCIA ----------
    "cuantas_noches_en_total_se_quedo_en_valencia": "stay_nights",
    "que_tipo_de_alojamiento_utilizo_durante_su_estancia_en_caso_de_haber_pernoctado_fuera_de_su_domicilio_habitual":
        "stay_accommodation_type",
    "podria_indicarnos_donde_se_hospedo_durante_su_estancia_en_valencia":
        "stay_accommodation_location",

    # ---------- MOVILIDAD URBANA ----------
    # Taxi
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_taxi_o_vtc_cabify_uber_para_asistir_al_congreso":
        "mob_taxi_congreso",
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_taxi_o_vtc_cabify_uber_para_actividades_fuera_del_congreso":
        "mob_taxi_ocio",

    # Bus
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_autobus_para_asistir_al_congreso":
        "mob_bus_congreso",
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_autobus_para_actividades_fuera_del_congreso":
        "mob_bus_ocio",

    # Metro
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_metrotranvia_para_asistir_al_congreso":
        "mob_metro_congreso",
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_metrotranvia_para_actividades_fuera_del_congreso":
        "mob_metro_ocio",

    # Coche
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_coche_de_combustion_para_asistir_al_congreso":
        "mob_car_combustion_congreso",
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_coche_de_combustion_para_actividades_fuera_del_congreso":
        "mob_car_combustion_ocio",

    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_coche_electrico_para_asistir_al_congreso":
        "mob_car_electric_congreso",
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_coche_electrico_para_actividades_fuera_del_congreso":
        "mob_car_electric_ocio",

    # Activa
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_bicicletapatinetea_pie_para_asistir_al_congreso":
        "mob_active_congreso",
    "cuantas_veces_utilizo_cada_uno_de_los_siguientes_medios_de_transporte_durante_su_estancia_en_valencia_para_1_asistir_al_congreso_2_realizar_actividades_fuera_del_congreso_ocio_turismo_cenas_etc_bicicletapatinetea_pie_para_actividades_fuera_del_congreso":
        "mob_active_ocio",
}

# =====================================================
# ETL PIPELINE
# =====================================================

def run():

    df = pd.read_excel(INPUT_FILE)

    # ---------- NORMALIZE COLUMN NAMES ----------
    df.columns = [normalize_col(c) for c in df.columns]

    # ---------- SAVE RAW NORMALIZED ----------
    df.to_csv(RAW_OUT, index=False)

    # ---------- DROP TEMPORAL / TECH COLUMNS ----------
    df = df[[c for c in df.columns if not c.startswith("temporizacion")]]

    # ---------- FILTER COMPLETED SURVEYS ----------
    if "meta_last_page" in df.columns:
        df = df[df["meta_last_page"].notna()]

    # ---------- RENAME SEMANTIC ----------
    df = df.rename(columns=RENAME_MAP)

    # ---------- TYPE CASTING ----------
    INT_COLS = [c for c in df.columns if c.startswith(("mob_", "food_", "shop_")) or c == "stay_nights"]
    for col in INT_COLS:
        df[col] = df[col].fillna(0).astype(int)

    # ---------- DISTANCE CALC ----------
    if "stay_accommodation_location" in df.columns:
        # espera columnas lat / lon ya extraídas o geocodificadas en pasos previos
        if "stay_lat" in df.columns and "stay_lon" in df.columns:
            df["dist_alojamiento_pdc_km"] = df.apply(
                lambda r: haversine_km(r["stay_lat"], r["stay_lon"], PDC_LAT, PDC_LON),
                axis=1
            )
            df["has_observed_distance"] = df["dist_alojamiento_pdc_km"].notna().astype(int)
        else:
            df["dist_alojamiento_pdc_km"] = np.nan
            df["has_observed_distance"] = 0

    # ---------- FINAL CLEAN ----------
    df.to_csv(CLEAN_OUT, index=False)

    # ---------- SAVE SCHEMA ----------
    with open(SCHEMA_OUT, "w") as f:
        for c in df.columns:
            f.write(f"{c}\n")

    print("CLEAN SURVEY GENERATED")
    print(f"RAW:   {RAW_OUT}")
    print(f"CLEAN: {CLEAN_OUT}")
    print(f"SCHEMA:{SCHEMA_OUT}")


if __name__ == "__main__":
    run()
