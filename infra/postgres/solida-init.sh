#!/bin/sh
# Extension et role de lecture (rapports) pour la base SOLIDA.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
    CREATE EXTENSION IF NOT EXISTS pgcrypto;

    CREATE ROLE solida_lecture LOGIN PASSWORD '${SOLIDA_LECTURE_PASSWORD}';
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO solida_lecture;
    GRANT USAGE ON SCHEMA public TO solida_lecture;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO solida_lecture;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO solida_lecture;
SQL
