"""
queries.py
Runs all 15 analysis queries against database/food_wastage.db and prints
the results. These same query strings are reused later inside the
Streamlit app's "SQL Insights" tab.

Run from project root:
    python queries.py
"""

import sqlite3
import pandas as pd

DB_PATH = "database/food_wastage.db"

# A dict of {description: SQL query} — order matches the project brief.
QUERIES = {
    "Q1. Providers & receivers per city": """
        SELECT City, 'Provider' AS Role, COUNT(*) AS Count
        FROM providers GROUP BY City
        UNION ALL
        SELECT City, 'Receiver' AS Role, COUNT(*) AS Count
        FROM receivers GROUP BY City
        ORDER BY City, Role;
    """,

    "Q2. Provider type contributing most food (by quantity)": """
        SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
        FROM food_listings
        GROUP BY Provider_Type
        ORDER BY Total_Quantity DESC;
    """,

    "Q3. Contact info of providers in Pune": """
        SELECT Name, Type, Address, Contact
        FROM providers
        WHERE City = 'Pune';
    """,

    "Q4. Receivers who claimed the most food (top 10)": """
        SELECT r.Receiver_ID, r.Name, COUNT(c.Claim_ID) AS Total_Claims
        FROM claims c
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.Receiver_ID
        ORDER BY Total_Claims DESC
        LIMIT 10;
    """,

    "Q5. Total quantity of food available from all providers": """
        SELECT SUM(Quantity) AS Total_Available_Quantity
        FROM food_listings;
    """,

    "Q6. City with the highest number of food listings": """
        SELECT Location, COUNT(*) AS Listing_Count
        FROM food_listings
        GROUP BY Location
        ORDER BY Listing_Count DESC
        LIMIT 1;
    """,

    "Q7. Most commonly available food types": """
        SELECT Food_Type, COUNT(*) AS Count
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY Count DESC;
    """,

    "Q8. Number of claims made for each food item (top 10)": """
        SELECT fl.Food_ID, fl.Food_Name, COUNT(c.Claim_ID) AS Claim_Count
        FROM food_listings fl
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
        GROUP BY fl.Food_ID
        ORDER BY Claim_Count DESC
        LIMIT 10;
    """,

    "Q9. Provider with highest number of Completed claims": """
        SELECT p.Provider_ID, p.Name, COUNT(*) AS Completed_Claims
        FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Provider_ID
        ORDER BY Completed_Claims DESC
        LIMIT 1;
    """,

    "Q10. Percentage of claims by status": """
        SELECT Status,
               COUNT(*) AS Count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
        FROM claims
        GROUP BY Status;
    """,

    "Q11. Average quantity of food claimed per receiver (top 10)": """
        SELECT r.Receiver_ID, r.Name,
               ROUND(AVG(fl.Quantity), 2) AS Avg_Quantity_Claimed
        FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.Receiver_ID
        ORDER BY Avg_Quantity_Claimed DESC
        LIMIT 10;
    """,

    "Q12. Meal type claimed the most": """
        SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS Claim_Count
        FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        GROUP BY fl.Meal_Type
        ORDER BY Claim_Count DESC;
    """,

    "Q13. Total quantity of food donated by each provider (top 10)": """
        SELECT p.Provider_ID, p.Name, SUM(fl.Quantity) AS Total_Donated
        FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        GROUP BY p.Provider_ID
        ORDER BY Total_Donated DESC
        LIMIT 10;
    """,

    "Q14. Food expiring in next 3 days, still unclaimed": """
        SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Location
        FROM food_listings fl
        LEFT JOIN claims c ON fl.Food_ID = c.Food_ID AND c.Status = 'Completed'
        WHERE c.Claim_ID IS NULL
          AND DATE(fl.Expiry_Date) BETWEEN DATE('now') AND DATE('now', '+3 day')
        ORDER BY fl.Expiry_Date ASC;
    """,

    "Q15. Provider type with highest claim completion rate": """
        SELECT p.Type AS Provider_Type,
               COUNT(*) AS Total_Claims,
               SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS Completed_Claims,
               ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Completion_Rate_Pct
        FROM claims c
        JOIN food_listings fl ON c.Food_ID = fl.Food_ID
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        GROUP BY p.Type
        ORDER BY Completion_Rate_Pct DESC;
    """,
}


def run_all_queries():
    conn = sqlite3.connect(DB_PATH)
    for title, sql in QUERIES.items():
        print("=" * 70)
        print(title)
        print("=" * 70)
        try:
            df = pd.read_sql_query(sql, conn)
            print(df.to_string(index=False) if not df.empty else "(no rows returned)")
        except Exception as e:
            print(f"ERROR running query: {e}")
        print()
    conn.close()


if __name__ == "__main__":
    run_all_queries()
