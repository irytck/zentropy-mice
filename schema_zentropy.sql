-- schema_zentropy.sql
-- Inicial schema para Proyecto Zentropy MICE (Postgres + TimescaleDB)

CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis; -- opcional, quitar si no necesitas geom

CREATE TABLE unit (
  unit_id SERIAL PRIMARY KEY,
  unit_code TEXT UNIQUE NOT NULL,
  description TEXT,
  si_equivalent_factor NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE lookup_measure (
  measure_id SERIAL PRIMARY KEY,
  measure_key TEXT UNIQUE NOT NULL,
  description TEXT,
  formula TEXT,
  default_unit_id INT REFERENCES unit(unit_id),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE congress (
  congress_id SERIAL PRIMARY KEY,
  code TEXT UNIQUE,
  name TEXT NOT NULL,
  start_date DATE,
  end_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE event (
  event_id SERIAL PRIMARY KEY,
  congress_id INT REFERENCES congress(congress_id) ON DELETE CASCADE,
  event_date DATE NOT NULL,
  name TEXT,
  start_ts TIMESTAMPTZ,
  end_ts TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE participant (
  participant_id BIGSERIAL PRIMARY KEY,
  anon_id TEXT UNIQUE NOT NULL,
  country_iso CHAR(2),
  age INTEGER,
  sex TEXT,
  profession TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE survey_response (
  response_id BIGSERIAL PRIMARY KEY,
  congress_id INT REFERENCES congress(congress_id) ON DELETE CASCADE,
  participant_id BIGINT REFERENCES participant(participant_id) ON DELETE SET NULL,
  submitted_at TIMESTAMPTZ NOT NULL,
  question_code TEXT NOT NULL,
  answer_text TEXT,
  answer_numeric NUMERIC,
  unit_id INT REFERENCES unit(unit_id),
  source_file TEXT,
  ingest_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE trip (
  trip_id BIGSERIAL PRIMARY KEY,
  participant_id BIGINT REFERENCES participant(participant_id),
  congress_id INT REFERENCES congress(congress_id),
  origin_city TEXT,
  origin_country_iso CHAR(2),
  mode TEXT,
  distance_km NUMERIC,
  co2_kg NUMERIC,
  energy_kwh_equiv NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE poi (
  poi_id SERIAL PRIMARY KEY,
  name TEXT,
  poi_type TEXT,
  geom GEOMETRY(POINT, 4326),
  address TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE consumption_item (
  item_id BIGSERIAL PRIMARY KEY,
  event_id INT REFERENCES event(event_id),
  congress_id INT REFERENCES congress(congress_id),
  participant_id BIGINT REFERENCES participant(participant_id),
  poi_id INT REFERENCES poi(poi_id),
  category TEXT,
  description TEXT,
  quantity NUMERIC,
  unit_id INT REFERENCES unit(unit_id),
  estimated_kg NUMERIC,
  source TEXT,
  ingest_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sensor (
  sensor_id SERIAL PRIMARY KEY,
  sensor_code TEXT UNIQUE NOT NULL,
  location TEXT,
  measurement_type TEXT,
  unit_id INT REFERENCES unit(unit_id),
  freq_seconds INT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE bms_timeseries (
  ts_id BIGSERIAL PRIMARY KEY,
  sensor_id INT REFERENCES sensor(sensor_id) ON DELETE CASCADE,
  ts TIMESTAMPTZ NOT NULL,
  value NUMERIC,
  quality_flag TEXT,
  ingest_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

SELECT create_hypertable('bms_timeseries', 'ts', if_not_exists => TRUE);

CREATE TABLE entropy_metric (
  metric_id BIGSERIAL PRIMARY KEY,
  congress_id INT REFERENCES congress(congress_id),
  event_id INT REFERENCES event(event_id),
  computed_at TIMESTAMPTZ DEFAULT now(),
  scale TEXT NOT NULL,
  flow TEXT NOT NULL,
  metric_key TEXT,
  metric_value NUMERIC,
  unit_id INT REFERENCES unit(unit_id),
  metadata JSONB
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
