-- =====================================================================
-- Module 4 practice - ANSWERS (try practice_questions.docx first!)
-- Tool: sqliteonline.com with shopkart.db open.
-- Your query may look different and still be right - compare RESULTS.
-- =====================================================================

-- P1 (Video 4.2). Show the name, city and membership of the first 5 customers.
SELECT name, city, membership
FROM customers
LIMIT 5;
-- Expected result: 5 rows
--   name           | city    | membership
--   ---------------+---------+-----------
--   Neha Kapoor    | Kolkata | Free
--   Sneha Das      | Delhi   | Prime
--   Rohit Kulkarni | Delhi   | Prime
--   Nisha Khan     | Kolkata | Free
--   Priya Khan     | Delhi   | Free

-- P2 (Video 4.2). List each distinct product category exactly once.
SELECT DISTINCT category
FROM products;
-- Expected result: 5 rows
--   category
--   -----------
--   Electronics
--   Fashion
--   Home
--   Books
--   Beauty

-- P3 (Video 4.2). For each product show name, list_price, cost_price and
-- margin_pct = (list_price - cost_price) * 100.0 / list_price. First 5 products.
SELECT product_name, list_price, cost_price,
       ROUND((list_price - cost_price) * 100.0 / list_price, 1) AS margin_pct
FROM products
LIMIT 5;
-- Expected result: 5 rows
--   product_name        | list_price | cost_price | margin_pct
--   --------------------+------------+------------+-----------
--   Wireless Earbuds    | 1999       | 1600       | 20.0
--   Bluetooth Speaker   | 2499       | 1940       | 22.4
--   Smartwatch          | 3999       | 3230       | 19.2
--   Power Bank 10000mAh | 1299       | 1030       | 20.7
--   USB-C Charger       | 899        | 670        | 25.5

-- P4 (Video 4.3). How many orders were paid by UPI with a discount of 20% or more?
SELECT COUNT(*) AS upi_big_discount
FROM orders
WHERE payment_mode = 'UPI'
  AND discount >= 0.2;
-- Expected result: 1 row
--   upi_big_discount
--   ----------------
--   499

-- P5 (Video 4.3). List Books priced between Rs 300 and Rs 500, cheapest first.
SELECT product_name, list_price
FROM products
WHERE category = 'Books'
  AND list_price BETWEEN 300 AND 500
ORDER BY list_price, product_name;
-- Expected result: 5 rows
--   product_name            | list_price
--   ------------------------+-----------
--   Rich Dad Poor Dad       | 349
--   Wings of Fire           | 349
--   The Psychology of Money | 399
--   Deep Work               | 449
--   Atomic Habits           | 499

-- P6 (Video 4.3). How many customers have a name starting with 'A'?
SELECT COUNT(*) AS names_starting_a
FROM customers
WHERE name LIKE 'A%';
-- Expected result: 1 row
--   names_starting_a
--   ----------------
--   142

-- P7 (Video 4.3). How many orders from Chennai or Hyderabad had NO rating?
SELECT COUNT(*) AS unrated
FROM orders
WHERE city IN ('Chennai', 'Hyderabad')
  AND rating IS NULL;
-- Expected result: 1 row
--   unrated
--   -------
--   40

-- P8 (Video 4.4). Average delivery days per city, slowest city first.
SELECT city, ROUND(AVG(delivery_days), 2) AS avg_delivery_days
FROM orders
GROUP BY city
ORDER BY avg_delivery_days DESC;
-- Expected result: 10 rows
--   city      | avg_delivery_days
--   ----------+------------------
--   Pune      | 5.77
--   Lucknow   | 5.75
--   Jaipur    | 5.63
--   Hyderabad | 3.81
--   Delhi     | 3.76
--   Kolkata   | 3.75
--   Chennai   | 3.74
--   Ahmedabad | 3.74
--   Bengaluru | 3.7
--   Mumbai    | 3.69

-- P9 (Video 4.4). Which payment modes have more than 800 orders?
SELECT payment_mode, COUNT(*) AS orders
FROM orders
GROUP BY payment_mode
HAVING COUNT(*) > 800
ORDER BY orders DESC;
-- Expected result: 3 rows
--   payment_mode | orders
--   -------------+-------
--   UPI          | 2057
--   COD          | 983
--   Credit Card  | 888

-- P10 (Video 4.5). Total units sold per category (join orders with products).
SELECT p.category, SUM(o.quantity) AS units_sold
FROM orders AS o
JOIN products AS p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY units_sold DESC;
-- Expected result: 5 rows
--   category    | units_sold
--   ------------+-----------
--   Fashion     | 2270
--   Electronics | 1972
--   Home        | 1720
--   Books       | 1497
--   Beauty      | 1496

-- P11 (Video 4.5). Revenue by customer gender (join orders with customers).
SELECT c.gender,
       COUNT(*) AS orders,
       ROUND(SUM(o.quantity * o.unit_price * (1 - o.discount)), 2) AS revenue
