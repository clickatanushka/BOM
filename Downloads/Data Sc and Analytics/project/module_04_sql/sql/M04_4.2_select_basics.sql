-- =====================================================================
-- ShopKart SQL | Video 4.2 - SELECT, FROM, LIMIT, aliases, DISTINCT
-- Tool : sqliteonline.com with shopkart.db open
-- Story: shopkart.db = the orders data we cleaned in Module 2, loaded
--        into a database together with customers and products.
-- =====================================================================

-- Q1. Your first query: show every column (*) of 5 orders.
--     FROM says which table, LIMIT says how many rows to show.
SELECT *
FROM orders
LIMIT 5;
-- Expected result: 5 rows
--   order_id | order_date | customer_id | product_id | quantity | unit_price | discount | city    | payment_mode | delivery_days | rating | returned
--   ---------+------------+-------------+------------+----------+------------+----------+---------+--------------+---------------+--------+---------
--   O10001   | 2025-01-01 | C0593       | P048       | 6        | 362        | 0.2      | Delhi   | COD          | 4             | 2      | N
--   O10002   | 2025-01-01 | C0367       | P049       | 2        | 300        | 0.05     | Chennai | Debit Card   | 4             | 5      | N
--   O10003   | 2025-01-01 | C0707       | P020       | 1        | 2258       | 0.05     | Delhi   | Debit Card   | 2             | 3      | N
--   O10004   | 2025-01-01 | C0118       | P026       | 2        | 2020       | 0.15     | Lucknow | COD          | 4             | 4      | Y
--   O10005   | 2025-01-01 | C0238       | P026       | 2        | 1937       | 0.1      | Chennai | UPI          | 2             | 4      | N

-- Q2. Pick only the columns you need (comma-separated).
SELECT order_id, order_date, city, quantity, unit_price
FROM orders
LIMIT 5;
-- Expected result: 5 rows
--   order_id | order_date | city    | quantity | unit_price
--   ---------+------------+---------+----------+-----------
--   O10001   | 2025-01-01 | Delhi   | 6        | 362
--   O10002   | 2025-01-01 | Chennai | 2        | 300
--   O10003   | 2025-01-01 | Delhi   | 1        | 2258
--   O10004   | 2025-01-01 | Lucknow | 2        | 2020
--   O10005   | 2025-01-01 | Chennai | 2        | 1937

-- Q3. Aliases with AS: rename columns in the output only.
--     The table itself does not change.
SELECT product_name AS product,
       category     AS dept,
       list_price   AS price_rs
FROM products
LIMIT 5;
-- Expected result: 5 rows
--   product             | dept        | price_rs
--   --------------------+-------------+---------
--   Wireless Earbuds    | Electronics | 1999
--   Bluetooth Speaker   | Electronics | 2499
--   Smartwatch          | Electronics | 3999
--   Power Bank 10000mAh | Electronics | 1299
--   USB-C Charger       | Electronics | 899

-- Q4. A calculated column: revenue of each order line.
--     revenue = quantity * unit_price * (1 - discount)
--     (same formula we used in the Module 2 spreadsheet)
SELECT order_id,
       quantity,
       unit_price,
       discount,
       quantity * unit_price * (1 - discount) AS revenue
FROM orders
LIMIT 5;
-- Expected result: 5 rows
--   order_id | quantity | unit_price | discount | revenue
--   ---------+----------+------------+----------+--------
--   O10001   | 6        | 362        | 0.2      | 1737.6
--   O10002   | 2        | 300        | 0.05     | 570.0
--   O10003   | 1        | 2258       | 0.05     | 2145.1
--   O10004   | 2        | 2020       | 0.15     | 3434.0
--   O10005   | 2        | 1937       | 0.1      | 3486.6
-- Note O10001: 6 * 362 * 0.8 = 1737.6. Computers store decimals in
-- binary, so you may see 1737.6000000000001. Video 4.7 fixes this
-- with ROUND().

-- Q5. Margin per unit for each product (list price minus cost).
SELECT product_name,
       list_price,
       cost_price,
       list_price - cost_price AS margin_per_unit
FROM products
LIMIT 5;
-- Expected result: 5 rows
--   product_name        | list_price | cost_price | margin_per_unit
--   --------------------+------------+------------+----------------
--   Wireless Earbuds    | 1999       | 1600       | 399
--   Bluetooth Speaker   | 2499       | 1940       | 559
--   Smartwatch          | 3999       | 3230       | 769
--   Power Bank 10000mAh | 1299       | 1030       | 269
--   USB-C Charger       | 899        | 670        | 229

-- Q6. DISTINCT: which cities do we deliver to? (no repeats)
SELECT DISTINCT city
FROM orders;
-- Expected result: 10 rows
--   city
--   ---------
--   Delhi
--   Chennai
--   Lucknow
--   Kolkata
--   Pune
--   Hyderabad
--   Ahmedabad
--   Mumbai
--   Bengaluru
--   Jaipur

-- Q7. DISTINCT payment modes. "Unknown" = the blanks we filled
--     during cleaning in Module 2.
SELECT DISTINCT payment_mode
FROM orders;
-- Expected result: 6 rows
--   payment_mode
--   ------------
--   COD
--   Debit Card
--   UPI
--   Credit Card
--   Net Banking
--   Unknown

-- Q8. DISTINCT on two columns = unique combinations.
--     Which payment modes are used in which city? (10 cities x 6 modes)
SELECT DISTINCT city, payment_mode
FROM orders
ORDER BY city, payment_mode
LIMIT 6;
-- (ORDER BY sorts - we learn it properly in Video 4.3.)
-- Expected result: 6 rows
--   city      | payment_mode
--   ----------+-------------
--   Ahmedabad | COD
--   Ahmedabad | Credit Card
--   Ahmedabad | Debit Card
--   Ahmedabad | Net Banking
--   Ahmedabad | UPI
--   Ahmedabad | Unknown

-- Q9. Count rows and count unique customers who ordered.
SELECT COUNT(*)                    AS total_orders,
       COUNT(DISTINCT customer_id) AS customers_who_ordered
FROM orders;
-- Expected result: 1 row
--   total_orders | customers_who_ordered
--   -------------+----------------------
--   5000         | 758
