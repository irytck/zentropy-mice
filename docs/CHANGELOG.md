# Changelog

## [Unreleased]

### Added
- Preparación de scripts ETL para generación de entidades y eventos
  a partir de survey CLEAN.

### Changed
- Documentación afinada para reflejar el estado “ready to ingest”.

---

## [2025-12-19]

### Added
- Arquitectura explícita RAW → CLEAN → EVENTS → CALCULATION.
- Tabla `participant_transport_event` como unidad mínima de movilidad urbana.
- Script `00_survey_clean.py` para limpieza completa de encuesta v2.
- Convención semántica de columnas (mob_, stay_, profile_, etc.).

### Changed
- `participant` redefinida como entidad mínima (sin respuestas de encuesta).
- Sustitución del enfoque basado en tablas de respuestas por generación de eventos.

### Removed
- Uso implícito de tablas `survey_response` y `trip` en la fase actual del modelo.
- Abandono del modelo basado en `participant_transport_km`.

---

## [2025-12-02]

### Added
- Esquema SQL inicial y entorno Docker (PostgreSQL).
- Primeras pruebas de notebooks de limpieza y cálculo de emisiones.
- Modelo físico inicial de energía de transporte (kJ-based).

### Changed
- Deprecación inicial de la tabla `trip` para cálculos diarios de transporte.

