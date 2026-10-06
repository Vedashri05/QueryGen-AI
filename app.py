import streamlit as st

from nlp2sql import db
from nlp2sql.config import settings
from nlp2sql.pipeline import ask
from nlp2sql.safety import UnsafeSQLError
from nlp2sql.viz import auto_chart

st.set_page_config(page_title="Ask your database", page_icon="🗄️", layout="wide")
st.title("🗄️ Ask your database")

with st.sidebar:
    st.header("Settings")
    db_url = st.text_input("Database URL", settings.db_url, type="password",
                           help="SQLAlchemy URL, e.g. postgresql+psycopg2://user:pass@host:5432/db")
    st.caption(f"LLM provider: **{settings.provider}**")
    try:
        schema = db.get_schema(db_url)
        with st.expander("Schema"):
            st.code(schema, language="sql")
    except Exception as exc:
        st.error(f"Can't open database: {exc}\n\nIs the database running and seeded? (`docker compose up -d`, then `python scripts/seed_db.py`)")
        st.stop()

examples = [
    "Total revenue by product category",
    "Top 5 customers by number of orders",
    "Monthly order count",
]
cols = st.columns(len(examples))
picked = None
for col, ex in zip(cols, examples):
    if col.button(ex, use_container_width=True):
        picked = ex

question = st.chat_input("Ask a question about your data…") or picked

if question:
    st.chat_message("user").write(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Writing and running SQL…"):
                result = ask(question, db_url)
            st.code(result.sql, language="sql")
            if result.retries:
                st.caption("The first query failed, so it was automatically corrected.")
            st.dataframe(result.df, use_container_width=True)
            fig = auto_chart(result.df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            st.download_button("Download CSV", result.df.to_csv(index=False), "result.csv")
        except UnsafeSQLError as exc:
            st.error(f"Blocked for safety: {exc}")
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")
