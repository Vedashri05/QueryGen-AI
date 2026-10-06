import pandas as pd
import plotly.express as px


def auto_chart(df: pd.DataFrame):
    """Pick a simple, sensible chart; return None if the data doesn't suit one."""
    if df.empty or len(df.columns) < 2 or len(df) > 200:
        return None
    num_cols = df.select_dtypes("number").columns.tolist()
    other_cols = [c for c in df.columns if c not in num_cols]
    if not num_cols or not other_cols:
        return None
    x, y = other_cols[0], num_cols[0]
    looks_like_time = any(k in x.lower() for k in ("date", "month", "year", "day", "time"))
    if looks_like_time:
        return px.line(df, x=x, y=y, markers=True)
    if len(df) <= 30:
        return px.bar(df, x=x, y=y)
    return None
