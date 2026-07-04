"""
03_eda_analysis.py
-------------------
Exploratory analysis answering concrete business questions and saving
the charts used in the insight report / README.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#444444",
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "font.size": 11,
})

df = pd.read_csv("/home/claude/project/data/superstore_cleaned.csv", parse_dates=["Order Date", "Ship Date"])
CHARTS = "/home/claude/project/charts"
ACCENT = "#2E5EAA"
ACCENT2 = "#D9773D"

# ---------------------------------------------------------------------------
# Q1: Which categories drive profit vs loss?
cat = df.groupby("Category")[["Sales", "Profit"]].sum().sort_values("Profit")
fig, ax = plt.subplots(figsize=(7, 4))
colors = [ACCENT2 if v < 0 else ACCENT for v in cat["Profit"]]
ax.barh(cat.index, cat["Profit"], color=colors)
ax.set_title("Profit by Category")
ax.set_xlabel("Total Profit ($)")
plt.tight_layout()
plt.savefig(f"{CHARTS}/01_profit_by_category.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Q2: Does discount level kill profit? (classic Superstore insight)
disc = df.groupby("Discount")["Profit Margin"].mean().sort_index()
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(disc.index.astype(str), disc.values, color=[ACCENT if v >= 0 else ACCENT2 for v in disc.values])
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Average Profit Margin by Discount Level")
ax.set_xlabel("Discount")
ax.set_ylabel("Avg Profit Margin")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
plt.tight_layout()
plt.savefig(f"{CHARTS}/02_margin_by_discount.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Q3: Monthly sales trend
monthly = df.groupby("Order Year-Month")[["Sales", "Profit"]].sum().reset_index()
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(monthly["Order Year-Month"], monthly["Sales"], color=ACCENT, label="Sales")
ax.plot(monthly["Order Year-Month"], monthly["Profit"], color=ACCENT2, label="Profit")
ax.set_xticks(range(0, len(monthly), 4))
ax.set_xticklabels(monthly["Order Year-Month"][::4], rotation=45, ha="right")
ax.set_title("Monthly Sales & Profit Trend")
ax.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS}/03_monthly_trend.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Q4: Regional performance
reg = df.groupby("Region")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False)
fig, ax = plt.subplots(figsize=(7, 4))
x = range(len(reg))
ax.bar([i - 0.2 for i in x], reg["Sales"], width=0.4, label="Sales", color=ACCENT)
ax.bar([i + 0.2 for i in x], reg["Profit"], width=0.4, label="Profit", color=ACCENT2)
ax.set_xticks(list(x))
ax.set_xticklabels(reg.index)
ax.set_title("Sales vs Profit by Region")
ax.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS}/04_region_performance.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Q5: Top 10 sub-categories by profit
subcat = df.groupby("Sub-Category")["Profit"].sum().sort_values()
fig, ax = plt.subplots(figsize=(7, 5))
colors = [ACCENT2 if v < 0 else ACCENT for v in subcat.values]
ax.barh(subcat.index, subcat.values, color=colors)
ax.set_title("Profit by Sub-Category")
plt.tight_layout()
plt.savefig(f"{CHARTS}/05_profit_by_subcategory.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Text summary of key findings (used in report + README)
findings = []

top_cat = cat["Profit"].idxmax()
worst_cat = cat["Profit"].idxmin()
findings.append(f"{top_cat} is the strongest category by total profit; "
                 f"{worst_cat} has the weakest profit contribution.")

high_disc_margin = df[df["Discount"] >= 0.3]["Profit Margin"].mean()
low_disc_margin = df[df["Discount"] <= 0.1]["Profit Margin"].mean()
findings.append(f"Orders with discounts of 30%+ average a {high_disc_margin:.1%} profit margin, "
                 f"versus {low_disc_margin:.1%} for orders discounted 10% or less.")

best_region = reg["Profit"].idxmax()
worst_region = reg["Profit"].idxmin()
findings.append(f"{best_region} region leads in profit; {worst_region} lags furthest behind despite "
                 f"comparable sales volume.")

worst_subcat = subcat.idxmin()
findings.append(f"'{worst_subcat}' is the single biggest drag on profit at the sub-category level.")

avg_ship = df["Shipping Days"].mean()
findings.append(f"Average shipping time across all orders is {avg_ship:.1f} days.")

with open("/home/claude/project/charts/key_findings.txt", "w") as f:
    for i, line in enumerate(findings, 1):
        f.write(f"{i}. {line}\n")

print("Charts saved to /home/claude/project/charts/")
print("\nKEY FINDINGS:")
for line in findings:
    print("-", line)
