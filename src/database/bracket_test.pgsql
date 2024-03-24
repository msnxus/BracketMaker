--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3
-- Dumped by pg_dump version 15.3

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bracket; Type: TABLE; Schema: public; Owner: nn3965
--

CREATE TABLE public.bracket (
    name character varying(80)
);


ALTER TABLE public.bracket OWNER TO nn3965;

--
-- Data for Name: bracket; Type: TABLE DATA; Schema: public; Owner: nn3965
--

COPY public.bracket (name) FROM stdin;
billy is fat
\.


--
-- PostgreSQL database dump complete
--

