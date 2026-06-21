import pandas as pd
import sqlite3
import os

DATA_DIR = "data"
DB_PATH = os.path.join("database", "food_wastage.db")

os.makedirs("database", exist_ok=True)

providers = pd.read_csv(os.path.join(DATA_DIR, "providers_data.csv"))
receivers = pd.read_csv(os.path.join(DATA_DIR, "receivers_data.csv"))
food_listings = pd.read_csv(os.path.join(DATA_DIR, "food_listings_data.csv"))
claims = pd.read_csv(os.path.join(DATA_DIR, "claims_data.csv"))

for df in [providers, receivers, food_listings, claims]:
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

food_listings["Expiry_Date"] = pd.to_datetime(food_listings["Expiry_Date"]).dt.strftime("%Y-%m-%d")
claims["Timestamp"] = pd.to_datetime(claims["Timestamp"])

providers = providers.drop_duplicates()
receivers = receivers.drop_duplicates()
food_listings = food_listings.drop_duplicates()
claims = claims.drop_duplicates()

for name, df in [("providers", providers), ("receivers", receivers),
                  ("food_listings", food_listings), ("claims", claims)]:
    nulls = df.isnull().sum().sum()
    if nulls:
        print(f"Warning: {name} has {nulls} null values")

conn = sqlite3.connect(DB_PATH)

providers.to_sql("providers", conn, if_exists="replace", index=False)
receivers.to_sql("receivers", conn, if_exists="replace", index=False)
food_listings.to_sql("food_listings", conn, if_exists="replace", index=False)
claims.to_sql("claims", conn, if_exists="replace", index=False)

print("\nDatabase created at:", DB_PATH)
for table in ["providers", "receivers", "food_listings", "claims"]:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<15} -> {count} rows")

conn.close()