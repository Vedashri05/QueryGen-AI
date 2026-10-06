import pytest

from nlp2sql.safety import UnsafeSQLError, clean_sql, validate_sql


def test_allows_select():
    assert validate_sql("SELECT * FROM customers;") == "SELECT * FROM customers"


def test_allows_cte():
    assert validate_sql("WITH a AS (SELECT 1) SELECT * FROM a")


def test_strips_markdown_fence():
    assert clean_sql("```sql\nSELECT 1;\n```") == "SELECT 1"


@pytest.mark.parametrize("bad", [
    "DROP TABLE customers",
    "DELETE FROM orders",
    "SELECT 1; DROP TABLE x",
    "UPDATE products SET price = 0",
    "",
])
def test_blocks_unsafe(bad):
    with pytest.raises(UnsafeSQLError):
        validate_sql(bad)
