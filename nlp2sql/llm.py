from .config import settings

SYSTEM_PROMPT = (
    "You are an expert data analyst who writes {dialect} SQL. Given a database schema "
    "and a question, reply with exactly ONE read-only SELECT query that answers it. "
    "Use only tables and columns that exist in the schema. "
    "Output only the SQL: no markdown, no comments, no explanation."
)


def _user_prompt(question: str, schema: str, error: str | None = None) -> str:
    prompt = f"Schema:\n{schema}\n\nQuestion: {question}"
    if error:
        prompt += f"\n\nYour previous query failed with: {error}\nWrite a corrected query."
    return prompt


def _anthropic(prompt: str, system: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_key)
    msg = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text")


def _openai_compatible(client, model: str, prompt: str, system: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def _openai(prompt: str, system: str) -> str:
    from openai import OpenAI

    return _openai_compatible(OpenAI(api_key=settings.openai_key), settings.openai_model, prompt, system)


def _azure(prompt: str, system: str) -> str:
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=settings.azure_key,
        azure_endpoint=settings.azure_endpoint,
        api_version=settings.azure_version,
    )
    return _openai_compatible(client, settings.azure_deployment, prompt, system)


def _compat(base_url: str, key: str, model: str, prompt: str, system: str) -> str:
    """Any provider that speaks the OpenAI chat API (Gemini, Groq, Ollama, ...)."""
    from openai import OpenAI

    return _openai_compatible(OpenAI(api_key=key or "none", base_url=base_url), model, prompt, system)


def _gemini(prompt: str, system: str) -> str:
    return _compat("https://generativelanguage.googleapis.com/v1beta/openai/",
                   settings.gemini_key, settings.gemini_model, prompt, system)


def _groq(prompt: str, system: str) -> str:
    return _compat("https://api.groq.com/openai/v1",
                   settings.groq_key, settings.groq_model, prompt, system)


def _ollama(prompt: str, system: str) -> str:
    return _compat(settings.ollama_url, "ollama", settings.ollama_model, prompt, system)


PROVIDERS = {
    "anthropic": _anthropic, "openai": _openai, "azure": _azure,
    "gemini": _gemini, "groq": _groq, "ollama": _ollama,
}


def generate_sql(question: str, schema: str, dialect: str, error: str | None = None) -> str:
    try:
        fn = PROVIDERS[settings.provider]
    except KeyError:
        raise ValueError(f"Unknown LLM_PROVIDER '{settings.provider}'. Use: {list(PROVIDERS)}")
    return fn(_user_prompt(question, schema, error), SYSTEM_PROMPT.format(dialect=dialect))
