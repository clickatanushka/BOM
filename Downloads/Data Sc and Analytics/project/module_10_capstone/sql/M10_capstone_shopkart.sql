-- =====================================================================
-- Module 10 – Capstone: ShopKart returns
-- Video 10.2 – Build it: SQL -> pandas -> charts -> model
-- Brief: "Returns are eating our profit. What's going on, and can we predict them?"
-- Database: shopkart.db (tables: orders 5,000 rows, customers 800, products 60)
-- Tool: sqliteonline.com -> File -> Open DB -> shopkart.db, OR run inside the notebook.
-- Every query below was run on shopkart.db; the real output is shown under it.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1 – Sanity check: how many rows in each table?
-- Run this first. If the numbers differ, you uploaded the wrong file.
-- ---------------------------------------------------------------------
SELECT 'orders' AS table_name, COUNT(*) AS n_rows FROM orders
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products;
-- Expected output (3 rows):
-- table_name | n_rows
-- orders | 5000
-- customers | 800
-- products | 60

-- ---------------------------------------------------------------------
-- Q2 – Headline: overall return rate
-- returned is 'Y' or 'N'. CASE turns Y into 1, so AVG gives the share returned.
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS total_orders,
       SUM(CASE WHEN returned = 'Y' THEN 1 ELSE 0 END) AS returned_orders,
       ROUND(AVG(CASE WHEN returned = 'Y' THEN 1.0 ELSE 0 END) * 100, 1) AS return_rate_pct
FROM orders;
-- Expected output (1 row):
-- total_orders | returned_orders | return_rate_pct
-- 5000 | 687 | 13.7

-- ---------------------------------------------------------------------
-- Q3 – THE CAPSTONE QUERY: one joined table for Python
-- orders + products (category, cost) + customers (membership, age, gender).
-- INNER JOIN to products: every order has a product. LEFT JOIN to customers: keep every order even if a customer were missing.
-- revenue is calculated in SQL so Python and SQL agree: quantity * unit_price * (1 - discount).
-- This is exactly the query pasted into the notebook (cell 'Load data with SQL').
-- ---------------------------------------------------------------------
SELECT o.order_id, o.order_date, o.customer_id, o.product_id,
       o.quantity, o.unit_price, o.discount, o.city, o.payment_mode,
       o.delivery_days, o.rating, o.returned,
       p.product_name, p.category, p.cost_price,
       c.gender, c.age, c.membership,
       ROUND(o.quantity * o.unit_price * (1 - o.discount), 2) AS revenue
FROM orders AS o
INNER JOIN products AS p ON o.product_id = p.product_id
LEFT JOIN customers AS c ON o.customer_id = c.customer_id
ORDER BY o.order_id;
-- Expected output (5000 rows, first 3 shown):
-- order_id | order_date | customer_id | product_id | quantity | unit_price | discount | city | payment_mode | delivery_days | rating | returned | product_name | category | cost_price | gender | age | membership | revenue
-- O10001 | 2025-01-01 | C0593 | P048 | 6 | 362 | 0.2 | Delhi | COD | 4 | 2 | N | Wings of Fire | Books | 240 | Female | 26 | Prime | 1737.6
-- O10002 | 2025-01-01 | C0367 | P049 | 2 | 300 | 0.05 | Chennai | Debit Card | 4 | 5 | N | Face Wash | Beauty | 150 | Male | 35 | Free | 570.0
-- O10003 | 2025-01-01 | C0707 | P020 | 1 | 2258 | 0.05 | Delhi | Debit Card | 2 | 3 | N | Saree | Fashion | 1280 | Male | 41 | Prime | 2145.1

-- ---------------------------------------------------------------------
-- Q3b – Row count of the capstone query (should match orders)
-- If this is not 5000, a join is duplicating or dropping rows.
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS n_rows
FROM orders AS o
INNER JOIN products AS p ON o.product_id = p.product_id
LEFT JOIN customers AS c ON o.customer_id = c.customer_id;
-- Expected output (1 row):
-- n_rows
-- 5000

