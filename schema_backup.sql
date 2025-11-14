--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17
-- Dumped by pg_dump version 14.17

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: timescaledb; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS timescaledb WITH SCHEMA public;


--
-- Name: EXTENSION timescaledb; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION timescaledb IS 'Enables scalable inserts and complex queries for time-series data (Community Edition)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bms_timeseries; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.bms_timeseries (
    ts_id bigint NOT NULL,
    sensor_id integer,
    ts timestamp with time zone NOT NULL,
    value numeric,
    quality_flag text,
    ingest_id text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.bms_timeseries OWNER TO zentropy;

--
-- Name: bms_timeseries_ts_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.bms_timeseries_ts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bms_timeseries_ts_id_seq OWNER TO zentropy;

--
-- Name: bms_timeseries_ts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.bms_timeseries_ts_id_seq OWNED BY public.bms_timeseries.ts_id;


--
-- Name: congress; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.congress (
    congress_id integer NOT NULL,
    code text,
    name text NOT NULL,
    start_date date,
    end_date date,
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.congress OWNER TO zentropy;

--
-- Name: congress_congress_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.congress_congress_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.congress_congress_id_seq OWNER TO zentropy;

--
-- Name: congress_congress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.congress_congress_id_seq OWNED BY public.congress.congress_id;


--
-- Name: dataset_ingest; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.dataset_ingest (
    ingest_id text NOT NULL,
    source text,
    file_name text,
    rows_ingested bigint,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    status text,
    notes text
);


ALTER TABLE public.dataset_ingest OWNER TO zentropy;

--
-- Name: entropy_metric; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.entropy_metric (
    metric_id bigint NOT NULL,
    congress_id integer,
    event_id integer,
    computed_at timestamp with time zone DEFAULT now(),
    scale text NOT NULL,
    flow text NOT NULL,
    metric_key text,
    metric_value numeric,
    unit_id integer,
    metadata jsonb
);


ALTER TABLE public.entropy_metric OWNER TO zentropy;

--
-- Name: entropy_metric_metric_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.entropy_metric_metric_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.entropy_metric_metric_id_seq OWNER TO zentropy;

--
-- Name: entropy_metric_metric_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.entropy_metric_metric_id_seq OWNED BY public.entropy_metric.metric_id;


--
-- Name: event; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.event (
    event_id integer NOT NULL,
    congress_id integer,
    event_date date NOT NULL,
    name text,
    start_ts timestamp with time zone,
    end_ts timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.event OWNER TO zentropy;

--
-- Name: event_event_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.event_event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_event_id_seq OWNER TO zentropy;

--
-- Name: event_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.event_event_id_seq OWNED BY public.event.event_id;


--
-- Name: lookup_measure; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.lookup_measure (
    measure_id integer NOT NULL,
    measure_key text NOT NULL,
    description text,
    formula text,
    default_unit_id integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.lookup_measure OWNER TO zentropy;

--
-- Name: lookup_measure_measure_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.lookup_measure_measure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lookup_measure_measure_id_seq OWNER TO zentropy;

--
-- Name: lookup_measure_measure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.lookup_measure_measure_id_seq OWNED BY public.lookup_measure.measure_id;


--
-- Name: participant; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.participant (
    participant_id bigint NOT NULL,
    anon_id text NOT NULL,
    country_iso character(2),
    age integer,
    sex text,
    profession text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.participant OWNER TO zentropy;

--
-- Name: participant_participant_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.participant_participant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.participant_participant_id_seq OWNER TO zentropy;

--
-- Name: participant_participant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.participant_participant_id_seq OWNED BY public.participant.participant_id;


--
-- Name: sensor; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.sensor (
    sensor_id integer NOT NULL,
    sensor_code text NOT NULL,
    location text,
    measurement_type text,
    unit_id integer,
    freq_seconds integer,
    meta jsonb,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.sensor OWNER TO zentropy;

--
-- Name: sensor_sensor_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.sensor_sensor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sensor_sensor_id_seq OWNER TO zentropy;

--
-- Name: sensor_sensor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.sensor_sensor_id_seq OWNED BY public.sensor.sensor_id;


--
-- Name: survey_response; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.survey_response (
    response_id bigint NOT NULL,
    congress_id integer,
    participant_id bigint,
    submitted_at timestamp with time zone NOT NULL,
    question_code text NOT NULL,
    answer_text text,
    answer_numeric numeric,
    unit_id integer,
    source_file text,
    ingest_id text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.survey_response OWNER TO zentropy;

--
-- Name: survey_response_response_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.survey_response_response_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.survey_response_response_id_seq OWNER TO zentropy;

--
-- Name: survey_response_response_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.survey_response_response_id_seq OWNED BY public.survey_response.response_id;


--
-- Name: trip; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.trip (
    trip_id bigint NOT NULL,
    participant_id bigint,
    congress_id integer,
    origin_city text,
    origin_country_iso character(2),
    mode text,
    distance_km numeric,
    co2_kg numeric,
    energy_kwh_equiv numeric,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.trip OWNER TO zentropy;

--
-- Name: trip_trip_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.trip_trip_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trip_trip_id_seq OWNER TO zentropy;

--
-- Name: trip_trip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.trip_trip_id_seq OWNED BY public.trip.trip_id;


--
-- Name: unit; Type: TABLE; Schema: public; Owner: zentropy
--

CREATE TABLE public.unit (
    unit_id integer NOT NULL,
    unit_code text NOT NULL,
    description text,
    si_equivalent_factor numeric,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.unit OWNER TO zentropy;

--
-- Name: unit_unit_id_seq; Type: SEQUENCE; Schema: public; Owner: zentropy
--

CREATE SEQUENCE public.unit_unit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.unit_unit_id_seq OWNER TO zentropy;

--
-- Name: unit_unit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: zentropy
--

ALTER SEQUENCE public.unit_unit_id_seq OWNED BY public.unit.unit_id;


--
-- Name: bms_timeseries ts_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.bms_timeseries ALTER COLUMN ts_id SET DEFAULT nextval('public.bms_timeseries_ts_id_seq'::regclass);


--
-- Name: congress congress_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.congress ALTER COLUMN congress_id SET DEFAULT nextval('public.congress_congress_id_seq'::regclass);


--
-- Name: entropy_metric metric_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.entropy_metric ALTER COLUMN metric_id SET DEFAULT nextval('public.entropy_metric_metric_id_seq'::regclass);


--
-- Name: event event_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.event ALTER COLUMN event_id SET DEFAULT nextval('public.event_event_id_seq'::regclass);


--
-- Name: lookup_measure measure_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.lookup_measure ALTER COLUMN measure_id SET DEFAULT nextval('public.lookup_measure_measure_id_seq'::regclass);


--
-- Name: participant participant_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.participant ALTER COLUMN participant_id SET DEFAULT nextval('public.participant_participant_id_seq'::regclass);


--
-- Name: sensor sensor_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.sensor ALTER COLUMN sensor_id SET DEFAULT nextval('public.sensor_sensor_id_seq'::regclass);


--
-- Name: survey_response response_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.survey_response ALTER COLUMN response_id SET DEFAULT nextval('public.survey_response_response_id_seq'::regclass);


--
-- Name: trip trip_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.trip ALTER COLUMN trip_id SET DEFAULT nextval('public.trip_trip_id_seq'::regclass);


--
-- Name: unit unit_id; Type: DEFAULT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.unit ALTER COLUMN unit_id SET DEFAULT nextval('public.unit_unit_id_seq'::regclass);


--
-- Name: bms_timeseries bms_timeseries_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.bms_timeseries
    ADD CONSTRAINT bms_timeseries_pkey PRIMARY KEY (ts_id);


--
-- Name: congress congress_code_key; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.congress
    ADD CONSTRAINT congress_code_key UNIQUE (code);


--
-- Name: congress congress_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.congress
    ADD CONSTRAINT congress_pkey PRIMARY KEY (congress_id);


--
-- Name: dataset_ingest dataset_ingest_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.dataset_ingest
    ADD CONSTRAINT dataset_ingest_pkey PRIMARY KEY (ingest_id);


--
-- Name: entropy_metric entropy_metric_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.entropy_metric
    ADD CONSTRAINT entropy_metric_pkey PRIMARY KEY (metric_id);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (event_id);


--
-- Name: lookup_measure lookup_measure_measure_key_key; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.lookup_measure
    ADD CONSTRAINT lookup_measure_measure_key_key UNIQUE (measure_key);


--
-- Name: lookup_measure lookup_measure_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.lookup_measure
    ADD CONSTRAINT lookup_measure_pkey PRIMARY KEY (measure_id);


--
-- Name: participant participant_anon_id_key; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.participant
    ADD CONSTRAINT participant_anon_id_key UNIQUE (anon_id);


--
-- Name: participant participant_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.participant
    ADD CONSTRAINT participant_pkey PRIMARY KEY (participant_id);


--
-- Name: sensor sensor_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.sensor
    ADD CONSTRAINT sensor_pkey PRIMARY KEY (sensor_id);


--
-- Name: sensor sensor_sensor_code_key; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.sensor
    ADD CONSTRAINT sensor_sensor_code_key UNIQUE (sensor_code);


--
-- Name: survey_response survey_response_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.survey_response
    ADD CONSTRAINT survey_response_pkey PRIMARY KEY (response_id);


--
-- Name: trip trip_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.trip
    ADD CONSTRAINT trip_pkey PRIMARY KEY (trip_id);


--
-- Name: unit unit_pkey; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.unit
    ADD CONSTRAINT unit_pkey PRIMARY KEY (unit_id);


--
-- Name: unit unit_unit_code_key; Type: CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.unit
    ADD CONSTRAINT unit_unit_code_key UNIQUE (unit_code);


--
-- Name: bms_timeseries bms_timeseries_sensor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.bms_timeseries
    ADD CONSTRAINT bms_timeseries_sensor_id_fkey FOREIGN KEY (sensor_id) REFERENCES public.sensor(sensor_id) ON DELETE CASCADE;


--
-- Name: entropy_metric entropy_metric_congress_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.entropy_metric
    ADD CONSTRAINT entropy_metric_congress_id_fkey FOREIGN KEY (congress_id) REFERENCES public.congress(congress_id);


--
-- Name: entropy_metric entropy_metric_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.entropy_metric
    ADD CONSTRAINT entropy_metric_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(event_id);


--
-- Name: entropy_metric entropy_metric_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.entropy_metric
    ADD CONSTRAINT entropy_metric_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.unit(unit_id);


--
-- Name: event event_congress_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_congress_id_fkey FOREIGN KEY (congress_id) REFERENCES public.congress(congress_id) ON DELETE CASCADE;


--
-- Name: lookup_measure lookup_measure_default_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.lookup_measure
    ADD CONSTRAINT lookup_measure_default_unit_id_fkey FOREIGN KEY (default_unit_id) REFERENCES public.unit(unit_id);


--
-- Name: sensor sensor_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.sensor
    ADD CONSTRAINT sensor_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.unit(unit_id);


--
-- Name: survey_response survey_response_congress_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.survey_response
    ADD CONSTRAINT survey_response_congress_id_fkey FOREIGN KEY (congress_id) REFERENCES public.congress(congress_id) ON DELETE CASCADE;


--
-- Name: survey_response survey_response_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.survey_response
    ADD CONSTRAINT survey_response_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES public.participant(participant_id) ON DELETE SET NULL;


--
-- Name: survey_response survey_response_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.survey_response
    ADD CONSTRAINT survey_response_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.unit(unit_id);


--
-- Name: trip trip_congress_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.trip
    ADD CONSTRAINT trip_congress_id_fkey FOREIGN KEY (congress_id) REFERENCES public.congress(congress_id);


--
-- Name: trip trip_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zentropy
--

ALTER TABLE ONLY public.trip
    ADD CONSTRAINT trip_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES public.participant(participant_id);


--
-- PostgreSQL database dump complete
--

