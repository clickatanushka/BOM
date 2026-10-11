-- =====================================================================
-- ShopKart SQL | Video 4.7 - CASE and functions
-- Business question: "How many small, medium and large orders do we
-- get, and in which month do we sell the most?"
-- =====================================================================

-- Q1. ROUND: tidy money values to 2 decimals.
SELECT order_id,
       quantity * unit_price * (1 - discount)           AS revenue_raw,
       ROUND(quantity * unit_price * (1 - discount), 2) AS revenue
FROM orders
LIMIT 3;
-- Expected result: 3 rows
--   order_id | revenue_raw | revenue
--   ---------+-------------+--------
--   O10001   | 1737.6      | 1737.6
--   O10002   | 570.0       | 570.0
--   O10003   | 2145.1      | 2145.1
-- (The "raw" column may show 1737.6000000000001 in your tool - that is
-- floating point; ROUND cleans it.)

-- Q2. CASE WHEN: an IF statement inside SQL.
--     Bucket each order by revenue: Small < 1,000 <= Medium < 5,000 <= Large
SELECT order_id,
       ROUND(quantity * unit_price * (1 - discount), 2) AS revenue,
       CASE
           WHEN quantity * unit_price * (1 - discount) < 1000 THEN 'Small'
           WHEN quantity * unit_price * (1 - discount) < 5000 THEN 'Medium'
           ELSE 'Large'
       END AS order_size
FROM orders
LIMIT 5;
-- Expected result: 5 rows
--   order_id | revenue | order_size
--   ---------+---------+-----------
--   O10001   | 1737.6  | Medium
--   O10002   | 570.0   | Small
--   O10003   | 2145.1  | Medium
--   O10004   | 3434.0  | Medium
--   O10005   | 3486.6  | Medium
-- CASE checks the WHEN lines top to bottom and stops at the first TRUE.

-- Q3. CASE + GROUP BY: how many orders and how much revenue per bucket.
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
-- Only 560 Large orders (11%) bring in half of all revenue!

-- Q4. UPPER, LOWER, LENGTH on text.
SELECT product_name,
       UPPER(product_name)  AS upper_name,
       LOWER(category)      AS lower_category,
       LENGTH(product_name) AS name_length
FROM products
LIMIT 5;
-- Expected result: 5 rows
--   product_name        | upper_name          | lower_category | name_length
--   --------------------+---------------------+----------------+------------
--   Wireless Earbuds    | WIRELESS EARBUDS    | electronics    | 16
--   Bluetooth Speaker   | BLUETOOTH SPEAKER   | electronics    | 17
--   Smartwatch          | SMARTWATCH          | electronics    | 10
--   Power Bank 10000mAh | POWER BANK 10000MAH | electronics    | 19
--   USB-C Charger       | USB-C CHARGER       | electronics    | 13

-- Q5. strftime('%m', date) pulls the month out of a date as text '01'..'12'.
SELECT order_id, order_date,
       strftime('%m', order_date) AS order_month,
       strftime('%Y', order_date) AS order_year
FROM orders
LIMIT 3;
-- Expected result: 3 rows
--   order_id | order_date | order_month | order_year
--   ---------+------------+-------------+-----------
--   O10001   | 2025-01-01 | 01          | 2025
--   O10002   | 2025-01-01 | 01          | 2025
--   O10003   | 2025-01-01 | 01          | 2025

-- Q6. Revenue by month: which is the festive peak?
SELECT strftime('%m', order_date) AS order_month,
       COUNT(*) AS orders,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 0) AS revenue
FROM orders
GROUP BY order_month
ORDER BY order_month;
-- Expected result: 12 rows
--   order_month | orders | revenue
--   ------------+--------+----------
--   01          | 320    | 1073267.0
--   02          | 289    | 863480.0
--   03          | 361    | 1080122.0
--   04          | 365    | 983481.0
--   05          | 333    | 786912.0
--   06          | 300    | 793841.0
--   07          | 371    | 873632.0
--   08          | 410    | 1203393.0
--   09          | 468    | 1543639.0
--   10          | 637    | 1978317.0
--   11          | 620    | 1965664.0
--   12          | 526    | 1558902.0
-- October (10) is the peak, November (11) a very close second -
-- the Diwali / festive season. May (05) is the lowest month.

-- Q7. COALESCE: replace NULL with something else.
--     Show 'Not rated' text for missing ratings (display only).
SELECT order_id, rating,
       COALESCE(rating, 'Not rated') AS rating_shown
FROM orders
WHERE rating IS NULL
LIMIT 3;
-- Expected result: 3 rows
--   order_id | rating | rating_shown
--   ---------+--------+-------------
--   O10037   | NULL   | Not rated
--   O10048   | NULL   | Not rated
--   O10071   | NULL   | Not rated

-- Q8. Careful: COALESCE(rating, 0) changes the average!
--     A missing rating is NOT a zero rating. Keep NULLs for averages.
SELECT ROUND(AVG(rating), 2)              AS avg_rating_correct,
       ROUND(AVG(COALESCE(rating, 0)), 2) AS avg_rating_wrong
FROM orders;
-- Expected result: 1 row
--   avg_rating_correct | avg_rating_wrong
--   -------------------+-----------------
--   3.96               | 3.75

-- Q9. CASE for a yes/no flag: delivery speed vs rating.
SELECT CASE WHEN delivery_days <= 4 THEN 'Fast (<=4 days)'
            ELSE 'Slow (5+ days)' END AS delivery_speed,
       COUNT(*) AS orders,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(100.0 * AVG(returned = 'Y'), 1) AS return_rate_pct
FROM orders
GROUP BY delivery_speed;
-- Expected result: 2 rows
--   delivery_speed  | orders | avg_rating | return_rate_pct
--   ----------------+--------+------------+----------------
--   Fast (<=4 days) | 3115   | 4.15       | 10.9
--   Slow (5+ days)  | 1885   | 3.65       | 18.4
-- Slow deliveries get lower ratings and more returns.
