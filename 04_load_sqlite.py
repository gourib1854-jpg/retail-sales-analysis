"""
04_load_sqlite.py
------------------
Loads the cleaned dataset into a SQLite database (orders table) so the
SQL queries in sql/queries.sql can be run against something real.
SQLite is used so the whole project runs with zero external setup;
the same queries work unchanged on MySQL/PostgreSQL.
"""
import pandas as pd
import sqlite3

df = pd.read_csv("/home/claude/project/data/superstore_cleaned.csv")

conn = sqlite3.connect("/home/claude/project/data/superstore.db")
df.to_sql("orders", conn, if_exists="replace", index=False)
conn.commit()

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM orders")
print("Rows loaded into orders table:", cur.fetchone()[0])
conn.close()
