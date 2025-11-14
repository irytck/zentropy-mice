# Arquitectura y ERD (Zentropy MICE)

Resumen:
- DB: PostgreSQL + TimescaleDB (series temporales BMS).
- Tablas principales: unit, lookup_measure, congress, event, participant, survey_response, trip, consumption_item, sensor, bms_timeseries, entropy_metric, dataset_ingest.
- Pipelines: raw -> staging -> curated -> calculator.
- Calculadora: módulo Python que ingiere tablas agregadas y devuelve métricas por escala (user/event/congress/building/city).

ERD (breve, actualizar con diagrama generado):
- congress 1—N event
- participant 1—N survey_response
- sensor 1—N bms_timeseries
- event 1—N consumption_item

Ingest & ETL:
- survey: ingestion CSV/XLSX -> validation -> clean -> insert into participant + survey_response + trip + consumption_item.
- bms: ingestion -> resample -> aggregates -> store in bms_timeseries.

Entregables y próximos pasos:
- completar definiciones de variables del bus y sensores.
- formalizar funciones de la calculadora (S_energy, S_material, S_information), pesos y normalizaciones.

