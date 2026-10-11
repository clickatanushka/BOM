-- =====================================================================
-- ShopKart SQL | Video 4.4 - Aggregates, GROUP BY, HAVING
-- Business question: "Which city brings the most revenue?"
-- Aggregate functions squash many rows into ONE number:
--   COUNT  SUM  AVG  MIN  MAX
-- =====================================================================

-- Q1. The whole business in one row: orders, units, revenue.
SELECT COUNT(*)                                       AS total_orders,
       SUM(quantity)                                  AS units_sold,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 2) AS total_revenue
FROM orders;
-- Expected result: 1 row
--   total_orders | units_sold | total_revenue
--   -------------+------------+--------------
--   5000         | 8955       | 14704649.7
-- ROUND(x, 2) keeps 2 decimals. Total revenue = Rs 1,47,04,649.70

-- Q2. Average order value, smallest and biggest order.
SELECT ROUND(AVG(quantity * unit_price * (1 - discount)), 2) AS avg_order_value,
       MIN(quantity * unit_price * (1 - discount))           AS smallest_order,
       MAX(quantity * unit_price * (1 - discount))           AS biggest_order
FROM orders;
-- Expected result: 1 row
--   avg_order_value | smallest_order | biggest_order
--   ----------------+----------------+--------------
--   2940.93         | 139.3          | 149990.0
-- The Rs 1,49,990 order is one of the 3 genuine bulk orders
-- (10 smartphones) we decided to KEEP in Module 2.

-- Q3. COUNT(*) vs COUNT(column): COUNT(column) skips NULLs.
SELECT COUNT(*)      AS all_orders,
       COUNT(rating) AS rated_orders,
       ROUND(AVG(rating), 2) AS avg_rating
FROM orders;
-- Expected result: 1 row
--   all_orders | rated_orders | avg_rating
--   -----------+--------------+-----------
--   5000       | 4740         | 3.96
-- AVG(rating) also ignores the 260 NULLs: it averages only 4,740 ratings.

-- Q4. GROUP BY: one row per city (the "buckets" drawn on the board).
SELECT city,
       COUNT(*) AS orders,
       ROUND(SUM(quantity * unit_price * (1 - discount)), 2) AS revenue
FROM orders
GROUP BY city
ORDER BY revenue DESC;
-- Expected result: 10 rows
--   city      | orders | revenue
--   ----------+--------+-----------
--   Delhi     | 804    | 2323405.4
--   Bengaluru | 736    | 2256613.25
--   Mumbai    | 759    | 2090206.0
--   Hyderabad | 495    | 1494616.75
--   Pune      | 451    | 1387698.3
--   Chennai   | 442    | 1333558.9
--   Kolkata   | 414    | 1237204.2
--   Ahmedabad | 303    | 1065043.05
--   Lucknow   | 326    | 791223.65
--   Jaipur    | 270    | 725080.2
-- Delhi is the top revenue city.

-- Q5. Orders by payment mode (most popular first).
SELECT payment_mode,
       COUNT(*) AS orders
FROM orders
GROUP BY payment_mode
ORDER BY orders DESC;
-- Expected result: 6 rows
--   payment_mode | orders
--   -------------+-------
--   UPI          | 2057
--   COD          | 983
--   Credit Card  | 888
--   Debit Card   | 685
--   Net Banking  | 297
--   Unknown      | 90

-- Q6. Return rate by city. returned = 'Y' gives 1 (true) or 0 (false),
--     so the AVG of it is the share of returned orders.
SELECT city,
       COUNT(*) AS orders,
       SUM(returned = 'Y') AS returns,
       ROUND(100.0 * AVG(returned = 'Y'), 1) AS return_rate_pct
