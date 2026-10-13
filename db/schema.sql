-- Tesfa database structure (tables only, no data). Run `CREATE EXTENSION IF NOT EXISTS vector;` first,
-- because rag_embeddings uses the pgvector type. Generated with pg_dump --schema-only.
--
-- PostgreSQL database dump
--

\restrict S9a4j76zp57Pfw6hWKCaRtchsjs7f90W0gjhWqkTGsEIb9V2cHuoDnxPve4v0HZ

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

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
-- Name: tesfa; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA tesfa;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alliances; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.alliances (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: alliances_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.alliances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alliances_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.alliances_id_seq OWNED BY tesfa.alliances.id;


--
-- Name: climate_zones; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.climate_zones (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: climate_zones_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.climate_zones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: climate_zones_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.climate_zones_id_seq OWNED BY tesfa.climate_zones.id;


--
-- Name: conflict_predictions; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.conflict_predictions (
    conflict_id integer NOT NULL,
    risk_score double precision NOT NULL,
    risk_category text NOT NULL
);


--
-- Name: conflict_types; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.conflict_types (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: conflict_types_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.conflict_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conflict_types_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.conflict_types_id_seq OWNED BY tesfa.conflict_types.id;


--
-- Name: conflicts; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.conflicts (
    id integer NOT NULL,
    country_a_id integer NOT NULL,
    country_b_id integer NOT NULL,
    conflict_type_id integer NOT NULL,
    year integer,
    duration_days integer,
    military_deaths_a integer,
    military_deaths_b integer,
    civilian_deaths integer,
    economic_loss_usd_billions double precision,
    temperature_avg_c double precision,
    rainfall_mm double precision,
    terrain_type_id integer,
    population_a_millions double precision,
    population_b_millions double precision,
    gdp_a_billions double precision,
    gdp_b_billions double precision,
    alliance_a_id integer,
    alliance_b_id integer,
    weapon_id integer,
    air_strikes integer,
    naval_battles integer,
    sanctions boolean,
    refugees_millions double precision,
    ceasefire boolean,
    outcome_id integer,
    latitude double precision,
    longitude double precision,
    climate_zone_id integer,
    resource_dispute_id integer,
    un_involvement boolean
);


--
-- Name: countries; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.countries (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: outcomes; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.outcomes (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: reference_links; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.reference_links (
    id integer NOT NULL,
    risk_category text NOT NULL,
    "position" integer NOT NULL,
    url text NOT NULL,
    title text NOT NULL
);


--
-- Name: resource_disputes; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.resource_disputes (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: risk_categories; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.risk_categories (
    name text NOT NULL,
    consequence text NOT NULL
);


--
-- Name: terrain_types; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.terrain_types (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: weapons; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.weapons (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: conflicts_full; Type: VIEW; Schema: tesfa; Owner: -
--

CREATE VIEW tesfa.conflicts_full AS
 SELECT c.id,
    ca.name AS country_a,
    cb.name AS country_b,
    ct.name AS conflict_type,
    c.year,
    c.duration_days,
    c.military_deaths_a,
    c.military_deaths_b,
    c.civilian_deaths,
    c.economic_loss_usd_billions,
    c.temperature_avg_c,
    c.rainfall_mm,
    tt.name AS terrain_type,
    c.population_a_millions,
    c.population_b_millions,
    c.gdp_a_billions,
    c.gdp_b_billions,
    aa.name AS alliance_a,
    ab.name AS alliance_b,
    w.name AS weapons_used,
    c.air_strikes,
    c.naval_battles,
    c.sanctions,
    c.refugees_millions,
    c.ceasefire,
    o.name AS outcome,
    c.latitude,
    c.longitude,
    cz.name AS climate_zone,
    rd.name AS resource_dispute,
    c.un_involvement,
    p.risk_score AS predicted_risk_score,
    p.risk_category,
    rc.consequence AS predicted_postwar_consequence,
    l.links AS evidence_reference_links
   FROM (((((((((((((tesfa.conflicts c
     JOIN tesfa.countries ca ON ((ca.id = c.country_a_id)))
     JOIN tesfa.countries cb ON ((cb.id = c.country_b_id)))
     JOIN tesfa.conflict_types ct ON ((ct.id = c.conflict_type_id)))
     LEFT JOIN tesfa.terrain_types tt ON ((tt.id = c.terrain_type_id)))
     LEFT JOIN tesfa.alliances aa ON ((aa.id = c.alliance_a_id)))
     LEFT JOIN tesfa.alliances ab ON ((ab.id = c.alliance_b_id)))
     LEFT JOIN tesfa.weapons w ON ((w.id = c.weapon_id)))
     LEFT JOIN tesfa.outcomes o ON ((o.id = c.outcome_id)))
     LEFT JOIN tesfa.climate_zones cz ON ((cz.id = c.climate_zone_id)))
     LEFT JOIN tesfa.resource_disputes rd ON ((rd.id = c.resource_dispute_id)))
     LEFT JOIN tesfa.conflict_predictions p ON ((p.conflict_id = c.id)))
     LEFT JOIN tesfa.risk_categories rc ON ((rc.name = p.risk_category)))
     LEFT JOIN ( SELECT reference_links.risk_category,
            jsonb_agg(jsonb_build_object('url', reference_links.url, 'title', reference_links.title) ORDER BY reference_links."position") AS links
           FROM tesfa.reference_links
          GROUP BY reference_links.risk_category) l ON ((l.risk_category = p.risk_category)));


--
-- Name: countries_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.countries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: countries_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.countries_id_seq OWNED BY tesfa.countries.id;


--
-- Name: outcomes_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.outcomes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: outcomes_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.outcomes_id_seq OWNED BY tesfa.outcomes.id;


--
-- Name: rag_embeddings; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.rag_embeddings (
    id integer NOT NULL,
    document_text text,
    metadata jsonb,
    embedding public.vector(768),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: rag_embeddings_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.rag_embeddings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rag_embeddings_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.rag_embeddings_id_seq OWNED BY tesfa.rag_embeddings.id;


--
-- Name: reference_links_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.reference_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reference_links_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.reference_links_id_seq OWNED BY tesfa.reference_links.id;


--
-- Name: resource_disputes_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.resource_disputes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: resource_disputes_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.resource_disputes_id_seq OWNED BY tesfa.resource_disputes.id;


--
-- Name: runs; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.runs (
    run_id character varying(100) NOT NULL,
    query text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: steps; Type: TABLE; Schema: tesfa; Owner: -
--

CREATE TABLE tesfa.steps (
    id integer NOT NULL,
    run_id character varying(100),
    tool_name character varying(100),
    input_payload jsonb,
    output_payload jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: steps_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.steps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: steps_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.steps_id_seq OWNED BY tesfa.steps.id;


--
-- Name: terrain_types_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.terrain_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: terrain_types_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.terrain_types_id_seq OWNED BY tesfa.terrain_types.id;


--
-- Name: weapons_id_seq; Type: SEQUENCE; Schema: tesfa; Owner: -
--

CREATE SEQUENCE tesfa.weapons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: weapons_id_seq; Type: SEQUENCE OWNED BY; Schema: tesfa; Owner: -
--

ALTER SEQUENCE tesfa.weapons_id_seq OWNED BY tesfa.weapons.id;


--
-- Name: alliances id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.alliances ALTER COLUMN id SET DEFAULT nextval('tesfa.alliances_id_seq'::regclass);


--
-- Name: climate_zones id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.climate_zones ALTER COLUMN id SET DEFAULT nextval('tesfa.climate_zones_id_seq'::regclass);


--
-- Name: conflict_types id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflict_types ALTER COLUMN id SET DEFAULT nextval('tesfa.conflict_types_id_seq'::regclass);


--
-- Name: countries id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.countries ALTER COLUMN id SET DEFAULT nextval('tesfa.countries_id_seq'::regclass);


--
-- Name: outcomes id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.outcomes ALTER COLUMN id SET DEFAULT nextval('tesfa.outcomes_id_seq'::regclass);


--
-- Name: rag_embeddings id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.rag_embeddings ALTER COLUMN id SET DEFAULT nextval('tesfa.rag_embeddings_id_seq'::regclass);


--
-- Name: reference_links id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.reference_links ALTER COLUMN id SET DEFAULT nextval('tesfa.reference_links_id_seq'::regclass);


--
-- Name: resource_disputes id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.resource_disputes ALTER COLUMN id SET DEFAULT nextval('tesfa.resource_disputes_id_seq'::regclass);


--
-- Name: steps id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.steps ALTER COLUMN id SET DEFAULT nextval('tesfa.steps_id_seq'::regclass);


--
-- Name: terrain_types id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.terrain_types ALTER COLUMN id SET DEFAULT nextval('tesfa.terrain_types_id_seq'::regclass);


--
-- Name: weapons id; Type: DEFAULT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.weapons ALTER COLUMN id SET DEFAULT nextval('tesfa.weapons_id_seq'::regclass);


--
-- Name: alliances alliances_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.alliances
    ADD CONSTRAINT alliances_name_key UNIQUE (name);


--
-- Name: alliances alliances_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.alliances
    ADD CONSTRAINT alliances_pkey PRIMARY KEY (id);


--
-- Name: climate_zones climate_zones_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.climate_zones
    ADD CONSTRAINT climate_zones_name_key UNIQUE (name);


--
-- Name: climate_zones climate_zones_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.climate_zones
    ADD CONSTRAINT climate_zones_pkey PRIMARY KEY (id);


--
-- Name: conflict_predictions conflict_predictions_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflict_predictions
    ADD CONSTRAINT conflict_predictions_pkey PRIMARY KEY (conflict_id);


--
-- Name: conflict_types conflict_types_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflict_types
    ADD CONSTRAINT conflict_types_name_key UNIQUE (name);


--
-- Name: conflict_types conflict_types_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflict_types
    ADD CONSTRAINT conflict_types_pkey PRIMARY KEY (id);


--
-- Name: conflicts conflicts_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_pkey PRIMARY KEY (id);


--
-- Name: countries countries_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.countries
    ADD CONSTRAINT countries_name_key UNIQUE (name);


--
-- Name: countries countries_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (id);


--
-- Name: outcomes outcomes_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.outcomes
    ADD CONSTRAINT outcomes_name_key UNIQUE (name);


--
-- Name: outcomes outcomes_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.outcomes
    ADD CONSTRAINT outcomes_pkey PRIMARY KEY (id);


--
-- Name: rag_embeddings rag_embeddings_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.rag_embeddings
    ADD CONSTRAINT rag_embeddings_pkey PRIMARY KEY (id);


--
-- Name: reference_links reference_links_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.reference_links
    ADD CONSTRAINT reference_links_pkey PRIMARY KEY (id);


--
-- Name: resource_disputes resource_disputes_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.resource_disputes
    ADD CONSTRAINT resource_disputes_name_key UNIQUE (name);


--
-- Name: resource_disputes resource_disputes_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.resource_disputes
    ADD CONSTRAINT resource_disputes_pkey PRIMARY KEY (id);


--
-- Name: risk_categories risk_categories_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.risk_categories
    ADD CONSTRAINT risk_categories_pkey PRIMARY KEY (name);


--
-- Name: runs runs_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.runs
    ADD CONSTRAINT runs_pkey PRIMARY KEY (run_id);


--
-- Name: steps steps_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.steps
    ADD CONSTRAINT steps_pkey PRIMARY KEY (id);


--
-- Name: terrain_types terrain_types_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.terrain_types
    ADD CONSTRAINT terrain_types_name_key UNIQUE (name);


--
-- Name: terrain_types terrain_types_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.terrain_types
    ADD CONSTRAINT terrain_types_pkey PRIMARY KEY (id);


--
-- Name: weapons weapons_name_key; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.weapons
    ADD CONSTRAINT weapons_name_key UNIQUE (name);


--
-- Name: weapons weapons_pkey; Type: CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.weapons
    ADD CONSTRAINT weapons_pkey PRIMARY KEY (id);


--
-- Name: conflict_predictions conflict_predictions_conflict_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflict_predictions
    ADD CONSTRAINT conflict_predictions_conflict_id_fkey FOREIGN KEY (conflict_id) REFERENCES tesfa.conflicts(id);


--
-- Name: conflict_predictions conflict_predictions_risk_category_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflict_predictions
    ADD CONSTRAINT conflict_predictions_risk_category_fkey FOREIGN KEY (risk_category) REFERENCES tesfa.risk_categories(name);


--
-- Name: conflicts conflicts_alliance_a_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_alliance_a_id_fkey FOREIGN KEY (alliance_a_id) REFERENCES tesfa.alliances(id);


--
-- Name: conflicts conflicts_alliance_b_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_alliance_b_id_fkey FOREIGN KEY (alliance_b_id) REFERENCES tesfa.alliances(id);


--
-- Name: conflicts conflicts_climate_zone_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_climate_zone_id_fkey FOREIGN KEY (climate_zone_id) REFERENCES tesfa.climate_zones(id);


--
-- Name: conflicts conflicts_conflict_type_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_conflict_type_id_fkey FOREIGN KEY (conflict_type_id) REFERENCES tesfa.conflict_types(id);


--
-- Name: conflicts conflicts_country_a_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_country_a_id_fkey FOREIGN KEY (country_a_id) REFERENCES tesfa.countries(id);


--
-- Name: conflicts conflicts_country_b_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_country_b_id_fkey FOREIGN KEY (country_b_id) REFERENCES tesfa.countries(id);


--
-- Name: conflicts conflicts_outcome_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_outcome_id_fkey FOREIGN KEY (outcome_id) REFERENCES tesfa.outcomes(id);


--
-- Name: conflicts conflicts_resource_dispute_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_resource_dispute_id_fkey FOREIGN KEY (resource_dispute_id) REFERENCES tesfa.resource_disputes(id);


--
-- Name: conflicts conflicts_terrain_type_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_terrain_type_id_fkey FOREIGN KEY (terrain_type_id) REFERENCES tesfa.terrain_types(id);


--
-- Name: conflicts conflicts_weapon_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.conflicts
    ADD CONSTRAINT conflicts_weapon_id_fkey FOREIGN KEY (weapon_id) REFERENCES tesfa.weapons(id);


--
-- Name: reference_links reference_links_risk_category_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.reference_links
    ADD CONSTRAINT reference_links_risk_category_fkey FOREIGN KEY (risk_category) REFERENCES tesfa.risk_categories(name);


--
-- Name: steps steps_run_id_fkey; Type: FK CONSTRAINT; Schema: tesfa; Owner: -
--

ALTER TABLE ONLY tesfa.steps
    ADD CONSTRAINT steps_run_id_fkey FOREIGN KEY (run_id) REFERENCES tesfa.runs(run_id);


--
-- PostgreSQL database dump complete
--

\unrestrict S9a4j76zp57Pfw6hWKCaRtchsjs7f90W0gjhWqkTGsEIb9V2cHuoDnxPve4v0HZ

