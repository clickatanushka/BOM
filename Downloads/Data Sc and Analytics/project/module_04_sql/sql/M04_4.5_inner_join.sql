-- =====================================================================
-- ShopKart SQL | Video 4.5 - INNER JOIN
-- Business question: "Which CATEGORY earns the most?"
-- Problem: orders has product_id but NOT category. Category lives in
-- the products table. A JOIN glues the two tables together on the
-- matching key: orders.product_id = products.product_id
-- =====================================================================

-- Q1. First look: each order with its product name and category.
--     o and p are TABLE aliases (short nicknames).
SELECT o.order_id,
       o.product_id,
       p.product_name,
       p.category,
       o.quantity
FROM orders AS o
INNER JOIN products AS p
        ON o.product_id = p.product_id
LIMIT 5;
-- Expected result: 5 rows
--   order_id | product_id | product_name    | category | quantity
--   ---------+------------+-----------------+----------+---------
--   O10001   | P048       | Wings of Fire   | Books    | 6
--   O10002   | P049       | Face Wash       | Beauty   | 2
--   O10003   | P020       | Saree           | Fashion  | 1
--   O10004   | P026       | Pressure Cooker | Home     | 2
--   O10005   | P026       | Pressure Cooker | Home     | 2

-- Q2. How many rows does the join return?
--     Every order has a valid product, so all 5,000 match.
SELECT COUNT(*) AS joined_rows
FROM orders AS o
INNER JOIN products AS p
        ON o.product_id = p.product_id;
-- Expected result: 1 row
--   joined_rows
--   -----------
--   5000

-- Q3. Revenue by category (JOIN + GROUP BY together).
SELECT p.category,
       COUNT(*) AS orders,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue
FROM orders AS o
INNER JOIN products AS p
        ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
-- Expected result: 5 rows
--   category    | orders | revenue
--   ------------+--------+-----------
--   Electronics | 1152   | 7331018.05
--   Fashion     | 1326   | 3121345.6
--   Home        | 1020   | 2655047.3
--   Beauty      | 750    | 877640.35
--   Books       | 752    | 719598.4
-- Electronics is half the business (Rs 73.3 lakh of Rs 1.47 crore).
-- Fashion has the MOST orders but less revenue (cheaper items).

-- Q4. Return rate by category. Fashion is highest (~21%).
SELECT p.category,
       COUNT(*) AS orders,
       ROUND(100.0 * AVG(o.returned = 'Y'), 1) AS return_rate_pct
FROM orders AS o
INNER JOIN products AS p
        ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;
-- Expected result: 5 rows
--   category    | orders | return_rate_pct
--   ------------+--------+----------------
--   Fashion     | 1326   | 21.0
--   Electronics | 1152   | 13.5
--   Home        | 1020   | 12.5
--   Beauty      | 750    | 9.5
--   Books       | 752    | 7.3

-- Q5. Top 5 products by revenue.
SELECT p.product_name,
       p.category,
       SUM(o.quantity) AS units,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue
FROM orders AS o
INNER JOIN products AS p
        ON o.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY revenue DESC
LIMIT 5;
-- Expected result: 5 rows
--   product_name        | category    | units | revenue
--   --------------------+-------------+-------+-----------
--   Tablet              | Electronics | 153   | 2522291.45
--   Smartphone          | Electronics | 148   | 1968580.1
--   Air Fryer           | Home        | 179   | 847787.7
--   Smartwatch          | Electronics | 171   | 585125.55
--   Mechanical Keyboard | Electronics | 161   | 491440.4

-- Q6. Profit needs cost_price, which also lives in products.
--     profit = revenue - quantity * cost_price
SELECT p.category,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)
                 - o.quantity * p.cost_price), 2)                 AS profit
FROM orders AS o
INNER JOIN products AS p
        ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY profit DESC;
-- Expected result: 5 rows
--   category    | revenue    | profit
--   ------------+------------+----------
--   Fashion     | 3121345.6  | 1130545.6
--   Electronics | 7331018.05 | 808468.05
--   Home        | 2655047.3  | 689997.3
--   Beauty      | 877640.35  | 375400.35
--   Books       | 719598.4   | 136338.4

-- Q7. Join orders with customers: revenue by membership type.
SELECT c.membership,
       COUNT(*) AS orders,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue,
       ROUND(AVG(o.quantity * o.unit_price * (1 - o.discount)), 2) AS avg_order_value
FROM orders AS o
INNER JOIN customers AS c
        ON o.customer_id = c.customer_id
GROUP BY c.membership;
-- Expected result: 2 rows
--   membership | orders | revenue    | avg_order_value
--   -----------+--------+------------+----------------
--   Free       | 2298   | 6777859.55 | 2949.46
--   Prime      | 2702   | 7926790.15 | 2933.68
-- Prime and Free spend about the SAME per order (~Rs 2,935-2,950),
-- but Prime places more orders in total.

-- Q8. "JOIN" alone means INNER JOIN. Same answer as Q2:
SELECT COUNT(*) AS joined_rows
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
-- Expected result: 1 row
--   joined_rows
--   -----------
--   5000
