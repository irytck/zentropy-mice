# Arquitectura y ERD (Zentropy MICE)

## Estado actual del sistema (19-12-2025)

Este documento describe la arquitectura **real implementada** a fecha de hoy.
El sistema se construye por capas explícitas:

RAW → CLEAN → EVENTS → CALCULATION.

La capa CLEAN actúa como contrato estable entre la encuesta y el modelo relacional,
y es la única fuente permitida para la generación de entidades y eventos.

---

### Modelo relacional (fase actual)

El modelo relacional actual cubre la **dimensión usuario y movilidad urbana**.
Otras dimensiones (materia, información, ciudad, edificio) se incorporarán en fases posteriores.

Tablas implementadas y activas:

- **participant**  
  Identidad mínima del congresista encuestado.

- **participant_transport_event**  
  Unidad mínima de movilidad urbana (usuario × modo × contexto).

- **transport_vehicle**  
- **transport_context**  
- **transport_distance_method**  
- **transport_energy_factor**  

- **dataset_ingest**  
  Trazabilidad de cargas y procesos ETL.

---

### ERD (simplificado)

participant 1—N participant_transport_event  
participant_transport_event N—1 transport_vehicle  
participant_transport_event N—1 transport_context  

Las métricas energéticas y entrópicas se calculan a partir de estos eventos
y no forman parte todavía del modelo persistente.

