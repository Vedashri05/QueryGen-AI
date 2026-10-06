"""Seed a demo e-commerce database into any SQLAlchemy URL.

    python scripts/seed_db.py                      # uses DB_URL from .env
    python scripts/seed_db.py mysql+pymysql://u:p@localhost/shop
"""
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (Column, Date, Float, ForeignKey, Integer, MetaData,
                        String, Table, create_engine)

load_dotenv()
url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DB_URL", "sqlite:///data/sample.db")
if url.startswith("sqlite"):
    Path("data").mkdir(exist_ok=True)

random.seed(7)
meta = MetaData()
customers = Table("customers", meta,
    Column("id", Integer, primary_key=True), Column("name", String(100)), Column("city", String(100)))
products = Table("products", meta,
    Column("id", Integer, primary_key=True), Column("name", String(100)),
    Column("category", String(100)), Column("price", Float))
orders = Table("orders", meta,
    Column("id", Integer, primary_key=True),
    Column("customer_id", Integer, ForeignKey("customers.id")), Column("order_date", Date))
order_items = Table("order_items", meta,
    Column("id", Integer, primary_key=True),
    Column("order_id", Integer, ForeignKey("orders.id")),
    Column("product_id", Integer, ForeignKey("products.id")), Column("quantity", Integer))

engine = create_engine(url)
meta.drop_all(engine)
meta.create_all(engine)

cities = ["Pune", "Mumbai", "Bengaluru", "Delhi", "Chennai"]
catalog = [("Laptop", "Electronics", 55000), ("Phone", "Electronics", 25000),
           ("Headphones", "Electronics", 3000), ("Desk", "Furniture", 8000),
           ("Chair", "Furniture", 6000), ("Notebook", "Stationery", 120),
           ("Pen Pack", "Stationery", 90)]

order_rows, item_rows, item_id = [], [], 1
for oid in range(1, 301):
    order_rows.append({"id": oid, "customer_id": random.randint(1, 40),
                       "order_date": date(2025, 1, 1) + timedelta(days=random.randint(0, 600))})
    for _ in range(random.randint(1, 3)):
        item_rows.append({"id": item_id, "order_id": oid,
                          "product_id": random.randint(1, len(catalog)),
                          "quantity": random.randint(1, 4)})
        item_id += 1

with engine.begin() as conn:
    conn.execute(customers.insert(), [{"id": i, "name": f"Customer {i}", "city": random.choice(cities)}
                                      for i in range(1, 41)])
    conn.execute(products.insert(), [{"id": i, "name": n, "category": c, "price": p}
                                     for i, (n, c, p) in enumerate(catalog, 1)])
    conn.execute(orders.insert(), order_rows)
    conn.execute(order_items.insert(), item_rows)

print(f"Seeded {engine.dialect.name} database.")
