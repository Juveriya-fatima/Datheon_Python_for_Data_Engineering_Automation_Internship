
import pandas as pd
import re
import os

# --------------------------------
# 1. LOAD DATA
# --------------------------------

print("Starting automated data cleaning...")

input_file = "products.csv"

df = pd.read_csv(input_file)

original_count = len(df)

print("Dataset loaded successfully!")
print("Original records:", original_count)


# --------------------------------
# 2. INITIAL DATA QUALITY CHECK
# --------------------------------

missing_before = df.isnull().sum().sum()
duplicates_before = df.duplicated().sum()

report = []

report.append("AUTOMATED DATA CLEANING AND VALIDATION REPORT")
report.append("=" * 50)
report.append(f"Original records: {original_count}")
report.append(f"Missing values before cleaning: {missing_before}")
report.append(f"Duplicate records before cleaning: {duplicates_before}")


# --------------------------------
# 3. REMOVE DUPLICATE RECORDS
# --------------------------------

df = df.drop_duplicates()

duplicates_removed = original_count - len(df)

report.append(f"Duplicate records removed: {duplicates_removed}")


# --------------------------------
# 4. HANDLE NULL VALUES
# --------------------------------

missing_title_before = df["title"].isnull().sum()

# Remove records without essential fields
df = df.dropna(subset=["title", "product_url"])

# Fill missing optional values
df["availability"] = df["availability"].fillna("Unknown")
df["rating"] = df["rating"].fillna("Unknown")
df["price"] = df["price"].fillna("0")

report.append(f"Records removed due to missing title or URL: {missing_title_before}")


# --------------------------------
# 5. CLEAN TEXT DATA
# --------------------------------

df["title"] = df["title"].astype(str).str.strip()
df["availability"] = df["availability"].astype(str).str.strip()
df["rating"] = df["rating"].astype(str).str.strip()
df["product_url"] = df["product_url"].astype(str).str.strip()


# --------------------------------
# 6. NORMALIZE CURRENCY
# --------------------------------

def clean_price(value):
    value = str(value)

    # Remove currency symbols and other characters
    value = re.sub(r"[^\d.]", "", value)

    try:
        return float(value)
    except ValueError:
        return None


df["price"] = df["price"].apply(clean_price)

df["currency"] = "GBP"

report.append("Currency values normalized to numeric GBP prices.")


# --------------------------------
# 7. NORMALIZE RATING
# --------------------------------

rating_mapping = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["rating"] = (
    df["rating"].astype(str).str.title().map(rating_mapping)
)

df["rating"] = df["rating"].fillna(0).astype(int)

report.append("Ratings converted into numeric values from 1 to 5.")
report.append("Unknown ratings represented as 0.")


# --------------------------------
# 8. NORMALIZE DATE COLUMNS
# --------------------------------

date_columns = [
    column for column in df.columns
    if "date" in column.lower() or "datetime" in column.lower()
]

if date_columns:
    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
            dayfirst=True
        )
        df[column] = df[column].dt.strftime("%Y-%m-%d")

    report.append("Date columns normalized to YYYY-MM-DD format.")
else:
    report.append(
        "Date normalization skipped: no date column exists in the source dataset."
    )


# --------------------------------
# 9. SCHEMA VALIDATION
# --------------------------------

required_columns = [
    "title",
    "price",
    "availability",
    "rating",
    "product_url",
    "currency"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    report.append(f"Schema validation FAILED. Missing columns: {missing_columns}")
    raise ValueError(f"Missing required columns: {missing_columns}")

# Validate data types
df["price"] = pd.to_numeric(df["price"], errors="coerce")

invalid_prices = df["price"].isnull().sum()
invalid_titles = (df["title"].str.len() == 0).sum()

# Validate URLs
invalid_urls = ~df["product_url"].str.startswith(
    ("http://", "https://"), na=False
)

invalid_url_count = invalid_urls.sum()

# Remove records that fail essential validation
df = df[
    df["price"].notna()
    & (df["title"].str.len() > 0)
    & ~invalid_urls
].copy()

# Enforce final data types
df["price"] = df["price"].astype(float)
df["rating"] = df["rating"].astype(int)

report.append("Required columns checked successfully.")
report.append(f"Invalid prices detected: {invalid_prices}")
report.append(f"Empty titles detected: {invalid_titles}")
report.append(f"Invalid URLs detected: {invalid_url_count}")


# --------------------------------
# 10. SAVE CLEAN DATASET
# --------------------------------

output_file = "clean_products.csv"

df.to_csv(output_file, index=False, encoding="utf-8-sig")

final_count = len(df)
missing_after = df.isnull().sum().sum()
duplicates_after = df.duplicated().sum()


# --------------------------------
# 11. GENERATE VALIDATION REPORT
# --------------------------------

report.append("")
report.append("=" * 50)
report.append("FINAL DATA QUALITY SUMMARY")
report.append("=" * 50)

report.append(f"Original records: {original_count}")
report.append(f"Final clean records: {final_count}")
report.append(f"Records removed: {original_count - final_count}")
report.append(f"Missing values after cleaning: {missing_after}")
report.append(f"Duplicate records after cleaning: {duplicates_after}")

report.append("")
report.append("FINAL SCHEMA:")
report.append(str(df.dtypes))

report.append("")
report.append("FINAL VALIDATION STATUS:")

if missing_after == 0 and duplicates_after == 0:
    report.append("PASSED - No missing values or duplicate records.")
else:
    report.append("WARNING - Some data quality issues remain.")

report.append("")
report.append("Clean dataset saved as: clean_products.csv")

with open("validation_report.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(report))


# --------------------------------
# 12. DISPLAY FINAL SUMMARY
# --------------------------------

print("\n========== CLEANING COMPLETED ==========")
print("Original records:", original_count)
print("Final clean records:", final_count)
print("Records removed:", original_count - final_count)
print("Missing values remaining:", missing_after)
print("Duplicate records remaining:", duplicates_after)

print("\nClean dataset saved:", output_file)
print("Validation report saved: validation_report.txt")

print("\nFinal dataset preview:")
print(df.head())

print("\nTask 2 completed successfully!")
