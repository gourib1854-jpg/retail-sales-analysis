-- ============================================================
-- queries.sql
-- Business-question SQL against the `orders` table
-- (loaded via notebooks/04_load_sqlite.py -> data/superstore.db)
-- Runs as-is on SQLite; portable to MySQL/PostgreSQL with minor
-- date-function tweaks (noted inline).
-- ============================================================

-- 1. Top 10 customers by total profit
SELECT
    "Customer Name",
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Sales), 2)  AS total_sales,
    COUNT(DISTINCT "Order ID") AS num_orders
FROM orders
GROUP BY "Customer Name"
ORDER BY total_profit DESC
LIMIT 10;


-- 2. Monthly sales & profit trend
SELECT
    "Order Year-Month" AS year_month,
    ROUND(SUM(Sales), 2)  AS monthly_sales,
    ROUND(SUM(Profit), 2) AS monthly_profit
FROM orders
GROUP BY "Order Year-Month"
ORDER BY "Order Year-Month";


-- 3. Profit margin by discount bracket
SELECT
    Discount,
    ROUND(AVG("Profit Margin"), 4) AS avg_margin,
    COUNT(*) AS num_orders
FROM orders
GROUP BY Discount
ORDER BY Discount;


-- 4. Running total of sales per region over time (WINDOW FUNCTION)
SELECT
    Region,
    "Order Date",
    Sales,
    SUM(Sales) OVER (
        PARTITION BY Region
        ORDER BY "Order Date"
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total_sales
FROM orders
ORDER BY Region, "Order Date";


-- 5. Rank sub-categories by profit within each category (WINDOW FUNCTION)
SELECT
    Category,
    "Sub-Category",
    ROUND(SUM(Profit), 2) AS subcat_profit,
    RANK() OVER (
        PARTITION BY Category
        ORDER BY SUM(Profit) DESC
    ) AS profit_rank_in_category
FROM orders
GROUP BY Category, "Sub-Category"
ORDER BY Category, profit_rank_in_category;


-- 6. Customers who ordered above their own average order value (CTE)
WITH customer_avg AS (
    SELECT
        "Customer Name",
        AVG(Sales) AS avg_order_value
    FROM orders
    GROUP BY "Customer Name"
)
SELECT
    o."Customer Name",
    o."Order ID",
    o.Sales,
    ca.avg_order_value
FROM orders o
JOIN customer_avg ca
    ON o."Customer Name" = ca."Customer Name"
WHERE o.Sales > ca.avg_order_value
ORDER BY o."Customer Name";


-- 7. Year-over-year sales growth by category (CTE + self-comparison)
WITH yearly AS (
    SELECT
        Category,
        "Order Year" AS yr,
        SUM(Sales) AS total_sales
    FROM orders
    GROUP BY Category, "Order Year"
)
SELECT
    curr.Category,
    curr.yr AS year,
    curr.total_sales AS current_year_sales,
    prev.total_sales AS previous_year_sales,
    ROUND(
        (curr.total_sales - prev.total_sales) * 100.0 / prev.total_sales, 2
    ) AS yoy_growth_pct
FROM yearly curr
LEFT JOIN yearly prev
    ON curr.Category = prev.Category
    AND curr.yr = prev.yr + 1
ORDER BY curr.Category, curr.yr;


-- 8. Regions where average shipping time exceeds the company-wide average
SELECT
    Region,
    ROUND(AVG("Shipping Days"), 2) AS avg_shipping_days
FROM orders
GROUP BY Region
HAVING avg_shipping_days > (SELECT AVG("Shipping Days") FROM orders)
ORDER BY avg_shipping_days DESC;


-- 9. Loss-making orders (negative profit) by category and discount level
SELECT
    Category,
    Discount,
    COUNT(*) AS loss_making_orders,
    ROUND(SUM(Profit), 2) AS total_loss
FROM orders
WHERE Profit < 0
GROUP BY Category, Discount
ORDER BY total_loss ASC;


-- 10. Segment-level profitability summary
SELECT
    Segment,
    COUNT(DISTINCT "Order ID") AS num_orders,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) * 1.0 / SUM(Sales), 4) AS overall_margin
FROM orders
GROUP BY Segment
ORDER BY total_profit DESC;
