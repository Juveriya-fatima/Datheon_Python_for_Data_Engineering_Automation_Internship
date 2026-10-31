
import sqlite3
import csv
import os

# --------------------------------
# 1. DATABASE CONFIGURATION
# --------------------------------

DATABASE = "books_database.db"
CSV_FILE = "clean_products.csv"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

print("Connected to SQLite database!")


try:
    # --------------------------------
    # 2. CREATE DATABASE TABLE
    # --------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            product_url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            availability TEXT,
            rating INTEGER,
            currency TEXT
        )
    """)

    print("Books table created successfully!")

    # --------------------------------
    # 3. READ CSV DATA
    # --------------------------------

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        records = []

        for row in reader:
            records.append((
                row["product_url"],
                row["title"],
                float(row["price"]),
                row["availability"],
                int(row["rating"]),
                row["currency"]
            ))

    print("CSV file loaded successfully!")
    print("Total records found:", len(records))

    # --------------------------------
    # 4. INSERT OR UPDATE (UPSERT)
    # --------------------------------

    query = """
        INSERT INTO books (
            product_url,
            title,
            price,
            availability,
            rating,
            currency
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(product_url)
        DO UPDATE SET
            title = excluded.title,
            price = excluded.price,
            availability = excluded.availability,
            rating = excluded.rating,
            currency = excluded.currency
    """

    # Transaction-safe batch insertion
    with connection:
        cursor.executemany(query, records)

    print("Database ingestion completed successfully!")
    print("Records inserted or updated:", len(records))

    # --------------------------------
    # 5. VERIFY DATABASE COUNT
    # --------------------------------

    cursor.execute("SELECT COUNT(*) FROM books")
    total_records = cursor.fetchone()[0]

    print("\n========== DATABASE SUMMARY ==========")
    print("Database:", DATABASE)
    print("Table: books")
    print("Total records in database:", total_records)
    print("Primary key: product_url")
    print("Transaction: Successful")

except Exception as error:
    print("Database ingestion failed:", error)
    raise

finally:
    connection.close()
    print("\nDatabase connection closed.")
