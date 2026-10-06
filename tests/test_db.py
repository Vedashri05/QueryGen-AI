import pytest
from sqlalchemy import text

from nlp2sql import db


@pytest.fixture
def url(tmp_path):
    u = f"sqlite:///{tmp_path}/t.db"
    from sqlalchemy import create_engine
    with create_engine(u).begin() as c:
        c.execute(text("CREATE TABLE a (id INTEGER PRIMARY KEY, name TEXT)"))
        c.execute(text("CREATE TABLE b (id INTEGER PRIMARY KEY, a_id INTEGER REFERENCES a(id))"))
        c.execute(text("INSERT INTO a VALUES (1, 'x:y')"))
    return u


def test_schema_has_tables_and_fk(url):
    schema = db.get_schema(url)
    assert "TABLE a" in schema and "-> a.id" in schema


def test_run_query_handles_colon_and_percent(url):
    df = db.run_query(url, "SELECT name FROM a WHERE name LIKE '%x:y%'")
    assert len(df) == 1


def test_connection_is_read_only(url):
    with db.get_engine(url).connect() as c:
        with pytest.raises(Exception):
            c.execute(text("INSERT INTO a VALUES (2, 'z')"))
