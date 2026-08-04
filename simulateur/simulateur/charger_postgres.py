"""
Charge toutes les tables parquet de sorties/ dans PostgreSQL.
Usage : DATABASE_URL="postgresql://user:mdp@host:5432/solida" python3 simulateur/charger_postgres.py
Les tables techniques (prefixe _) ne sont pas chargees.
Necessite : pip install sqlalchemy psycopg2-binary pandas pyarrow
"""
import os, pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

out = Path(__file__).resolve().parent.parent / "sorties"
url = os.environ.get("DATABASE_URL")
if not url:
    raise SystemExit("Definir DATABASE_URL (postgresql://user:mdp@host:5432/solida)")

eng = create_engine(url)
for f in sorted(out.glob("*.parquet")):
    if f.stem.startswith("_"):
        continue
    df = pd.read_parquet(f)
    df.to_sql(f.stem, eng, if_exists="replace", index=False, chunksize=5000, method="multi")
    print(f"  charge : {f.stem:22s} ({len(df)} lignes, {len(df.columns)} colonnes)")
print("Termine. Index recommandes : societaires(numero_membre), credits(societaire_id).")