FROM orders AS o
JOIN customers AS c ON o.customer_id = c.customer_id
GROUP BY c.gender;
-- Expected result: 2 rows
--   gender | orders | revenue
--   -------+--------+----------
--   Female | 2263   | 6843964.3
--   Male   | 2737   | 7860685.4

-- P12 (Video 4.6). How many products were never ordered even once?
SELECT COUNT(*) AS never_sold
FROM products AS p
LEFT JOIN orders AS o ON p.product_id = o.product_id
WHERE o.order_id IS NULL;
-- Expected result: 1 row
--   never_sold
--   ----------
--   0
-- 0: every one of the 60 products sold at least once.

-- P13 (Video 4.6). Which city's customers never ordered? Count the 42 by city.
SELECT c.city, COUNT(*) AS never_ordered
FROM customers AS c
LEFT JOIN orders AS o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
GROUP BY c.city
ORDER BY never_ordered DESC, c.city;
-- Expected result: 10 rows
--   city      | never_ordered
--   ----------+--------------
--   Mumbai    | 9
--   Bengaluru | 6
--   Delhi     | 6
--   Chennai   | 4
--   Hyderabad | 4
--   Pune      | 4
--   Kolkata   | 3
--   Lucknow   | 3
--   Ahmedabad | 2
--   Jaipur    | 1

-- P14 (Video 4.7). Bucket customers by age: '18-24', '25-34', '35+'.
-- How many customers in each bucket?
SELECT CASE
           WHEN age < 25 THEN '18-24'
           WHEN age < 35 THEN '25-34'
           ELSE '35+'
       END AS age_group,
       COUNT(*) AS customers
FROM customers
GROUP BY age_group
ORDER BY age_group;
-- Expected result: 3 rows
--   age_group | customers
--   ----------+----------
--   18-24     | 201
--   25-34     | 401
--   35+       | 198

-- P15 (Video 4.8). Which orders have revenue above the overall average
-- order value? Count them, using a subquery (do not type the average).
SELECT COUNT(*) AS above_avg_orders
FROM orders
WHERE quantity * unit_price * (1 - discount) >
      (SELECT AVG(quantity * unit_price * (1 - discount)) FROM orders);
-- Expected result: 1 row
--   above_avg_orders
--   ----------------
--   1228
-- About 1 in 4 orders is above average: a few big orders pull the mean up.

-- =====================================================================
-- End-of-video tasks (from the recap slides) - answers
-- =====================================================================

-- T4.1. Row counts in each table.
SELECT (SELECT COUNT(*) FROM orders)    AS orders,
       (SELECT COUNT(*) FROM customers) AS customers,
       (SELECT COUNT(*) FROM products)  AS products;
-- Expected result: 1 row
--   orders | customers | products
--   -------+-----------+---------
--   5000   | 800       | 60

-- T4.2. First 10 products with margin.
SELECT product_name, list_price, cost_price,
       list_price - cost_price AS margin
FROM products
LIMIT 10;
-- Expected result: 10 rows
--   product_name        | list_price | cost_price | margin
--   --------------------+------------+------------+-------
--   Wireless Earbuds    | 1999       | 1600       | 399
--   Bluetooth Speaker   | 2499       | 1940       | 559
--   Smartwatch          | 3999       | 3230       | 769
--   Power Bank 10000mAh | 1299       | 1030       | 269
--   USB-C Charger       | 899        | 670        | 229
--   Gaming Mouse        | 1499       | 1220       | 279
--   Mechanical Keyboard | 3499       | 2800       | 699
--   Phone Case          | 399        | 320        | 79
--   Smartphone          | 14999      | 11260      | 3739
--   Tablet              | 18999      | 14750      | 4249

-- T4.3a. Delhi orders paid by COD with quantity 2 or more.
SELECT COUNT(*) AS delhi_cod_2plus
FROM orders
WHERE city = 'Delhi'
  AND payment_mode = 'COD'
  AND quantity >= 2;
-- Expected result: 1 row
--   delhi_cod_2plus
--   ---------------
--   78

-- T4.3b. The 5 cheapest Fashion products.
SELECT product_name, list_price
FROM products
WHERE category = 'Fashion'
ORDER BY list_price ASC
LIMIT 5;
-- Expected result: 5 rows
--   product_name   | list_price
--   ---------------+-----------
--   Cotton T-Shirt | 499
--   Leather Belt   | 699
--   Sunglasses     | 999
--   Formal Shirt   | 1199
--   Hoodie         | 1299

-- T4.4. Average rating per payment mode (and see P9 for HAVING > 800).
SELECT payment_mode, ROUND(AVG(rating), 2) AS avg_rating
FROM orders
GROUP BY payment_mode
ORDER BY avg_rating DESC, payment_mode;
-- Expected result: 6 rows
--   payment_mode | avg_rating
--   -------------+-----------
--   Debit Card   | 4.0
--   Net Banking  | 3.98
--   UPI          | 3.98
--   Credit Card  | 3.94
--   Unknown      | 3.93
--   COD          | 3.9

-- T4.5 = P11, T4.6 = P12 + P13, T4.7 = P14, T4.8 = P15 (above).
