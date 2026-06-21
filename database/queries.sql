-- ============================================================
-- queries.sql
-- 15 SQL queries for the Local Food Wastage Management System
-- Tables: providers, receivers, food_listings, claims
-- ============================================================

-- ---------- FOOD PROVIDERS & RECEIVERS ----------

-- Q1. How many food providers and receivers are there in each city?
SELECT City, 'Provider' AS Role, COUNT(*) AS Count
FROM providers
GROUP BY City
UNION ALL
SELECT City, 'Receiver' AS Role, COUNT(*) AS Count
FROM receivers
GROUP BY City
ORDER BY City, Role;

-- Q2. Which type of food provider contributes the most food (by quantity)?
SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
FROM food_listings
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC;

-- Q3. What is the contact information of food providers in a specific city?
-- (example city: Pune — change as needed)
SELECT Name, Type, Address, Contact
FROM providers
WHERE City = 'Pune';

-- Q4. Which receivers have claimed the most food?
SELECT r.Receiver_ID, r.Name, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Receiver_ID
ORDER BY Total_Claims DESC
LIMIT 10;


-- ---------- FOOD LISTINGS & AVAILABILITY ----------

-- Q5. What is the total quantity of food available from all providers?
SELECT SUM(Quantity) AS Total_Available_Quantity
FROM food_listings;

-- Q6. Which city has the highest number of food listings?
SELECT Location, COUNT(*) AS Listing_Count
FROM food_listings
GROUP BY Location
ORDER BY Listing_Count DESC
LIMIT 1;

-- Q7. What are the most commonly available food types?
SELECT Food_Type, COUNT(*) AS Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Count DESC;


-- ---------- CLAIMS & DISTRIBUTION ----------

-- Q8. How many food claims have been made for each food item?
SELECT fl.Food_ID, fl.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
FROM food_listings fl
LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
GROUP BY fl.Food_ID
ORDER BY Claim_Count DESC;

-- Q9. Which provider has had the highest number of successful (Completed) food claims?
SELECT p.Provider_ID, p.Name, COUNT(*) AS Completed_Claims
FROM claims c
JOIN food_listings fl ON c.Food_ID = fl.Food_ID
JOIN providers p ON fl.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID
ORDER BY Completed_Claims DESC
LIMIT 1;

-- Q10. What percentage of food claims are Completed vs Pending vs Cancelled?
SELECT Status,
       COUNT(*) AS Count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
FROM claims
GROUP BY Status;


-- ---------- ANALYSIS & INSIGHTS ----------

-- Q11. What is the average quantity of food claimed per receiver?
SELECT r.Receiver_ID, r.Name,
       ROUND(AVG(fl.Quantity), 2) AS Avg_Quantity_Claimed
FROM claims c
JOIN food_listings fl ON c.Food_ID = fl.Food_ID
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Receiver_ID
ORDER BY Avg_Quantity_Claimed DESC;

-- Q12. Which meal type is claimed the most?
SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
FROM claims c
JOIN food_listings fl ON c.Food_ID = fl.Food_ID
GROUP BY fl.Meal_Type
ORDER BY Claim_Count DESC;

-- Q13. What is the total quantity of food donated by each provider?
SELECT p.Provider_ID, p.Name, SUM(fl.Quantity) AS Total_Donated
FROM food_listings fl
JOIN providers p ON fl.Provider_ID = p.Provider_ID
GROUP BY p.Provider_ID
ORDER BY Total_Donated DESC;

-- Q14. (Bonus) Which food items are expiring within the next 3 days and still unclaimed?
SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Location
FROM food_listings fl
LEFT JOIN claims c ON fl.Food_ID = c.Food_ID AND c.Status = 'Completed'
WHERE c.Claim_ID IS NULL
  AND DATE(fl.Expiry_Date) BETWEEN DATE('now') AND DATE('now', '+3 day')
ORDER BY fl.Expiry_Date ASC;

-- Q15. (Bonus) Which provider type has the highest claim completion rate?
SELECT p.Type AS Provider_Type,
       COUNT(*) AS Total_Claims,
       SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Claims,
       ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Completion_Rate_Pct
FROM claims c
JOIN food_listings fl ON c.Food_ID = fl.Food_ID
JOIN providers p ON fl.Provider_ID = p.Provider_ID
GROUP BY p.Type
ORDER BY Completion_Rate_Pct DESC;
