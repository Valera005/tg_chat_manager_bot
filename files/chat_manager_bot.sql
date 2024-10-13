--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1
-- Dumped by pg_dump version 14.1

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
-- Name: bans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bans (
    id bigint NOT NULL,
    chat_id bigint,
    user_id bigint,
    datetime timestamp without time zone,
    datetime_of_expiration timestamp without time zone,
    moderator_user_id bigint NOT NULL,
    description text
);


ALTER TABLE public.bans OWNER TO postgres;

--
-- Name: bans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bans_id_seq OWNER TO postgres;

--
-- Name: bans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bans_id_seq OWNED BY public.bans.id;


--
-- Name: commands; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.commands (
    command_id integer,
    chat_id bigint,
    rank integer
);


ALTER TABLE public.commands OWNER TO postgres;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    id bigint NOT NULL,
    chat_id bigint,
    title character varying(255),
    username character varying(255),
    type character varying(50),
    chat_member_type character varying(50),
    date_of_addition timestamp without time zone,
    date_of_edit timestamp without time zone,
    can_send_messages boolean DEFAULT true,
    rules text,
    hello_message text,
    max_warns integer DEFAULT 3,
    warn_interval interval DEFAULT '7 days'::interval,
    ban_interval interval DEFAULT '7 days'::interval,
    owner_user_id bigint,
    max_invites integer DEFAULT 0,
    is_talks boolean DEFAULT true,
    is_groups boolean DEFAULT true,
    is_urls boolean DEFAULT true,
    is_bots boolean DEFAULT true,
    is_channels boolean DEFAULT true,
    is_transfer_owner boolean DEFAULT false,
    prev_owner_user_id bigint,
    last_time_general_meeting timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
    CONSTRAINT groups_max_warns_check CHECK ((max_warns >= 0)),
    CONSTRAINT groups_type_check CHECK ((((type)::text = 'group'::text) OR ((type)::text = 'supergroup'::text)))
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.groups_id_seq OWNER TO postgres;

--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.links (
    id integer NOT NULL,
    deeplink character varying(255),
    number_of_trans integer DEFAULT 0,
    is_visible boolean DEFAULT true
);


ALTER TABLE public.links OWNER TO postgres;

--
-- Name: links_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.links_id_seq OWNER TO postgres;

--
-- Name: links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.links_id_seq OWNED BY public.links.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id bigint NOT NULL,
    chat_id bigint,
    user_id bigint,
    html_text text,
    message_thread_id bigint,
    datetime timestamp without time zone,
    message_id bigint
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    pay_id bigint NOT NULL,
    user_id bigint,
    transaction_id bigint,
    status character varying(50),
    method character varying(50),
    amount double precision,
    currency character varying(15),
    profit double precision,
    email character varying(255),
    description character varying(255),
    date timestamp without time zone
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profiles (
    id bigint NOT NULL,
    user_id bigint,
    username character varying(255),
    first_name character varying(255),
    full_name character varying(255),
    nickname character varying(15),
    coins integer DEFAULT 0
);


ALTER TABLE public.profiles OWNER TO postgres;

--
-- Name: profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.profiles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.profiles_id_seq OWNER TO postgres;

--
-- Name: profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.profiles_id_seq OWNED BY public.profiles.id;


--
-- Name: rewards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rewards (
    id bigint NOT NULL,
    chat_id bigint,
    user_id bigint,
    datetime timestamp without time zone,
    moderator_user_id bigint,
    power integer,
    description text
);


ALTER TABLE public.rewards OWNER TO postgres;

--
-- Name: rewards_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rewards_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rewards_id_seq OWNER TO postgres;

