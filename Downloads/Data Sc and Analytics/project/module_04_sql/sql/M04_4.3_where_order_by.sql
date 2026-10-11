-- =====================================================================
-- ShopKart SQL | Video 4.3 - WHERE, operators, ORDER BY
-- Business question: "Show me only the orders I care about, sorted."
-- Text values go in 'single quotes'. Numbers do not.
-- =====================================================================

-- Q1. Orders from Pune only (= means "equals").
SELECT order_id, order_date, city, returned
FROM orders
WHERE city = 'Pune'
LIMIT 5;
-- Expected result: 5 rows
--   order_id | order_date | city | returned
--   ---------+------------+------+---------
--   O10008   | 2025-01-01 | Pune | N
--   O10015   | 2025-01-02 | Pune | N
--   O10026   | 2025-01-03 | Pune | N
--   O10056   | 2025-01-05 | Pune | Y
--   O10061   | 2025-01-06 | Pune | N

-- Q2. How many Pune orders? (WHERE runs before COUNT)
SELECT COUNT(*) AS pune_orders
FROM orders
WHERE city = 'Pune';
-- Expected result: 1 row
--   pune_orders
--   -----------
--   451

-- Q3. Comparison operators: > >= < <= and <> (not equal).
--     Big orders: 4 or more units.
SELECT COUNT(*) AS big_orders
FROM orders
WHERE quantity >= 4;
-- Expected result: 1 row
--   big_orders
--   ----------
--   253

-- Q4. AND: both conditions must be true.
--     Pune orders that were returned.
SELECT COUNT(*) AS pune_returns
FROM orders
WHERE city = 'Pune'
  AND returned = 'Y';
-- Expected result: 1 row
--   pune_returns
--   ------------
--   146
-- 146 out of 451 Pune orders were returned = 32.4%. Remember this!

-- Q5. OR: at least one condition true.
--     Cash-on-delivery orders OR orders of 4+ units.
SELECT COUNT(*) AS cod_or_big
FROM orders
WHERE payment_mode = 'COD'
   OR quantity >= 4;
-- Expected result: 1 row
--   cod_or_big
--   ----------
--   1180

-- Q6. IN: a shorter way to write many ORs on one column.
--     Orders from the three metro cities.
SELECT COUNT(*) AS metro_orders
FROM orders
WHERE city IN ('Delhi', 'Mumbai', 'Bengaluru');
-- Expected result: 1 row
--   metro_orders
--   ------------
--   2299

-- Q7. BETWEEN: a range, both ends included.
--     Orders placed in November 2025 (festive season).
--     Dates are stored as text 'YYYY-MM-DD', which sorts correctly.
SELECT COUNT(*) AS nov_orders
FROM orders
WHERE order_date BETWEEN '2025-11-01' AND '2025-11-30';
-- Expected result: 1 row
--   nov_orders
--   ----------
--   620

-- Q8. BETWEEN on numbers: products priced Rs 500 to Rs 1,000.
SELECT product_name, category, list_price
FROM products
WHERE list_price BETWEEN 500 AND 1000;
-- Expected result: 12 rows
--   product_name              | category    | list_price
--   --------------------------+-------------+-----------
--   USB-C Charger             | Electronics | 899
--   Leather Belt              | Fashion     | 699
--   Sunglasses                | Fashion     | 999
--   Bedsheet Set              | Home        | 999
--   Wall Clock                | Home        | 699
--   Storage Box Set           | Home        | 799
--   Cushion Covers            | Home        | 599
--   Python Crash Course       | Books       | 899
--   Data Science for Business | Books       | 999
--   Sapiens                   | Books       | 599
--   Lipstick                  | Beauty      | 599
--   Face Serum                | Beauty      | 799

-- Q9. LIKE with % (any number of characters): names containing "phone".
--     In SQLite, LIKE ignores upper/lower case for English letters.
SELECT product_id, product_name, list_price
FROM products
WHERE product_name LIKE '%phone%';
-- Expected result: 2 rows
--   product_id | product_name | list_price
--   -----------+--------------+-----------
--   P008       | Phone Case   | 399
--   P009       | Smartphone   | 14999

-- Q10. IS NULL: orders where the customer did NOT give a rating.
--      Never write  rating = NULL  -- it always finds nothing.
SELECT COUNT(*) AS unrated_orders
FROM orders
WHERE rating IS NULL;
-- Expected result: 1 row
--   unrated_orders
--   --------------
--   260

-- Q11. IS NOT NULL: the rated orders.
SELECT COUNT(*) AS rated_orders
FROM orders
WHERE rating IS NOT NULL;
-- Expected result: 1 row
--   rated_orders
--   ------------
--   4740

-- Q12. Mixing AND with OR: use brackets so SQL reads it your way.
--      Returned orders from Pune or Kolkata.
SELECT COUNT(*) AS returns_pune_kolkata
FROM orders
WHERE returned = 'Y'
  AND (city = 'Pune' OR city = 'Kolkata');
-- Expected result: 1 row
--   returns_pune_kolkata
--   --------------------
--   205

-- Q13. ORDER BY ... DESC: most expensive products first.
SELECT product_name, category, list_price
FROM products
ORDER BY list_price DESC
LIMIT 5;
-- Expected result: 5 rows
--   product_name        | category    | list_price
--   --------------------+-------------+-----------
--   Tablet              | Electronics | 18999
--   Smartphone          | Electronics | 14999
--   Air Fryer           | Home        | 5499
--   Smartwatch          | Electronics | 3999
--   Mechanical Keyboard | Electronics | 3499

-- Q14. ORDER BY ... ASC (default): cheapest products first.
SELECT product_name, category, list_price
FROM products
ORDER BY list_price ASC, product_name
LIMIT 5;
-- Expected result: 5 rows
--   product_name        | category | list_price
--   --------------------+----------+-----------
--   Kajal               | Beauty   | 199
--   Hair Oil            | Beauty   | 249
--   Think and Grow Rich | Books    | 249
--   Face Wash           | Beauty   | 299
--   Ikigai              | Books    | 299

-- Q15. Sort by two columns: category A-Z, then price high to low.
SELECT category, product_name, list_price
FROM products
ORDER BY category ASC, list_price DESC
LIMIT 6;
-- Expected result: 6 rows
--   category | product_name    | list_price
--   ---------+-----------------+-----------
--   Beauty   | Hair Dryer      | 1799
--   Beauty   | Beard Trimmer   | 1499
--   Beauty   | Perfume         | 1299
--   Beauty   | Face Serum      | 799
--   Beauty   | Lipstick        | 599
--   Beauty   | Sunscreen SPF50 | 499

-- Q16. Putting it together: the 5 biggest Delhi orders by revenue.
SELECT order_id, order_date, quantity, unit_price, discount,
       quantity * unit_price * (1 - discount) AS revenue
FROM orders
WHERE city = 'Delhi'
ORDER BY revenue DESC
LIMIT 5;
-- Expected result: 5 rows
--   order_id | order_date | quantity | unit_price | discount | revenue
--   ---------+------------+----------+------------+----------+---------
--   O14848   | 2025-12-20 | 3        | 18491      | 0.15     | 47152.05
--   O14858   | 2025-12-21 | 3        | 15256      | 0.1      | 41191.2
--   O10627   | 2025-03-02 | 2        | 19424      | 0.0      | 38848.0
--   O11035   | 2025-04-05 | 2        | 18056      | 0.0      | 36112.0
--   O10520   | 2025-02-20 | 2        | 19792      | 0.1      | 35625.6