-- ---------------------------------------------------------------------
-- Q4 – Return rate by city (highest first)
-- ---------------------------------------------------------------------
SELECT city,
       COUNT(*) AS orders,
       SUM(CASE WHEN returned = 'Y' THEN 1 ELSE 0 END) AS returns,
       ROUND(AVG(CASE WHEN returned = 'Y' THEN 1.0 ELSE 0 END) * 100, 1) AS return_rate_pct
FROM orders
GROUP BY city
ORDER BY return_rate_pct DESC;
-- Expected output (10 rows):
-- city | orders | returns | return_rate_pct
-- Pune | 451 | 146 | 32.4
-- Kolkata | 414 | 59 | 14.3
-- Ahmedabad | 303 | 43 | 14.2
-- Lucknow | 326 | 44 | 13.5
-- Jaipur | 270 | 36 | 13.3
-- Hyderabad | 495 | 63 | 12.7
-- Chennai | 442 | 56 | 12.7
-- Bengaluru | 736 | 89 | 12.1
-- Delhi | 804 | 82 | 10.2
-- Mumbai | 759 | 69 | 9.1

-- ---------------------------------------------------------------------
-- Q5 – Return rate by category
-- Needs the products table for category.
-- ---------------------------------------------------------------------
SELECT p.category,
       COUNT(*) AS orders,
       SUM(CASE WHEN o.returned = 'Y' THEN 1 ELSE 0 END) AS returns,
       ROUND(AVG(CASE WHEN o.returned = 'Y' THEN 1.0 ELSE 0 END) * 100, 1) AS return_rate_pct
FROM orders AS o
INNER JOIN products AS p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;
-- Expected output (5 rows):
-- category | orders | returns | return_rate_pct
-- Fashion | 1326 | 279 | 21.0
-- Electronics | 1152 | 155 | 13.5
-- Home | 1020 | 127 | 12.5
-- Beauty | 750 | 71 | 9.5
-- Books | 752 | 55 | 7.3

-- ---------------------------------------------------------------------
-- Q6 – Return rate by payment mode
-- ---------------------------------------------------------------------
SELECT payment_mode,
       COUNT(*) AS orders,
       ROUND(AVG(CASE WHEN returned = 'Y' THEN 1.0 ELSE 0 END) * 100, 1) AS return_rate_pct
FROM orders
GROUP BY payment_mode
ORDER BY return_rate_pct DESC;
-- Expected output (6 rows):
-- payment_mode | orders | return_rate_pct
-- COD | 983 | 19.1
-- Unknown | 90 | 16.7
-- Net Banking | 297 | 13.1
-- Credit Card | 888 | 12.6
-- Debit Card | 685 | 12.3
-- UPI | 2057 | 12.1

-- ---------------------------------------------------------------------
-- Q7 – Return rate by delivery speed (grouped into bands with CASE)
-- Single days like 11 or 12 have only 1–2 orders, so we group them into bands.
-- ---------------------------------------------------------------------
SELECT CASE
         WHEN delivery_days <= 3 THEN '1) 2-3 days'
         WHEN delivery_days = 4  THEN '2) 4 days'
         WHEN delivery_days = 5  THEN '3) 5 days'
         WHEN delivery_days <= 7 THEN '4) 6-7 days'
         ELSE '5) 8+ days'
       END AS delivery_band,
       COUNT(*) AS orders,
       ROUND(AVG(CASE WHEN returned = 'Y' THEN 1.0 ELSE 0 END) * 100, 1) AS return_rate_pct
FROM orders
GROUP BY delivery_band
ORDER BY delivery_band;
-- Expected output (5 rows):
-- delivery_band | orders | return_rate_pct
-- 1) 2-3 days | 1905 | 10.4
-- 2) 4 days | 1210 | 11.7
-- 3) 5 days | 942 | 16.6
-- 4) 6-7 days | 824 | 18.8
-- 5) 8+ days | 119 | 30.3

