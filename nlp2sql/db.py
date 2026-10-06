"""Database access via SQLAlchemy: works with PostgreSQL, MySQL, SQLite, ..."""
from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine

_READ_ONLY_SQL = {
    "sqlite": "PRAGMA query_only = ON",
    "postgresql": "SET default_transaction_read_only = on",
    "mysql": "SET SESSION TRANSACTION READ ONLY",
}


@lru_cache(maxsize=8)
def get_engine(url: str) -> Engine:
    engine = create_engine(url, pool_pre_ping=True)

    @event.listens_for(engine, "connect")
    def _make_read_only(dbapi_conn, _record):
        stmt = _READ_ONLY_SQL.get(engine.dialect.name)
        if stmt:  # second line of defence behind safety.py
            cur = dbapi_conn.cursor()
            cur.execute(stmt)
            cur.close()
            dbapi_conn.commit()

    return engine


def dialect_name(url: str) -> str:
    return get_engine(url).dialect.name


def get_schema(url: str) -> str:
    """Compact, LLM-friendly description of every table, column and foreign key."""
    insp = inspect(get_engine(url))
    blocks = []
    for table in sorted(insp.get_table_names()):
        pks = set(insp.get_pk_constraint(table).get("constrained_columns") or [])
        fks = {
            col: f"{fk['referred_table']}.{fk['referred_columns'][i]}"
            for fk in insp.get_foreign_keys(table)
            for i, col in enumerate(fk["constrained_columns"])
        }
        lines = []
        for c in insp.get_columns(table):
            line = f"  {c['name']} {c['type']}"
            if c["name"] in pks:
                line += " PRIMARY KEY"
            if c["name"] in fks:
                line += f" -> {fks[c['name']]}"
            lines.append(line)
        blocks.append(f"TABLE {table} (\n" + ",\n".join(lines) + "\n)")
    return "\n\n".join(blocks)


def run_query(url: str, sql: str, limit: int = 500) -> pd.DataFrame:
    # Escape ':' so SQLAlchemy doesn't mistake it for a bind parameter
    wrapped = f"SELECT * FROM ({sql}) AS q LIMIT {int(limit)}".replace(":", r"\:")
    with get_engine(url).connect() as conn:
        result = conn.execute(text(wrapped))
        return pd.DataFrame(result.fetchall(), columns=list(result.keys()))
