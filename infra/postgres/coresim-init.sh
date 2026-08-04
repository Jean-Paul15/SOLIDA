#!/bin/sh
# Extensions et garde-fou du role de lecture pour la base CORE-SIM.
# Voir 06-INFRA/03-postgresql.md.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    CREATE EXTENSION IF NOT EXISTS unaccent;

    CREATE ROLE solida_lecteur LOGIN PASSWORD '${SOLIDA_LECTEUR_PASSWORD}';
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO solida_lecteur;
    GRANT USAGE ON SCHEMA public TO solida_lecteur;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO solida_lecteur;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO solida_lecteur;
SQL
