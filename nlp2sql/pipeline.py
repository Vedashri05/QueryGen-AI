from dataclasses import dataclass

import pandas as pd

from . import db
from .llm import generate_sql
from .safety import validate_sql


@dataclass
class Result:
    sql: str
    df: pd.DataFrame
    retries: int


def ask(question: str, db_url: str, max_retries: int = 1) -> Result:
    """Question -> SQL -> validate -> execute, with one self-repair attempt on failure."""
    schema = db.get_schema(db_url)
    dialect = db.dialect_name(db_url)
    error = None
    for attempt in range(max_retries + 1):
        sql = validate_sql(generate_sql(question, schema, dialect, error))
        try:
            return Result(sql, db.run_query(db_url, sql), attempt)
        except Exception as exc:  # bad column/table etc. -> feed error back to the model
            error = str(exc)
            if attempt == max_retries:
                raise