-- ---------------------------------------------------------------------
-- Q8 – Money: revenue of returned orders ('revenue lost to returns')
-- ASSUMPTION (say it out loud in the video): when an order is returned, ShopKart refunds the full
-- order value, so the whole revenue of that order is lost. We ignore return shipping cost and
-- resale of the returned item (we have no data for them). So this is an estimate, not an audited loss.
-- We also show the profit those orders would have made (revenue - quantity * cost_price).
-- ---------------------------------------------------------------------
SELECT ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 0) AS total_revenue,
       ROUND(SUM(CASE WHEN o.returned = 'Y'
                      THEN o.quantity * o.unit_price * (1 - o.discount) ELSE 0 END), 0) AS revenue_lost_to_returns,
       ROUND(SUM(CASE WHEN o.returned = 'Y'
                      THEN o.quantity * o.unit_price * (1 - o.discount) - o.quantity * p.cost_price ELSE 0 END), 0) AS profit_on_returned_orders,
       ROUND(100.0 * SUM(CASE WHEN o.returned = 'Y'
                      THEN o.quantity * o.unit_price * (1 - o.discount) ELSE 0 END)
             / SUM(o.quantity * o.unit_price * (1 - o.discount)), 1) AS pct_revenue_lost
FROM orders AS o
INNER JOIN products AS p ON o.product_id = p.product_id;
-- Expected output (1 row):
-- total_revenue | revenue_lost_to_returns | profit_on_returned_orders | pct_revenue_lost
-- 14704650.0 | 2150901.0 | 460821.0 | 14.6

-- ---------------------------------------------------------------------
-- Q9 – Where is the money lost? Revenue of returned orders by city
-- ---------------------------------------------------------------------
SELECT city,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 0) AS revenue_lost
FROM orders
WHERE returned = 'Y'
GROUP BY city
ORDER BY revenue_lost DESC;
-- Expected output (10 rows):
-- city | revenue_lost
-- Pune | 536752.0
-- Bengaluru | 335693.0
-- Delhi | 267422.0
-- Mumbai | 184125.0
-- Hyderabad | 178041.0
-- Kolkata | 174594.0
-- Lucknow | 144173.0
-- Ahmedabad | 141293.0
-- Chennai | 105909.0
-- Jaipur | 82897.0

-- ---------------------------------------------------------------------
-- Q10 – Deeper: is Pune bad for every category? (CTE)
-- A CTE gives the subquery a name. We compare Pune with all other cities, category by category.
-- ---------------------------------------------------------------------
WITH tagged AS (
  SELECT p.category,
         CASE WHEN o.city = 'Pune' THEN 'Pune' ELSE 'Other cities' END AS city_group,
         CASE WHEN o.returned = 'Y' THEN 1.0 ELSE 0 END AS is_returned
  FROM orders AS o
  INNER JOIN products AS p ON o.product_id = p.product_id
)
SELECT category, city_group, COUNT(*) AS orders,
       ROUND(AVG(is_returned) * 100, 1) AS return_rate_pct
FROM tagged
GROUP BY category, city_group
ORDER BY category, city_group;
-- Expected output (10 rows):
-- category | city_group | orders | return_rate_pct
-- Beauty | Other cities | 701 | 8.3
-- Beauty | Pune | 49 | 26.5
-- Books | Other cities | 694 | 6.2
-- Books | Pune | 58 | 20.7
-- Electronics | Other cities | 1048 | 11.5
-- Electronics | Pune | 104 | 33.7
-- Fashion | Other cities | 1187 | 19.0
-- Fashion | Pune | 139 | 38.8
-- Home | Other cities | 919 | 10.3
-- Home | Pune | 101 | 31.7

-- ---------------------------------------------------------------------
-- Q11 – Is Pune slow to deliver? Average delivery days by city
-- ---------------------------------------------------------------------
SELECT city, ROUND(AVG(delivery_days), 2) AS avg_delivery_days
FROM orders
GROUP BY city
ORDER BY avg_delivery_days DESC;
-- Expected output (10 rows):
-- city | avg_delivery_days
-- Pune | 5.77
-- Lucknow | 5.75
-- Jaipur | 5.63
-- Hyderabad | 3.81
-- Delhi | 3.76
-- Kolkata | 3.75
-- Chennai | 3.74
-- Ahmedabad | 3.74
-- Bengaluru | 3.7
-- Mumbai | 3.69
