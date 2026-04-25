-- Esquema Noticias 360
CREATE DATABASE noticias360;
\c noticias360;

CREATE TABLE periodistas (
    id        SERIAL PRIMARY KEY,
    nombre    VARCHAR(120) NOT NULL,
    email     VARCHAR(255) UNIQUE NOT NULL,
    pwd_hash  VARCHAR(255) NOT NULL,
    role      VARCHAR(30) DEFAULT 'ROLE_PERIODISTA',
    estado    VARCHAR(20) DEFAULT 'activo',
    mfa_secret VARCHAR(32),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE fuentes (
    id           SERIAL PRIMARY KEY,
    periodista_id INT REFERENCES periodistas(id),
    nombre       TEXT NOT NULL,   -- cifrado en prod con AES-256
    contacto     TEXT NOT NULL,   -- cifrado en prod con AES-256
    descripcion  TEXT,            -- cifrado en prod con AES-256
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE articulos (
    id        SERIAL PRIMARY KEY,
    titulo    VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    autor_id  INT REFERENCES periodistas(id),
    estado    VARCHAR(20) DEFAULT 'borrador',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE suscriptores (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    plan          VARCHAR(20) DEFAULT 'gratuito',
    estado        VARCHAR(20) DEFAULT 'activo',
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE USER noticias_app WITH PASSWORD 'CHANGE_ME';
GRANT CONNECT ON DATABASE noticias360 TO noticias_app;
GRANT USAGE ON SCHEMA public TO noticias_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO noticias_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO noticias_app;