--
-- Name: rewards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rewards_id_seq OWNED BY public.rewards.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    chat_id bigint,
    user_id bigint,
    rank integer DEFAULT 0,
    karma integer DEFAULT 0,
    datetime timestamp without time zone,
    invited_by_user_id bigint,
    CONSTRAINT users_rank_check CHECK (((rank >= 0) AND (rank < 5)))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users_private; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_private (
    id bigint NOT NULL,
    chat_id bigint,
    user_id bigint,
    username character varying(255),
    first_name character varying(255),
    full_name character varying(255),
    nickname character varying(15),
    datetime timestamp without time zone,
    deeplink character varying(255)
);


ALTER TABLE public.users_private OWNER TO postgres;

--
-- Name: users_private_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_private_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_private_id_seq OWNER TO postgres;

--
-- Name: users_private_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_private_id_seq OWNED BY public.users_private.id;


--
-- Name: warns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warns (
    chat_id bigint,
    user_id bigint,
    datetime timestamp without time zone,
    datetime_of_expiration timestamp without time zone,
    description text,
    id bigint NOT NULL,
    moderator_user_id bigint
);


ALTER TABLE public.warns OWNER TO postgres;

--
-- Name: warns_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warns_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.warns_id_seq OWNER TO postgres;

--
-- Name: warns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warns_id_seq OWNED BY public.warns.id;


--
-- Name: weddings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.weddings (
    id bigint NOT NULL,
    chat_id bigint,
    user1_id bigint,
    user2_id bigint,
    datetime timestamp without time zone
);


ALTER TABLE public.weddings OWNER TO postgres;

--
-- Name: weddings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.weddings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weddings_id_seq OWNER TO postgres;

--
-- Name: weddings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.weddings_id_seq OWNED BY public.weddings.id;


--
-- Name: bans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bans ALTER COLUMN id SET DEFAULT nextval('public.bans_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: links id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.links ALTER COLUMN id SET DEFAULT nextval('public.links_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles ALTER COLUMN id SET DEFAULT nextval('public.profiles_id_seq'::regclass);


--
-- Name: rewards id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rewards ALTER COLUMN id SET DEFAULT nextval('public.rewards_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: users_private id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_private ALTER COLUMN id SET DEFAULT nextval('public.users_private_id_seq'::regclass);


--
-- Name: warns id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warns ALTER COLUMN id SET DEFAULT nextval('public.warns_id_seq'::regclass);


--
-- Name: weddings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weddings ALTER COLUMN id SET DEFAULT nextval('public.weddings_id_seq'::regclass);


--
-- Name: bans bans_chat_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bans
    ADD CONSTRAINT bans_chat_id_user_id_key UNIQUE (chat_id, user_id);


--
-- Name: bans bans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bans
    ADD CONSTRAINT bans_pkey PRIMARY KEY (id);


--
-- Name: commands commands_chat_id_command_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commands
    ADD CONSTRAINT commands_chat_id_command_id_key UNIQUE (chat_id, command_id);


--
-- Name: groups groups_chat_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_chat_id_key UNIQUE (chat_id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: links links_deeplink_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_deeplink_key UNIQUE (deeplink);


--
-- Name: links links_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: messages messages_chat_id_message_id_message_thread_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_chat_id_message_id_message_thread_id_key UNIQUE (chat_id, message_id, message_thread_id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (pay_id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);


--
-- Name: rewards rewards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rewards
    ADD CONSTRAINT rewards_pkey PRIMARY KEY (id);


--
-- Name: users users_chat_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_chat_id_user_id_key UNIQUE (chat_id, user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_private users_private_chat_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_private
    ADD CONSTRAINT users_private_chat_id_key UNIQUE (chat_id);


--
-- Name: users_private users_private_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_private
    ADD CONSTRAINT users_private_pkey PRIMARY KEY (id);


--
-- Name: users_private users_private_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_private
    ADD CONSTRAINT users_private_user_id_key UNIQUE (user_id);


--
-- Name: warns warns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warns
    ADD CONSTRAINT warns_pkey PRIMARY KEY (id);


--
-- Name: weddings weddings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weddings
    ADD CONSTRAINT weddings_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

