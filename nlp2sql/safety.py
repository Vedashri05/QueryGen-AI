"""Guardrails: only a single, read-only SELECT statement may run."""
import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|truncate|attach|detach|pragma|vacuum|reindex|grant|revoke|call|exec|execute|copy|into)\b",
    re.IGNORECASE,
)


class UnsafeSQLError(ValueError):
    pass


def clean_sql(raw: str) -> str:
    """Strip markdown fences, comments and trailing semicolons from model output."""
    sql = raw.strip()
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql.strip().rstrip(";").strip()


def validate_sql(sql: str) -> str:
    sql = clean_sql(sql)
    if not sql:
        raise UnsafeSQLError("Empty query.")
    if ";" in sql:
        raise UnsafeSQLError("Only one statement is allowed.")
    if not re.match(r"^(select|with)\b", sql, re.IGNORECASE):
        raise UnsafeSQLError("Only SELECT queries are allowed.")
    if FORBIDDEN.search(sql):
        raise UnsafeSQLError("Query contains a forbidden keyword.")
    return sql