FROM orders
GROUP BY city
ORDER BY return_rate_pct DESC;
-- Expected result: 10 rows
--   city      | orders | returns | return_rate_pct
--   ----------+--------+---------+----------------
--   Pune      | 451    | 146     | 32.4
--   Kolkata   | 414    | 59      | 14.3
--   Ahmedabad | 303    | 43      | 14.2
--   Lucknow   | 326    | 44      | 13.5
--   Jaipur    | 270    | 36      | 13.3
--   Hyderabad | 495    | 63      | 12.7
--   Chennai   | 442    | 56      | 12.7
--   Bengaluru | 736    | 89      | 12.1
--   Delhi     | 804    | 82      | 10.2
--   Mumbai    | 759    | 69      | 9.1
-- Pune 32.4% vs about 10-14% everywhere else. Big business problem!

-- Q7. Overall return rate for comparison.
SELECT ROUND(100.0 * AVG(returned = 'Y'), 1) AS overall_return_rate_pct
FROM orders;
-- Expected result: 1 row
--   overall_return_rate_pct
--   -----------------------
--   13.7

-- Q8. GROUP BY two columns: orders per city per payment mode.
SELECT city, payment_mode, COUNT(*) AS orders
FROM orders
GROUP BY city, payment_mode
ORDER BY city, orders DESC
LIMIT 6;
-- Expected result: 6 rows
--   city      | payment_mode | orders
--   ----------+--------------+-------
--   Ahmedabad | UPI          | 147
--   Ahmedabad | COD          | 55
--   Ahmedabad | Credit Card  | 46
--   Ahmedabad | Debit Card   | 35
--   Ahmedabad | Net Banking  | 13
--   Ahmedabad | Unknown      | 7

-- Q9. Products per category with min / max / average list price.
SELECT category,
       COUNT(*)                  AS products,
       MIN(list_price)           AS cheapest,
       MAX(list_price)           AS costliest,
       ROUND(AVG(list_price), 0) AS avg_price
FROM products
GROUP BY category
ORDER BY products DESC, category;
-- Expected result: 5 rows
--   category    | products | cheapest | costliest | avg_price
--   ------------+----------+----------+-----------+----------
--   Beauty      | 12       | 199      | 1799      | 703.0
--   Books       | 12       | 249      | 1099      | 541.0
--   Electronics | 12       | 399      | 18999     | 4457.0
--   Fashion     | 12       | 499      | 2999      | 1607.0
--   Home        | 12       | 399      | 5499      | 1716.0

-- Q10. WHERE vs HAVING.
--      WHERE filters ROWS before grouping.
--      HAVING filters GROUPS after grouping (can use COUNT, SUM ...).
--      Cities with more than 500 orders:
SELECT city, COUNT(*) AS orders
FROM orders
GROUP BY city
HAVING COUNT(*) > 500
ORDER BY orders DESC;
-- Expected result: 3 rows
--   city      | orders
--   ----------+-------
--   Delhi     | 804
--   Mumbai    | 759
--   Bengaluru | 736

-- Q11. WHERE and HAVING together:
--      among RETURNED orders only, which cities have 60+ returns?
SELECT city, COUNT(*) AS returns
FROM orders
WHERE returned = 'Y'
GROUP BY city
HAVING COUNT(*) >= 60
ORDER BY returns DESC;
-- Expected result: 5 rows
--   city      | returns
--   ----------+--------
--   Pune      | 146
--   Bengaluru | 89
--   Delhi     | 82
--   Mumbai    | 69
--   Hyderabad | 63

-- Q12. Loyal customers: customers with 15 or more orders.
SELECT customer_id, COUNT(*) AS orders
FROM orders
GROUP BY customer_id
HAVING COUNT(*) >= 15
ORDER BY orders DESC, customer_id
LIMIT 5;
-- Expected result: 5 rows
--   customer_id | orders
--   ------------+-------
--   C0612       | 21
--   C0155       | 19
--   C0757       | 17
--   C0057       | 16
--   C0227       | 16
-- (17 customers in total have 15+ orders. Remove LIMIT to see all.)
