-- =====================================================================
-- ShopKart SQL PROJECT - Module 4 end-to-end (run this file FIRST)
-- 10 business questions the ShopKart manager asked, answered with SQL.
-- Tool : sqliteonline.com -> File -> Open DB -> shopkart.db
-- Data : shopkart.db = the cleaned Module 2 orders (5,000 rows) +
--        customers (800) + products (60).
-- Revenue of an order line = quantity * unit_price * (1 - discount)
-- Every "Expected result" below was produced by running the query.
-- If your numbers match, your setup is correct.
-- =====================================================================

-- BQ1. How big is the business? (orders, customers, units, revenue)
SELECT COUNT(*)                    AS total_orders,
       COUNT(DISTINCT customer_id) AS active_customers,
       SUM(quantity)               AS units_sold,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 2) AS total_revenue,
       ROUND(AVG(quantity * unit_price * (1 - discount)), 2) AS avg_order_value
FROM orders;
-- Expected result: 1 row
--   total_orders | active_customers | units_sold | total_revenue | avg_order_value
--   -------------+------------------+------------+---------------+----------------
--   5000         | 758              | 8955       | 14704649.7    | 2940.93

-- BQ2. Which cities bring the most revenue? (top 5)
SELECT city,
       COUNT(*) AS orders,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 2) AS revenue
FROM orders
GROUP BY city
ORDER BY revenue DESC
LIMIT 5;
-- Expected result: 5 rows
--   city      | orders | revenue
--   ----------+--------+-----------
--   Delhi     | 804    | 2323405.4
--   Bengaluru | 736    | 2256613.25
--   Mumbai    | 759    | 2090206.0
--   Hyderabad | 495    | 1494616.75
--   Pune      | 451    | 1387698.3

-- BQ3. Which city has a returns problem? (return rate by city)
SELECT city,
       COUNT(*) AS orders,
       ROUND(100.0 * AVG(returned = 'Y'), 1) AS return_rate_pct
FROM orders
GROUP BY city
ORDER BY return_rate_pct DESC
LIMIT 3;
-- Expected result: 3 rows
--   city      | orders | return_rate_pct
--   ----------+--------+----------------
--   Pune      | 451    | 32.4
--   Kolkata   | 414    | 14.3
--   Ahmedabad | 303    | 14.2
-- Pune 32.4% vs 13.7% overall (about 2.4 times).

-- BQ4. Which category earns the most, and which gets returned most?
SELECT p.category,
       COUNT(*) AS orders,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue,
       ROUND(100.0 * AVG(o.returned = 'Y'), 1) AS return_rate_pct
FROM orders AS o
JOIN products AS p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
-- Expected result: 5 rows
--   category    | orders | revenue    | return_rate_pct
--   ------------+--------+------------+----------------
--   Electronics | 1152   | 7331018.05 | 13.5
--   Fashion     | 1326   | 3121345.6  | 21.0
--   Home        | 1020   | 2655047.3  | 12.5
--   Beauty      | 750    | 877640.35  | 9.5
--   Books       | 752    | 719598.4   | 7.3

-- BQ5. Which month is the peak? (top 3 months by revenue)
SELECT strftime('%m', order_date) AS order_month,
       COUNT(*) AS orders,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 0) AS revenue
FROM orders
GROUP BY order_month
ORDER BY revenue DESC
LIMIT 3;
-- Expected result: 3 rows
--   order_month | orders | revenue
--   ------------+--------+----------
--   10          | 637    | 1978317.0
--   11          | 620    | 1965664.0
--   12          | 526    | 1558902.0

-- BQ6. How do customers pay, and does COD get returned more?
SELECT payment_mode,
       COUNT(*) AS orders,
       ROUND(100.0 * AVG(returned = 'Y'), 1) AS return_rate_pct
FROM orders
GROUP BY payment_mode
ORDER BY orders DESC;
-- Expected result: 6 rows
--   payment_mode | orders | return_rate_pct
--   -------------+--------+----------------
--   UPI          | 2057   | 12.1
--   COD          | 983    | 19.1
--   Credit Card  | 888    | 12.6
--   Debit Card   | 685    | 12.3
--   Net Banking  | 297    | 13.1
--   Unknown      | 90     | 16.7

