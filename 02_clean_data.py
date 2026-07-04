"""
02_clean_data.py
-----------------
Cleans the raw Superstore-style export. Every step is documented so this
can be explained in an interview: "here's what was wrong with the raw
data, and here's what I did about it."
"""
import pandas as pd
import numpy as np

df = pd.read_csv("/home/claude/project/data/superstore_raw.csv")

print("=== BEFORE CLEANING ===")
print("Shape:", df.shape)
dupe_cols = [c for c in df.columns if c != "Row ID"]
print("Duplicate rows (ignoring Row ID):", df.duplicated(subset=dupe_cols).sum())
print("Nulls per column:\n", df.isnull().sum()[df.isnull().sum() > 0])
print()

# 1. Drop exact duplicate rows (Row ID is just a sequential export artifact,
# so two rows identical on every real business field are true duplicates)
before = len(df)
df = df.drop_duplicates(subset=dupe_cols)
print(f"Removed {before - len(df)} exact duplicate rows")

# 2. Parse mixed-format date strings robustly
df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed", dayfirst=False, errors="coerce")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed", dayfirst=False, errors="coerce")
bad_dates = df["Order Date"].isnull().sum()
if bad_dates:
    print(f"Warning: {bad_dates} rows had unparseable Order Date -> dropped")
    df = df.dropna(subset=["Order Date"])

# 3. Normalize text casing/whitespace
df["Ship Mode"] = df["Ship Mode"].str.strip().str.title()
df["Category"] = df["Category"].str.strip().str.title()
df["Sub-Category"] = df["Sub-Category"].str.strip()

# 4. Handle missing values
# Customer Name: fill with "Unknown Customer" rather than dropping the row
# (the sale still happened and should count toward regional/category totals)
df["Customer Name"] = df["Customer Name"].fillna("Unknown Customer")
df["City"] = df["City"].fillna("Unknown City")

# 5. Fix data-entry errors
# Negative quantities are almost certainly sign-entry errors, not returns
# (a real returns flag would be a separate column) -> take absolute value
neg_qty = (df["Quantity"] < 0).sum()
df["Quantity"] = df["Quantity"].abs()
print(f"Fixed {neg_qty} negative-quantity entries (converted to absolute value)")

# Zero-sales rows with nonzero quantity are broken records -> drop
zero_sales = ((df["Sales"] == 0) & (df["Quantity"] > 0)).sum()
df = df[~((df["Sales"] == 0) & (df["Quantity"] > 0))]
print(f"Dropped {zero_sales} rows with Sales=0 but Quantity>0 (broken export rows)")

# 6. Derived columns useful for analysis
df["Order Year"] = df["Order Date"].dt.year
df["Order Month"] = df["Order Date"].dt.month
df["Order Month Name"] = df["Order Date"].dt.month_name()
df["Order Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
df["Profit Margin"] = (df["Profit"] / df["Sales"]).round(4)
df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

df = df.sort_values("Order Date").reset_index(drop=True)

print("\n=== AFTER CLEANING ===")
print("Shape:", df.shape)
print("Duplicate rows:", df.duplicated().sum())
print("Remaining nulls:\n", df.isnull().sum()[df.isnull().sum() > 0] if df.isnull().sum().sum() else "None")

df.to_csv("/home/claude/project/data/superstore_cleaned.csv", index=False)
print("\nSaved -> data/superstore_cleaned.csv")
