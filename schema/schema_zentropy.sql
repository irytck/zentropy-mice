-- schema_zentropy.sql
-- Inicial schema para Proyecto Zentropy MICE (Postgres + TimescaleDB)

CREATE TABLE participant (
    participant_id      SERIAL PRIMARY KEY,
    survey_id            TEXT UNIQUE, --trazabilidad con RAW
    congress_id          INTEGER NOT NULL, --para comparar Cs0 y Cs1
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transport_context (
    context_id   SERIAL PRIMARY KEY,
    context_code TEXT UNIQUE NOT NULL, -- 'congreso', 'ocio'
    description  TEXT
);

CREATE TABLE transport_vehicle (
    vehicle_id      SERIAL PRIMARY KEY,
    vehicle_code    TEXT UNIQUE NOT NULL, -- bus, car, metro, taxi, bike, walk
    energy_type     TEXT NOT NULL,         -- electricity, diesel, gasoil, human
    is_motorized    BOOLEAN NOT NULL
);

CREATE TABLE transport_distance_method (
    method_code TEXT PRIMARY KEY,  -- observed, poi_based, average, synthetic
    description TEXT
);

CREATE TABLE transport_energy_factor (
  energy_type TEXT PRIMARY KEY,
  kj_per_unit NUMERIC NOT NULL,
  unit TEXT NOT NULL
);

CREATE TABLE participant_transport_event ( --Tabla central: evento de movilidad urbana
    transport_event_id  SERIAL PRIMARY KEY,

    participant_id      INTEGER NOT NULL
        REFERENCES participant(participant_id),

    vehicle_id          INTEGER NOT NULL
        REFERENCES transport_vehicle(vehicle_id),

    context_id          INTEGER NOT NULL
        REFERENCES transport_context(context_id),

    distance_km         NUMERIC(8,3) NOT NULL CHECK (distance_km >= 0),

    distance_method     TEXT NOT NULL
        REFERENCES transport_distance_method(method_code),

    data_source         TEXT NOT NULL,  -- survey, inferred, synthetic
    assumption_flag     BOOLEAN DEFAULT FALSE,

    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dataset_ingest (
  ingest_id TEXT PRIMARY KEY,
  source TEXT,
  file_name TEXT,
  rows_ingested BIGINT,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  status TEXT,
  notes TEXT
);

------------------------------------------------------------------------------------------------
INSERT INTO transport_context (context_code, description)
VALUES
('congreso', 'Desplazamientos urbanos para asistir al congreso'),
('ocio', 'Desplazamientos urbanos para ocio, turismo o actividades sociales');

INSERT INTO transport_distance_method (method_code, description)
VALUES
('observed',  'Distancia declarada u observada directamente'),
('average',   'Distancia media asumida por metodología'),
('poi_based', 'Estimación basada en POIs (origen-destino)'),
('synthetic', 'Distancia generada mediante modelo sintético');

INSERT INTO transport_vehicle (vehicle_code, energy_type, is_motorized)
VALUES
-- Transporte público
('bus',    'diesel',      TRUE),
('metro',  'electricity', TRUE),
('taxi',   'diesel',      TRUE),

-- Transporte privado
('car_combustion',    'fuel',      TRUE),
('car_electric', 'electricity', TRUE),

-- Movilidad activa
('bike',   'human',       FALSE),
('walk',   'human',       FALSE);

INSERT INTO transport_energy_factor (energy_type, kj_per_unit, unit)
VALUES
('diesel',      38000, 'kJ/l'),
('fuel',        34780, 'kJ/l' ),
('electricity', 3600,  'kJ/kWh'),
('human',       1,     'kJ/km'); -- placeholder metabólico



------------------------------------------------------------------------------------------------
-- FASE DEL CÁLCULO (NO EJECUTAR AHORA)
-- CREATE TABLE participant_transport_energy (
--   pte_id BIGSERIAL PRIMARY KEY,
--   participant_id BIGINT REFERENCES participant(participant_id),
--   congress_id INT REFERENCES congress(congress_id),
--   energy_kj NUMERIC NOT NULL,
--   computed_at TIMESTAMPTZ DEFAULT now(),
--   metadata JSONB
-- );

