# Zentropy MICE — Data & Calculadora

Resumen rápido:
- Proyecto: medir entropía socioeconómica de eventos MICE en Valencia.
- Estado: esquema DB creado (schema_zentropy.sql), notebooks y scripts ETL iniciales, calculadora MVP basada en Excel convertida a script Python.
- Cómo levantar (local con Colima + Docker CLI):
  1. `colima start`
  2. `docker compose up -d`
  3. `cat schema_zentropy.sql | docker compose exec -T db psql -U zentropy -d zentropy`
- Estructura del repo: `notebooks/`, `src/etl/`, `src/calculator/`, `schema_zentropy.sql`, `docker-compose.yml`.
- Importante: no subir datos sensibles. Usa `.env` para credenciales (no commit).

Próximos pasos:
1. Finalizar ETL encuesta → cargar en `participant`, `survey_response`, `trip`, `consumption_item`.
2. Definir sensores y métricas.
3. Formalizar fórmulas de la calculadora e implementar en `src/calculator/`.
4. Tests (pytest) y Great Expectations para validación.

Contacto: Iuliia Rytck irytck@upv.edu.es
