-- =====================================================================
-- ShopKart SQL | Video 4.1 - What is a database (keys, schema)
-- Tool : sqliteonline.com -> File -> Open DB -> shopkart.db
-- Goal : look around the database BEFORE writing analysis queries.
-- This is the first code file of the whole course. Run one query at a
-- time: select (highlight) the query, then click Run (or Shift+Enter).
-- Lines that start with -- are comments. SQL ignores them.
-- =====================================================================

-- Q1. Which tables are inside shopkart.db?
--     sqlite_master is SQLite's own "table of contents".
SELECT name, type
FROM sqlite_master
WHERE type = 'table';
-- Expected result: 3 rows
--   name      | type
--   ----------+------
--   customers | table
--   products  | table
--   orders    | table

-- Q2. What columns does the orders table have, and which is the key?
--     pk = 1 marks the PRIMARY KEY column (order_id).
PRAGMA table_info(orders);
-- Expected result: 12 rows
--   cid | name          | type    | notnull | dflt_value | pk
--   ----+---------------+---------+---------+------------+---
--   0   | order_id      | TEXT    | 0       | NULL       | 1
--   1   | order_date    | TEXT    | 0       | NULL       | 0
--   2   | customer_id   | TEXT    | 0       | NULL       | 0
--   3   | product_id    | TEXT    | 0       | NULL       | 0
--   4   | quantity      | INTEGER | 0       | NULL       | 0
--   5   | unit_price    | INTEGER | 0       | NULL       | 0
--   6   | discount      | REAL    | 0       | NULL       | 0
--   7   | city          | TEXT    | 0       | NULL       | 0
--   8   | payment_mode  | TEXT    | 0       | NULL       | 0
--   9   | delivery_days | INTEGER | 0       | NULL       | 0
--   10  | rating        | INTEGER | 0       | NULL       | 0
--   11  | returned      | TEXT    | 0       | NULL       | 0

-- Q3. Same for customers (primary key: customer_id).
PRAGMA table_info(customers);
-- Expected result: 7 rows
--   cid | name        | type    | notnull | dflt_value | pk
--   ----+-------------+---------+---------+------------+---
--   0   | customer_id | TEXT    | 0       | NULL       | 1
--   1   | name        | TEXT    | 0       | NULL       | 0
--   2   | gender      | TEXT    | 0       | NULL       | 0
--   3   | age         | INTEGER | 0       | NULL       | 0
--   4   | city        | TEXT    | 0       | NULL       | 0
--   5   | signup_date | TEXT    | 0       | NULL       | 0
--   6   | membership  | TEXT    | 0       | NULL       | 0

-- Q4. Same for products (primary key: product_id).
PRAGMA table_info(products);
-- Expected result: 5 rows
--   cid | name         | type    | notnull | dflt_value | pk
--   ----+--------------+---------+---------+------------+---
--   0   | product_id   | TEXT    | 0       | NULL       | 1
--   1   | product_name | TEXT    | 0       | NULL       | 0
--   2   | category     | TEXT    | 0       | NULL       | 0
--   3   | list_price   | INTEGER | 0       | NULL       | 0
--   4   | cost_price   | INTEGER | 0       | NULL       | 0

-- Q5. The full CREATE statement of orders. Look for REFERENCES:
--     that is how the FOREIGN KEYS customer_id and product_id point
--     to the customers and products tables.
SELECT sql
FROM sqlite_master
WHERE name = 'orders';
-- Expected result: 1 row
--   sql
--   --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--   CREATE TABLE orders (order_id TEXT PRIMARY KEY, order_date TEXT, customer_id TEXT REFERENCES customers(customer_id), product_id TEXT REFERENCES products(product_id), quantity INTEGER, unit_price INTEGER, discount REAL, city TEXT, payment_mode TEXT, delivery_days INTEGER, rating INTEGER, returned TEXT)

-- Q6. How many rows in each table? (UNION ALL just stacks results.)
SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM orders
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products;
-- Expected result: 3 rows
--   table_name | row_count
--   -----------+----------
--   orders     | 5000
--   customers  | 800
--   products   | 60

-- Q7. Peek at 3 rows of each table to see what one row means.
--     One row in orders = one order line.
SELECT * FROM orders LIMIT 3;
-- Expected result: 3 rows
--   order_id | order_date | customer_id | product_id | quantity | unit_price | discount | city    | payment_mode | delivery_days | rating | returned
--   ---------+------------+-------------+------------+----------+------------+----------+---------+--------------+---------------+--------+---------
--   O10001   | 2025-01-01 | C0593       | P048       | 6        | 362        | 0.2      | Delhi   | COD          | 4             | 2      | N
--   O10002   | 2025-01-01 | C0367       | P049       | 2        | 300        | 0.05     | Chennai | Debit Card   | 4             | 5      | N
--   O10003   | 2025-01-01 | C0707       | P020       | 1        | 2258       | 0.05     | Delhi   | Debit Card   | 2             | 3      | N

-- Q8. One row in customers = one customer.
SELECT * FROM customers LIMIT 3;
-- Expected result: 3 rows
--   customer_id | name           | gender | age | city    | signup_date | membership
--   ------------+----------------+--------+-----+---------+-------------+-----------
--   C0001       | Neha Kapoor    | Female | 18  | Kolkata | 2023-05-31  | Free
--   C0002       | Sneha Das      | Female | 36  | Delhi   | 2023-01-16  | Prime
--   C0003       | Rohit Kulkarni | Male   | 20  | Delhi   | 2024-07-23  | Prime

-- Q9. One row in products = one product in the catalogue.
SELECT * FROM products LIMIT 3;
-- Expected result: 3 rows
--   product_id | product_name      | category    | list_price | cost_price
--   -----------+-------------------+-------------+------------+-----------
--   P001       | Wireless Earbuds  | Electronics | 1999       | 1600
--   P002       | Bluetooth Speaker | Electronics | 2499       | 1940
--   P003       | Smartwatch        | Electronics | 3999       | 3230