-- BQ7. How many customers signed up but never ordered?
SELECT COUNT(*) AS never_ordered
FROM customers AS c
LEFT JOIN orders AS o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
-- Expected result: 1 row
--   never_ordered
--   -------------
--   42

-- BQ8. Small / Medium / Large orders: who brings the money?
SELECT CASE
           WHEN quantity * unit_price * (1 - discount) < 1000 THEN 'Small'
           WHEN quantity * unit_price * (1 - discount) < 5000 THEN 'Medium'
           ELSE 'Large'
       END AS order_size,
       COUNT(*) AS orders,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 0) AS revenue
FROM orders
GROUP BY order_size
ORDER BY revenue DESC;
-- Expected result: 3 rows
--   order_size | orders | revenue
--   -----------+--------+----------
--   Large      | 560    | 7370455.0
--   Medium     | 2802   | 6325172.0
--   Small      | 1638   | 1009022.0

-- BQ9. Does slow delivery hurt ratings? (missing ratings are ignored)
SELECT delivery_days,
       COUNT(*) AS orders,
       ROUND(AVG(rating), 2) AS avg_rating
FROM orders
WHERE delivery_days <= 8
GROUP BY delivery_days
ORDER BY delivery_days;
-- Expected result: 7 rows
--   delivery_days | orders | avg_rating
--   --------------+--------+-----------
--   2             | 689    | 4.2
--   3             | 1216   | 4.22
--   4             | 1210   | 4.05
--   5             | 942    | 3.81
--   6             | 579    | 3.63
--   7             | 245    | 3.39
--   8             | 83     | 3.08
-- (Days 9-12 have very few orders - 36 in total - so we leave them out.)

-- BQ10. Top 3 categories by revenue for Prime vs Free members.
WITH member_category AS (
    SELECT c.membership,
           p.category,
           ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue
    FROM orders AS o
    JOIN customers AS c ON o.customer_id = c.customer_id
    JOIN products  AS p ON o.product_id  = p.product_id
    GROUP BY c.membership, p.category
),
ranked AS (
    SELECT m.membership, m.category, m.revenue,
           (SELECT COUNT(*) + 1
            FROM member_category AS x
            WHERE x.membership = m.membership
              AND x.revenue > m.revenue) AS rank_in_group
    FROM member_category AS m
)
SELECT membership, category, revenue, rank_in_group
FROM ranked
WHERE rank_in_group <= 3
ORDER BY membership, rank_in_group;
-- Expected result: 6 rows
--   membership | category    | revenue    | rank_in_group
--   -----------+-------------+------------+--------------
--   Free       | Electronics | 3347966.9  | 1
--   Free       | Fashion     | 1455160.8  | 2
--   Free       | Home        | 1252160.2  | 3
--   Prime      | Electronics | 3983051.15 | 1
--   Prime      | Fashion     | 1666184.8  | 2
--   Prime      | Home        | 1402887.1  | 3

-- BQ11 (bonus). Prime vs Free: order value vs order frequency.
SELECT c.membership,
       COUNT(DISTINCT o.customer_id) AS active_customers,
       COUNT(*) AS orders,
       ROUND(1.0 * COUNT(*) / COUNT(DISTINCT o.customer_id), 2) AS orders_per_customer,
       ROUND(AVG(o.quantity * o.unit_price * (1 - o.discount)), 2) AS avg_order_value
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.customer_id
GROUP BY c.membership;
-- Expected result: 2 rows
--   membership | active_customers | orders | orders_per_customer | avg_order_value
--   -----------+------------------+--------+---------------------+----------------
--   Free       | 482              | 2298   | 4.77                | 2949.46
--   Prime      | 276              | 2702   | 9.79                | 2933.68
-- =====================================================================
-- Summary for the manager (copy into your notes):
-- 1. Rs 1.47 crore revenue from 5,000 orders; Delhi is the top city.
-- 2. Pune returns 32.4% of orders - 2.4x the 13.7% average. Investigate.
-- 3. Electronics = half of revenue; Fashion has the highest return rate.
-- 4. Oct-Nov festive season is the peak (Oct Rs 19.8 lakh, Nov Rs 19.7 lakh).
-- 5. 42 customers never ordered - send a first-order coupon.
-- 6. Prime and Free spend the same per order; Prime orders twice as often.
-- =====================================================================
