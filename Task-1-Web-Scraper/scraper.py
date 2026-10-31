
import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import webbrowser
import html
import os

base_url = "https://books.toscrape.com/catalogue/page-{}.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_books = []

def fetch_page(url):

    for attempt in range(3):

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()
            return response.text

        except requests.RequestException as error:
            print(f"Attempt {attempt + 1} failed: {error}")
            time.sleep(2)

    print("Skipping page after 3 failed attempts.")
    return None


page = 1

while True:

    url = base_url.format(page)

    print(f"\nScraping page {page}...")

    html = fetch_page(url)

    if html is None:
        break

    soup = BeautifulSoup(html, "html.parser")

    books = soup.select("article.product_pod")

    if not books:
        break

    for book in books:

        try:
            title = book.select_one("h3 a")["title"]

            price = book.select_one(".price_color").text.strip()

            availability = book.select_one(
                ".availability"
            ).text.strip()

            rating = book.select_one(
                ".star-rating"
            )["class"][1]

            product_link = book.select_one("h3 a")["href"]

            product_url = requests.compat.urljoin(
                url, product_link
            )

            all_books.append({
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "product_url": product_url
            })

        except (AttributeError, KeyError, TypeError) as error:
            print("Error extracting a book:", error)

    print(f"Extracted {len(books)} books from page {page}")

    next_button = soup.select_one("li.next a")

    if not next_button:
        break

    page += 1
    time.sleep(0.5)


# Export CSV
fieldnames = [
    "title",
    "price",
    "availability",
    "rating",
    "product_url"
]

with open("products.csv", "w", newline="", encoding="utf-8-sig") as file:

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_books)


# Export JSON
with open("products.json", "w", encoding="utf-8") as file:

    json.dump(all_books, file, indent=4, ensure_ascii=False)


print("\n========== SCRAPING SUMMARY ==========")
print("Total records extracted:", len(all_books))
print("CSV file saved successfully!")
print("JSON file saved successfully!")


# Create HTML report
html_content = """
<html>
<head>
    <title>Book Data Scraper</title>
    <style>
        body {
            font-family: Arial;
            background: #f4f6f9;
            padding: 30px;
        }

        h1 {
            text-align: center;
            color: #243b55;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }

        th {
            background: #243b55;
            color: white;
        }

        tr:nth-child(even) {
            background: #f2f2f2;
        }

        a {
            color: #2563eb;
        }
    </style>
</head>
<body>

<h1>Book Data Scraper Dashboard</h1>

<p>Total Books Extracted: """ + str(len(all_books)) + """</p>

<table>
<tr>
    <th>Title</th>
    <th>Price</th>
    <th>Availability</th>
    <th>Rating</th>
    <th>Product Link</th>
</tr>
"""

for book in all_books:
    html_content += f"""
    <tr>
        <td>{html.escape(book['title'])}</td>
        <td>{html.escape(book['price'])}</td>
        <td>{html.escape(book['availability'])}</td>
        <td>{html.escape(book['rating'])}</td>
        <td><a href="{html.escape(book['product_url'], quote=True)}" target="_blank">View Book</a></td>
    </tr>
    """

html_content += """
</table>
</body>
</html>
"""

with open("products.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML report created successfully!")

# Open report in browser
webbrowser.open(
    "file://" + os.path.abspath("products.html")
)
