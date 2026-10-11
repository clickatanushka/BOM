-- =====================================================================
-- ShopKart SQL | Video 4.8 - Subqueries, CTE, business case
-- Business question from the CEO: "What are the top 3 categories by
-- revenue for Prime members vs Free members?"
-- =====================================================================

-- Q1. A SUBQUERY is a query inside a query, in brackets.
--     First, the average list price on its own:
SELECT ROUND(AVG(list_price), 2) AS avg_list_price
FROM products;
-- Expected result: 1 row
--   avg_list_price
--   --------------
--   1804.83

-- Q2. Products priced ABOVE the average - without typing 1804.83.
--     The inner query runs first and returns one number.
SELECT product_name, category, list_price
FROM products
WHERE list_price > (SELECT AVG(list_price) FROM products)
ORDER BY list_price DESC;
-- Expected result: 15 rows
--   product_name        | category    | list_price
--   --------------------+-------------+-----------
--   Tablet              | Electronics | 18999
--   Smartphone          | Electronics | 14999
--   Air Fryer           | Home        | 5499
--   Smartwatch          | Electronics | 3999
--   Mechanical Keyboard | Electronics | 3499
--   Mixer Grinder       | Home        | 3299
--   Running Shoes       | Fashion     | 2999
--   Bluetooth Speaker   | Electronics | 2499
--   Sneakers            | Fashion     | 2499
--   Dinner Set          | Home        | 2499
--   Saree               | Fashion     | 2299
--   Webcam HD           | Electronics | 2199
--   Wireless Earbuds    | Electronics | 1999
--   Pressure Cooker     | Home        | 1999
--   Analog Watch        | Fashion     | 1899
-- 15 of 60 products are above average (a few expensive gadgets pull
-- the average up - remember mean vs median from Module 3).

-- Q3. Subquery with IN: customers who bought a Smartphone (P009).
SELECT COUNT(*) AS smartphone_buyers
FROM customers
WHERE customer_id IN (SELECT customer_id
                      FROM orders
                      WHERE product_id = 'P009');
-- Expected result: 1 row
--   smartphone_buyers
--   -----------------
--   75

-- Q4. Subquery in FROM: average number of orders per customer.
SELECT ROUND(AVG(order_count), 2) AS avg_orders_per_customer,
       MAX(order_count)           AS max_orders
FROM (SELECT customer_id, COUNT(*) AS order_count
      FROM orders
      GROUP BY customer_id) AS per_customer;
-- Expected result: 1 row
--   avg_orders_per_customer | max_orders
--   ------------------------+-----------
--   6.6                     | 21

-- Q5. A CTE (Common Table Expression) = a named subquery written
--     at the TOP with WITH. Same answer as Q4, easier to read.
WITH per_customer AS (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT ROUND(AVG(order_count), 2) AS avg_orders_per_customer,
       MAX(order_count)           AS max_orders
FROM per_customer;
-- Expected result: 1 row
--   avg_orders_per_customer | max_orders
--   ------------------------+-----------
--   6.6                     | 21

-- Q6. CTE step 1 of the business case: revenue per membership+category.
WITH member_category AS (
    SELECT c.membership,
           p.category,
           ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue
    FROM orders AS o
    JOIN customers AS c ON o.customer_id = c.customer_id
    JOIN products  AS p ON o.product_id  = p.product_id
    GROUP BY c.membership, p.category
)
SELECT *
FROM member_category
ORDER BY membership, revenue DESC;
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

-- Q7. Business case: TOP 3 categories by revenue for Prime vs Free.
--     Step 2: rank categories inside each membership group.
--     A category's rank = 1 + number of categories in the SAME
--     membership with MORE revenue (a correlated subquery).
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
    SELECT m.membership,
           m.category,
           m.revenue,
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
-- Why a second CTE "ranked"? WHERE runs BEFORE SELECT (logical order),
-- so WHERE cannot see a column created in the same SELECT. Making it
-- a CTE first gives WHERE a real column to filter on.
-- Expected result: 6 rows
--   membership | category    | revenue    | rank_in_group
--   -----------+-------------+------------+--------------
--   Free       | Electronics | 3347966.9  | 1
--   Free       | Fashion     | 1455160.8  | 2
--   Free       | Home        | 1252160.2  | 3
--   Prime      | Electronics | 3983051.15 | 1
--   Prime      | Fashion     | 1666184.8  | 2
--   Prime      | Home        | 1402887.1  | 3
-- Answer: SAME top 3 for both groups - Electronics, Fashion, Home.
-- Prime earns more in every category because Prime members order
-- more often (about 9.8 orders each vs 4.8 for Free).

-- Q8. Optional, for curious learners: the same ranking with a window
--     function (works in SQLite 3.25+ and on sqliteonline.com).
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
    SELECT membership, category, revenue,
           RANK() OVER (PARTITION BY membership ORDER BY revenue DESC) AS rnk
    FROM member_category
)
SELECT membership, category, revenue, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY membership, rnk;
-- Expected result: 6 rows
--   membership | category    | revenue    | rnk
--   -----------+-------------+------------+----
--   Free       | Electronics | 3347966.9  | 1
--   Free       | Fashion     | 1455160.8  | 2
--   Free       | Home        | 1252160.2  | 3
--   Prime      | Electronics | 3983051.15 | 1
--   Prime      | Fashion     | 1666184.8  | 2
--   Prime      | Home        | 1402887.1  | 3

-- Q9. Why do Prime members earn more? Orders per customer by membership.
WITH per_customer AS (
    SELECT o.customer_id, c.membership,
           COUNT(*) AS orders,
           SUM(o.quantity * o.unit_price * (1 - o.discount)) AS spend
    FROM orders AS o
    JOIN customers AS c ON o.customer_id = c.customer_id
    GROUP BY o.customer_id, c.membership
)
SELECT membership,
       COUNT(*)                             AS active_customers,
       ROUND(AVG(orders), 2)                AS avg_orders_per_customer,
       ROUND(SUM(spend) / SUM(orders), 2)   AS avg_order_value
FROM per_customer
GROUP BY membership;
-- Expected result: 2 rows
--   membership | active_customers | avg_orders_per_customer | avg_order_value
--   -----------+------------------+-------------------------+----------------
--   Free       | 482              | 4.77                    | 2949.46
--   Prime      | 276              | 9.79                    | 2933.68
-- Same order value, but Prime customers order about twice as often.
