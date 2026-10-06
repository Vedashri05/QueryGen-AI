# Ask Your Database (NL → SQL)

Type a question in plain English; the app writes SQL, runs it safely, shows the table, and auto-charts it.

## Features
- Works with free options (Gemini, Groq, Ollama) or paid ones (Anthropic, OpenAI, Azure) via `LLM_PROVIDER`
- Read-only safety: single `SELECT` only + read-only SQLite connection
- Self-repair: if the SQL errors, the error is sent back to the model once
- Auto bar/line charts (Plotly), CSV download
- Streamlit UI, demo e-commerce database included
- Database-agnostic via SQLAlchemy: PostgreSQL, MySQL/MariaDB, SQLite

## Run (PostgreSQL via Docker)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your LLM API key
docker compose up -d        # starts PostgreSQL
python scripts/seed_db.py   # creates demo tables
streamlit run app.py
pytest
```
Use another database by changing `DB_URL` in `.env` (MySQL: `mysql+pymysql://user:pass@host:3306/db`;
SQLite: `sqlite:///data/sample.db`). Point it at your own database and it reads the schema automatically.
Prefer a read-only database user for real data.

## Structure
```
app.py              Streamlit UI
nlp2sql/
  config.py         env settings
  llm.py            provider-agnostic SQL generation
  safety.py         SQL validation guardrails
  db.py             SQLAlchemy engine, schema introspection, read-only execution
  pipeline.py       question -> SQL -> result (+ retry)
  viz.py            automatic chart selection
scripts/seed_db.py  demo data (any DB)
docker-compose.yml  local PostgreSQL
tests/              safety tests
```

## Ideas to extend (good for a portfolio)
- Schema retrieval with embeddings for big databases
- Conversation memory for follow-up questions
- Evaluation set of question → expected SQL with execution-accuracy scoring
