-- =====================================================================
-- ShopKart SQL | Video 4.6 - LEFT JOIN & others, 3-table join
-- Business question: "Which customers signed up but NEVER ordered?"
-- INNER JOIN keeps only matches -> those customers would vanish.
-- LEFT JOIN keeps EVERY row of the left table; where there is no
-- match, the right-side columns come back as NULL.
-- =====================================================================

-- Q1. INNER vs LEFT: count rows.
--     INNER: customers who have orders, one row per order.
SELECT COUNT(*) AS inner_rows
FROM customers AS c
INNER JOIN orders AS o
        ON c.customer_id = o.customer_id;
-- Expected result: 1 row
--   inner_rows
--   ----------
--   5000

-- Q2. LEFT: same 5,000 rows + 1 extra row for each customer with no order.
SELECT COUNT(*) AS left_rows
FROM customers AS c
LEFT JOIN orders AS o
       ON c.customer_id = o.customer_id;
-- Expected result: 1 row
--   left_rows
--   ---------
--   5042
-- 5,042 - 5,000 = 42 extra rows = 42 customers without any order.

-- Q3. See the NULLs: customers with no matching order.
SELECT c.customer_id, c.name, c.city, c.membership,
       o.order_id
FROM customers AS c
LEFT JOIN orders AS o
       ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
LIMIT 5;
-- Expected result: 5 rows
--   customer_id | name           | city    | membership | order_id
--   ------------+----------------+---------+------------+---------
--   C0008       | Isha Reddy     | Chennai | Free       | NULL
--   C0038       | Isha Singh     | Mumbai  | Prime      | NULL
--   C0046       | Aditya Nair    | Mumbai  | Free       | NULL
--   C0073       | Kritika Das    | Lucknow | Prime      | NULL
--   C0087       | Tanvi Banerjee | Jaipur  | Free       | NULL

-- Q4. How many customers never ordered?
SELECT COUNT(*) AS never_ordered
FROM customers AS c
LEFT JOIN orders AS o
       ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
-- Expected result: 1 row
--   never_ordered
--   -------------
--   42
-- 42 customers to target with a "first order" coupon.

-- Q5. Split the 42 by membership. 13 of them even pay for Prime!
SELECT c.membership, COUNT(*) AS never_ordered
FROM customers AS c
LEFT JOIN orders AS o
       ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
GROUP BY c.membership;
-- Expected result: 2 rows
--   membership | never_ordered
--   -----------+--------------
--   Free       | 29
--   Prime      | 13

-- Q6. Orders per customer INCLUDING zero.
--     COUNT(o.order_id) counts only non-NULL ids, so no-order
--     customers correctly show 0 (COUNT(*) would wrongly show 1).
SELECT c.customer_id, c.name, COUNT(o.order_id) AS orders
FROM customers AS c
LEFT JOIN orders AS o
       ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY orders ASC, c.customer_id
LIMIT 5;
-- Expected result: 5 rows
--   customer_id | name           | orders
--   ------------+----------------+-------
--   C0008       | Isha Reddy     | 0
--   C0038       | Isha Singh     | 0
--   C0046       | Aditya Nair    | 0
--   C0073       | Kritika Das    | 0
--   C0087       | Tanvi Banerjee | 0

-- Q7. 3-table join: order + customer + product in one result.
SELECT o.order_id,
       c.name       AS customer,
       c.membership,
       p.product_name,
       p.category,
       o.quantity * o.unit_price * (1 - o.discount) AS revenue
FROM orders AS o
INNER JOIN customers AS c ON o.customer_id = c.customer_id
INNER JOIN products  AS p ON o.product_id  = p.product_id
LIMIT 5;
-- Expected result: 5 rows
--   order_id | customer       | membership | product_name    | category | revenue
--   ---------+----------------+------------+-----------------+----------+--------
--   O10001   | Kavya Khan     | Prime      | Wings of Fire   | Books    | 1737.6
--   O10002   | Yash Khan      | Free       | Face Wash       | Beauty   | 570.0
--   O10003   | Rohit Kulkarni | Prime      | Saree           | Fashion  | 2145.1
--   O10004   | Harsh Khan     | Free       | Pressure Cooker | Home     | 3434.0
--   O10005   | Anjali Rao     | Free       | Pressure Cooker | Home     | 3486.6

-- Q8. 3-table join + GROUP BY: revenue by membership AND category.
SELECT c.membership,
       p.category,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue
FROM orders AS o
INNER JOIN customers AS c ON o.customer_id = c.customer_id
INNER JOIN products  AS p ON o.product_id  = p.product_id
GROUP BY c.membership, p.category
ORDER BY c.membership, revenue DESC;
-- Expected result: 10 rows
--   membership | category    | revenue
--   -----------+-------------+-----------
--   Free       | Electronics | 3347966.9
--   Free       | Fashion     | 1455160.8
--   Free       | Home        | 1252160.2
--   Free       | Beauty      | 399108.75
--   Free       | Books       | 323462.9
--   Prime      | Electronics | 3983051.15
--   Prime      | Fashion     | 1666184.8
--   Prime      | Home        | 1402887.1
--   Prime      | Beauty      | 478531.6
--   Prime      | Books       | 396135.5

-- Q9. Top 5 customers by total spend (name from customers table).
SELECT c.name, c.city, c.membership,
       COUNT(*) AS orders,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS total_spend
FROM orders AS o
INNER JOIN customers AS c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name, c.city, c.membership
ORDER BY total_spend DESC
LIMIT 5;
-- Expected result: 5 rows
--   name         | city      | membership | orders | total_spend
--   -------------+-----------+------------+--------+------------
--   Dev Nair     | Bengaluru | Prime      | 10     | 182349.0
--   Nikhil Iyer  | Hyderabad | Prime      | 16     | 170213.2
--   Divya Rao    | Mumbai    | Free       | 5      | 143639.5
--   Pooja Sharma | Ahmedabad | Prime      | 11     | 119576.6
--   Aman Rao     | Mumbai    | Prime      | 13     | 111936.5

-- ---------------------------------------------------------------------
-- RIGHT JOIN and FULL OUTER JOIN (theory)
-- RIGHT JOIN  = LEFT JOIN with the tables swapped: keeps every row of
--               the RIGHT table.
-- FULL JOIN   = keeps every row from BOTH tables, NULLs on either side.
-- SQLite added RIGHT and FULL JOIN in version 3.39 (2022). Older
-- SQLite versions do not have them. In this course we always write
-- LEFT JOIN (put the "keep all" table first). Any RIGHT JOIN can be
-- rewritten as a LEFT JOIN by swapping the table order.
-- Example of the same idea as Q2 written as LEFT JOIN:
--   customers LEFT JOIN orders   ==   orders RIGHT JOIN customers
-- ---------------------------------------------------------------------
