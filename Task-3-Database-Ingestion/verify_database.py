
import sqlite3

DATABASE = "books_database.db"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

print("========== DATABASE VERIFICATION ==========")

# 1. Total records
cursor.execute("SELECT COUNT(*) FROM books")
print("\nTotal books:", cursor.fetchone()[0])


# 2. Display first five records
print("\nFirst 5 books:")

cursor.execute("""
    SELECT title, price, rating
    FROM books
    LIMIT 5
""")

for row in cursor.fetchall():
    print(row)


# 3. Find the most expensive books
print("\nTop 5 expensive books:")

cursor.execute("""
    SELECT title, price
    FROM books
    ORDER BY price DESC
    LIMIT 5
""")

for row in cursor.fetchall():
    print(row)


# 4. Average book price
cursor.execute("SELECT AVG(price) FROM books")
average_price = cursor.fetchone()[0]

print("\nAverage book price:", round(average_price, 2))


# 5. Rating distribution
print("\nRating distribution:")

cursor.execute("""
    SELECT rating, COUNT(*)
    FROM books
    GROUP BY rating
    ORDER BY rating
""")

for row in cursor.fetchall():
    print("Rating:", row[0], "| Books:", row[1])


# 6. Check duplicate primary keys
cursor.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT product_url)
    FROM books
""")

print("\nDuplicate product URLs:", cursor.fetchone()[0])


# 7. Check database schema
print("\nDatabase table structure:")

cursor.execute("PRAGMA table_info(books)")

for column in cursor.fetchall():
    print(column)


connection.close()

print("\nDatabase verification completed successfully!")
