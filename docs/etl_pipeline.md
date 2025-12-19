# ETL Pipeline — Survey Data (Zentropy MICE)

Este documento describe el **proceso ETL completo** para transformar los datos de la encuesta de congresistas en **datasets estructurados y trazables**, listos para alimentar:

- la calculadora de energía y emisiones,
- los modelos de entropía,
- la base de datos relacional Zentropy.

El pipeline está diseñado para ser **reproducible, escalable y auditable**.

---

## 1. Objetivo del ETL

Transformar las respuestas de la encuesta (formato crudo y heterogéneo) en:

- datos agregados por participante,
- flujos cuantificables (energía, emisiones),
- tablas de entrada coherentes con el modelo físico-relacional.

El ETL **no calcula entropía**, solo prepara los flujos.

---

## 2. Fuentes de datos (Input)

### 2.1 Encuesta de congresistas

- Formato original: Excel / CSV
- Granularidad: una fila por respuesta
- Contenido:
  - perfil del participante,
  - movilidad intraurbana,
  - alojamiento,
  - alimentación,
  - compras,
  - actividades.

### 2.2 Tablas auxiliares (no encuesta)

- `transport_vehicle`
- `transport_energy_factor`
- factores de emisión (si aplica)
- tablas de mapeo (survey → categorías físicas)

---

## 3. Estructura general del pipeline

El ETL se divide en **cuatro capas lógicas**:

## ETL Pipeline (estado actual)

Encuesta:
RAW (Excel original)
→ CLEAN (CSV contractual, normalizado)
→ EVENTS (participant, participant_transport_event)
→ CALCULATION (energía, entropía)

La capa CLEAN es el contrato estable entre encuesta y modelo.
La tabla `participant` NO contiene respuestas de encuesta.
Las respuestas se proyectan en tablas de eventos por dominio.

---

## 4. RAW layer — datos originales

### Características
- Datos sin modificar.
- Columnas originales de la encuesta.
- Valores nulos, inconsistencias y textos libres.

### Acciones
- Lectura del fichero original.
- Registro del ingest (`dataset_ingest`).
- No se aplican transformaciones.

**Nunca se sobreescribe el RAW**.

---

## 5. CLEAN layer — limpieza y normalización

### 5.1 Normalización de columnas
- Renombrar columnas a `snake_case`.
- Unificar idiomas y etiquetas.
- Conversión explícita de tipos:
  - fechas → `datetime`,
  - contadores → `int`,
  - distancias → `float`.

### 5.2 Limpieza de valores
- Valores vacíos → `NULL` o `0` según semántica.
- Normalización de categorías:
  - transporte (`bus`, `metro`, `taxi`, etc.),
  - alojamiento,
  - tipos de comida.

### 5.3 Parsing de campos complejos
- Coordenadas (`lat;lon`) → columnas separadas.
- Campos multirespuesta → columnas auxiliares o tablas long.

### Output
- Dataset limpio, misma granularidad que la encuesta.
- Sin cálculos físicos.

---

## 6. EVENTS layer 

### 6.2 Transformaciones clave

#### A. Movilidad

#### B. Alimentación

#### C. Compras

#### D. Alojamiento

## 7. CALCULATOR-READY layer — modelo físico

Esta capa adapta los datos agregados al **modelo físico-relacional**.

### 7.1 Transporte diario

#### Paso 1 — Cálculo de km por modo
Ejemplo:
km_bus = uso_bus_congreso * dist_km_alojamiento_congreso
+ uso_bus_ocio * dist_km_medio_ocio

La estimación de dist_km_ocio se documenta como supuesto metodológico y puede basarse en POIs visitados o valores medios por defecto, según disponibilidad de datos.

#### Paso 2 — Determinación del tipo de vehículo

Se usa una tabla de mapeo:

| survey_mode | vehicle_type |
|------------|--------------|
| bus        | bus_combustion |
| metro      | metro |
| taxi       | taxi_combustion |
| car        | car_combustion |

#### Paso 3 — Conversión a formato long

Tabla final de entrada para la calculadora:

| participant_id | vehicle_type | km |
|----------------|--------------|----|
| 1              | bus_combustion | 5 |
| 1              | car_electric   | 15 |

Esta tabla alimenta directamente `participant_transport_km`.

---

## 8. Carga en base de datos (Load)

### Tablas destino
- `participant`
- `participant_transport_km`
- (opcional) `consumption_item`

### Principios
- Inserts idempotentes (control por `ingest_id`).
- Separación clara entre:
  - datos observados,
  - datos derivados.

---

## 9. Control de calidad y validaciones

### Validaciones mínimas
- km ≥ 0
- noches ≥ 0
- coherencia entre:
  - tipo de alojamiento y noches,
  - transporte y distancias.

### Flags
- registros con supuestos → metadata JSON.
- valores imputados → documentados.

---

## 10. Trazabilidad y reproducibilidad

Cada ejecución del ETL debe registrar:
- fuente del archivo,
- timestamp,
- número de filas procesadas,
- versión del modelo.

Esto permite:
- recalcular con nuevos factores,
- auditar resultados,
- comparar congresos.

---

## 11. Relación con la calculadora

El ETL **no calcula energía ni emisiones**.

Produce:
- flujos físicos listos (`km por vehículo`).

La calculadora:
- aplica factores físicos,
- genera energía, emisiones y entropía.

---

## 12. Pendientes identificados

- Definición definitiva de distancias ocio.
- Inclusión futura de actividades.
- Tests automatizados del pipeline.

---

## 13. Resumen

Este ETL:
- convierte encuesta → flujos físicos,
- separa datos de ciencia,
- garantiza escalabilidad y rigor,
- es compatible con SQL, Python y modelos de entropía.

Es la base del sistema Zentropy MICE.

See `docs/transport_energy_model.md` for the physical energy model.


