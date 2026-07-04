"""
01_generate_data.py
--------------------
Generates a realistic, Superstore-style retail sales dataset with the
kind of real-world messiness you'd actually find on Kaggle: missing
values, duplicate rows, inconsistent date formats, inconsistent text
casing, and a few negative/zero-quantity data-entry errors.

This stands in for downloading the dataset from Kaggle (network access
to kaggle.com isn't available in this build environment). The schema
and business logic mirror the real "Sample Superstore" dataset exactly,
so every downstream script (cleaning, EDA, SQL, dashboard) works
unchanged if you swap in the real Kaggle CSV later.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

N = 5500  # number of order-line rows

# ---- Reference/lookup data -------------------------------------------------
regions_states_cities = {
    "West":    [("California", "Los Angeles"), ("California", "San Francisco"),
                ("Washington", "Seattle"), ("Oregon", "Portland"), ("Nevada", "Las Vegas")],
    "East":    [("New York", "New York City"), ("New York", "Buffalo"),
                ("Massachusetts", "Boston"), ("Pennsylvania", "Philadelphia")],
    "Central": [("Texas", "Houston"), ("Texas", "Dallas"), ("Illinois", "Chicago"),
                ("Michigan", "Detroit"), ("Ohio", "Columbus")],
    "South":   [("Florida", "Miami"), ("Florida", "Orlando"), ("Georgia", "Atlanta"),
                ("North Carolina", "Charlotte"), ("Tennessee", "Nashville")],
}

categories = {
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art", "Labels", "Fasteners"],
    "Technology": ["Phones", "Accessories", "Machines", "Copiers"],
}

product_names = {
    "Chairs": ["Executive Leather Chair", "Mesh Task Chair", "Stackable Chair"],
    "Tables": ["Round Conference Table", "Adjustable Height Desk", "Glass Coffee Table"],
    "Bookcases": ["5-Shelf Bookcase", "Corner Bookcase"],
    "Furnishings": ["Desk Lamp", "Wall Clock", "Framed Print"],
    "Binders": ["3-Ring Binder", "View Binder", "Heavy-Duty Binder"],
    "Paper": ["Copy Paper A4", "Sticky Notes Pack", "Legal Pads"],
    "Storage": ["Plastic Storage Bin", "File Cabinet", "Storage Cart"],
    "Art": ["Marker Set", "Sketch Pad", "Colored Pencils"],
    "Labels": ["Address Labels", "Shipping Labels"],
    "Fasteners": ["Push Pins", "Paper Clips", "Rubber Bands"],
    "Phones": ["Smartphone X200", "Cordless Phone", "Phone Case"],
    "Accessories": ["Wireless Mouse", "USB Hub", "Laptop Stand"],
    "Machines": ["Label Printer", "Laminator"],
    "Copiers": ["Desktop Copier", "Office Copier Pro"],
}

ship_modes_clean = ["Standard Class", "Second Class", "First Class", "Same Day"]
segments = ["Consumer", "Corporate", "Home Office"]

first_names = ["John", "Priya", "Wei", "Maria", "Ahmed", "Sofia", "Liam", "Ananya",
               "Carlos", "Emma", "Raj", "Grace", "Noah", "Fatima", "Yuki", "Olivia"]
last_names = ["Smith", "Sharma", "Chen", "Garcia", "Khan", "Rossi", "Brown", "Patel",
              "Lopez", "Davis", "Nair", "Wilson", "Kim", "Ali", "Tanaka", "Clark"]

start_date = datetime(2022, 1, 1)
end_date = datetime(2025, 12, 31)

rows = []
customer_pool = [(f"{random.choice(first_names)} {random.choice(last_names)}",
                   f"CU-{1000+i}") for i in range(400)]

for i in range(N):
    region = random.choice(list(regions_states_cities.keys()))
    state, city = random.choice(regions_states_cities[region])
    category = random.choices(list(categories.keys()), weights=[0.2, 0.55, 0.25])[0]
    sub_category = random.choice(categories[category])
    product = random.choice(product_names[sub_category])
    cust_name, cust_id = random.choice(customer_pool)

    order_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    ship_delay = random.randint(1, 7)
    ship_date = order_date + timedelta(days=ship_delay)

    quantity = random.randint(1, 12)
    base_price = {
        "Furniture": random.uniform(60, 900),
        "Office Supplies": random.uniform(3, 120),
        "Technology": random.uniform(50, 1200),
    }[category]

    discount = random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5])
    sales = round(base_price * quantity * (1 - discount * 0.3), 2)  # discount softens list price -> sales

    # profit logic: technology has thin/negative margins at high discount,
    # furniture has the classic "profit goes negative above ~20% discount" pattern
    margin = {
        "Furniture": 0.18 - discount * 1.1,
        "Office Supplies": 0.28 - discount * 0.5,
        "Technology": 0.22 - discount * 0.8,
    }[category]
    profit = round(sales * margin + np.random.normal(0, 5), 2)

    ship_mode = random.choice(ship_modes_clean)
    segment = random.choice(segments)

    rows.append({
        "Order ID": f"ORD-{2022 + order_date.year - 2022}-{100000+i}",
        "Order Date": order_date,
        "Ship Date": ship_date,
        "Ship Mode": ship_mode,
        "Customer ID": cust_id,
        "Customer Name": cust_name,
        "Segment": segment,
        "Country": "United States",
        "City": city,
        "State": state,
        "Region": region,
        "Category": category,
        "Sub-Category": sub_category,
        "Product Name": product,
        "Sales": sales,
        "Quantity": quantity,
        "Discount": discount,
        "Profit": profit,
    })

df = pd.DataFrame(rows)

# ---- Inject realistic messiness --------------------------------------------

# 1. Inconsistent Ship Mode casing/spacing (common in real scraped/exported data)
messy_idx = df.sample(frac=0.08, random_state=1).index
df.loc[messy_idx, "Ship Mode"] = df.loc[messy_idx, "Ship Mode"].str.upper()
messy_idx2 = df.sample(frac=0.05, random_state=2).index
df.loc[messy_idx2, "Ship Mode"] = df.loc[messy_idx2, "Ship Mode"].str.lower().str.strip()

# 2. Missing Customer Name / Postal-equivalent (City) values
null_idx = df.sample(frac=0.02, random_state=3).index
df.loc[null_idx, "Customer Name"] = np.nan

null_idx2 = df.sample(frac=0.015, random_state=4).index
df.loc[null_idx2, "City"] = np.nan

# 3. Duplicate rows (exact dupes, as if the export ran twice)
dupes = df.sample(frac=0.01, random_state=5)
df = pd.concat([df, dupes], ignore_index=True)

# 4. Inconsistent date formats stored as strings (mix of formats)
def messy_date(d):
    fmt = random.choice(["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%B %d, %Y"])
    return d.strftime(fmt)

date_str_idx = df.sample(frac=1.0, random_state=6).index  # convert all to string w/ mixed formats
df["Order Date"] = [messy_date(d) for d in df["Order Date"]]
df["Ship Date"] = [messy_date(d) for d in df["Ship Date"]]

# 5. A few data-entry errors: negative quantity, zero sales
err_idx = df.sample(frac=0.005, random_state=7).index
df.loc[err_idx, "Quantity"] = -df.loc[err_idx, "Quantity"]

err_idx2 = df.sample(frac=0.003, random_state=8).index
df.loc[err_idx2, "Sales"] = 0

# 6. Extra whitespace in a text column (very common real-world issue)
ws_idx = df.sample(frac=0.03, random_state=9).index
df.loc[ws_idx, "Category"] = " " + df.loc[ws_idx, "Category"] + "  "

# Shuffle rows so it doesn't look artificially ordered
df = df.sample(frac=1.0, random_state=10).reset_index(drop=True)
df.insert(0, "Row ID", range(1, len(df) + 1))

df.to_csv("/home/claude/project/data/superstore_raw.csv", index=False)
print(f"Generated {len(df)} rows -> data/superstore_raw.csv")
print(df.dtypes)
