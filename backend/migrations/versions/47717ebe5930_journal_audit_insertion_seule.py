"""journal_audit en insertion seule

Revision ID: 47717ebe5930
Revises: c1f8e5a3d947
Create Date: 2026-08-12 16:10:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "47717ebe5930"
down_revision: str | None = "c1f8e5a3d947"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Meme patron que decision_scoring_insertion_seule (schema initial) : un trigger, pas un
    # simple REVOKE, parce que solida_app est proprietaire de la table (elle l'a creee via les
    # migrations) — un proprietaire contourne toujours les GRANT/REVOKE. Le trigger bloque tout
    # le monde, solida_app compris ; seule exception : un DELETE execute dans une transaction
    # qui a explicitement pose le flag de session `solida.purge_audit` (voir
    # purger_journal_audit.py, seul appelant legitime), pour que la purge planifiee par
    # retention (1 an, deja en place) continue de fonctionner.
    op.execute("""
        CREATE FUNCTION empecher_modification_journal_audit()
        RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'DELETE' AND current_setting('solida.purge_audit', true) = 'on' THEN
                RETURN OLD;
            END IF;
            RAISE EXCEPTION
                'journal_audit est en insertion seule : % interdit hors purge planifiee', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER journal_audit_insertion_seule
        BEFORE UPDATE OR DELETE ON journal_audit
        FOR EACH ROW EXECUTE FUNCTION empecher_modification_journal_audit();
    """)
    # solida_purge : role dedie a la purge, cree par infra/postgres/solida-init.sh au demarrage
    # du conteneur Postgres (avant que cette migration ne s'execute) — seul GRANT necessaire,
    # le trigger ci-dessus fait le reste du travail de controle d'acces.
    op.execute("GRANT SELECT, DELETE ON journal_audit TO solida_purge;")


def downgrade() -> None:
    op.execute("REVOKE SELECT, DELETE ON journal_audit FROM solida_purge;")
    op.execute("DROP TRIGGER journal_audit_insertion_seule ON journal_audit;")
    op.execute("DROP FUNCTION empecher_modification_journal_audit();")
