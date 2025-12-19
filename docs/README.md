# Zentropy MICE — Data & Calculadora

## Resumen
Proyecto para medir y analizar la entropía socioeconómica del turismo MICE en Valencia,
a partir de datos de encuesta, flujos urbanos y modelos físicos de energía.

El sistema está diseñado por capas explícitas:
RAW → CLEAN → EVENTS → CALCULATION.

---

## Estado actual

- Modelo relacional base definido para la dimensión usuario y movilidad urbana
  (`participant`, `participant_transport_event` y tablas de referencia).
- Pipeline ETL de encuesta diseñado y preparado hasta la capa CLEAN.
- Script de limpieza (`00_survey_clean.py`) listo para ejecución cuando se disponga
  de datos reales de encuesta.
- Arquitectura preparada para la generación posterior de eventos y cálculos físicos.

Actualmente **no se han cargado datos reales**, por diseño.

---

## Data & Calculation Architecture

- La capa CLEAN de encuesta actúa como contrato estable entre la encuesta y el modelo relacional.
- Los eventos de movilidad se generan en la tabla `participant_transport_event`.
- El cálculo energético se basa en dichos eventos y en factores definidos en tablas físicas.

Modelo de energía de transporte:
[`docs/transport_energy_model.md`](docs/transport_energy_model.md)

---

## Próximos pasos

1. Ejecutar `00_survey_clean.py` cuando se disponga del Excel real de encuesta.
2. Generar la tabla `participant` a partir del survey CLEAN.
3. Generar eventos de movilidad en `participant_transport_event`.
4. Validar distribuciones de uso de transporte y distancias (QA).
5. Implementar el cálculo de energía de transporte.



Contacto: Iuliia Rytck irytck@upv.edu.es
