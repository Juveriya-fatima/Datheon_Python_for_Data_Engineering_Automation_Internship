
from flask import Flask, jsonify, render_template_string, send_file
import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import threading
import os

app = Flask(__name__)

books_data = []
status = "Ready"
current_page = 0
total_pages = 0
is_running = False

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_page(url):
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15
            )
            response.raise_for_status()
            return response.text

        except requests.RequestException as error:
            print(f"Attempt {attempt + 1} failed: {error}")
            time.sleep(1)

    return None


def export_data():
    csv_path = os.path.join(OUTPUT_DIR, "products.csv")
    json_path = os.path.join(OUTPUT_DIR, "products.json")

    fieldnames = [
        "title",
        "price",
        "availability",
        "rating",
        "product_url"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books_data)

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(books_data, file, indent=4, ensure_ascii=False)


def scrape_books():
    global status, current_page, total_pages, is_running

    books_data.clear()
    current_page = 0
    total_pages = 0
    status = "Scraping in progress..."

    page = 1

    try:
        while True:
            current_page = page
            print(f"Scraping page {page}...")

            url = BASE_URL.format(page)
            html = fetch_page(url)

            if html is None:
                print(f"Could not scrape page {page}. Skipping.")
                page += 1
                continue

            soup = BeautifulSoup(html, "html.parser")
            books = soup.select("article.product_pod")

            if not books:
                break

            for book in books:
                try:
                    title = book.select_one("h3 a")["title"]
                    price = book.select_one(".price_color").get_text(strip=True)
                    availability = book.select_one(".availability").get_text(strip=True)
                    rating = book.select_one(".star-rating")["class"][1]

                    product_link = book.select_one("h3 a")["href"]
                    product_url = requests.compat.urljoin(url, product_link)

                    books_data.append({
                        "title": title,
                        "price": price,
                        "availability": availability,
                        "rating": rating,
                        "product_url": product_url
                    })

                except (AttributeError, KeyError, TypeError) as error:
                    print("Extraction error:", error)

            total_pages += 1
            print(f"Page {page} completed. Total books: {len(books_data)}")

            next_button = soup.select_one("li.next a")

            if not next_button:
                break

            page += 1
            time.sleep(0.1)

        export_data()
        status = "Completed"

    except Exception as error:
        status = f"Error: {error}"
        print(error)

    finally:
        is_running = False


@app.route("/")
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Web Scraper Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #263445;
        }

        header {
            background: #ffffff;
            padding: 22px 6%;
            border-bottom: 1px solid #e5eaf1;
        }

        header h1 {
            margin: 0;
            color: #183b65;
        }

        header p {
            color: #718096;
            margin-bottom: 0;
        }

        .container {
            width: 88%;
            max-width: 1200px;
            margin: 30px auto;
        }

        .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }

        button, .download {
            background: #2563eb;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 7px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
        }

        button:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin: 25px 0;
        }

        .card {
            background: white;
            padding: 22px;
            border-radius: 10px;
            box-shadow: 0 2px 10px #00000008;
        }

        .card p {
            color: #718096;
            margin: 0 0 12px;
        }

        .card h2 {
            color: #183b65;
            margin: 0;
            font-size: 27px;
        }

        .panel {
            background: white;
            padding: 22px;
            border-radius: 10px;
            margin-bottom: 22px;
            box-shadow: 0 2px 10px #00000008;
        }

        .status {
            font-weight: bold;
            color: #2563eb;
        }

        .downloads {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .table-wrapper {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 700px;
        }

        th, td {
            padding: 13px;
            border-bottom: 1px solid #edf0f5;
            text-align: left;
            font-size: 13px;
        }

        th {
            background: #f5f8fc;
            color: #42536a;
        }

        @media(max-width: 750px) {
            .cards {
                grid-template-columns: repeat(2, 1fr);
            }

            .container {
                width: 94%;
            }
        }
    </style>
</head>

<body>

<header>
    <h1>Web Scraper Dashboard</h1>
    <p>Autonomous Web Tracker and Data Extractor</p>
</header>

<div class="container">

    <div class="top">
        <div>
            <h2>Scraping Overview</h2>
            <p>Live book data extraction from Books to Scrape</p>
        </div>

        <button id="startBtn" onclick="startScraping()">
            Start Scraping
        </button>
    </div>

    <div class="cards">

        <div class="card">
            <p>Total Books Extracted</p>
            <h2 id="count">0</h2>
        </div>

        <div class="card">
            <p>Pages Scraped</p>
            <h2 id="pages">0</h2>
        </div>

        <div class="card">
            <p>Current Page</p>
            <h2 id="currentPage">0</h2>
        </div>

        <div class="card">
            <p>Scraping Status</p>
            <h2 id="status" class="status">Ready</h2>
        </div>

    </div>

    <div class="panel">
        <h3>Final Scraping Summary</h3>

        <p>Total records extracted: <b id="finalCount">0</b></p>
        <p>Total pages completed: <b id="finalPages">0</b></p>
        <p>CSV export: <b id="csvStatus">Not generated</b></p>
        <p>JSON export: <b id="jsonStatus">Not generated</b></p>

        <div class="downloads">
            <a class="download" href="/download/csv">Download CSV</a>
            <a class="download" href="/download/json">Download JSON</a>
        </div>
    </div>

    <div class="panel">
        <h3>Extracted Book Records</h3>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>S.No.</th>
                        <th>Book Title</th>
                        <th>Price</th>
                        <th>Availability</th>
                        <th>Rating</th>
                    </tr>
                </thead>

                <tbody id="bookTable"></tbody>
            </table>
        </div>
    </div>

</div>

<script>
let lastCount = 0;

async function startScraping() {
    const button = document.getElementById("startBtn");
    button.disabled = true;
    button.innerText = "Scraping...";

    document.getElementById("bookTable").innerHTML = "";
    lastCount = 0;

    await fetch("/start", { method: "POST" });
    updateData();
}

async function updateData() {
    try {
        const response = await fetch("/data");
        const data = await response.json();

        document.getElementById("count").innerText = data.count;
        document.getElementById("pages").innerText = data.pages;
        document.getElementById("currentPage").innerText = data.page;
        document.getElementById("status").innerText = data.status;

        document.getElementById("finalCount").innerText = data.count;
        document.getElementById("finalPages").innerText = data.pages;

        document.getElementById("csvStatus").innerText =
            data.status === "Completed" ? "Exported successfully" : "Pending";

        document.getElementById("jsonStatus").innerText =
            data.status === "Completed" ? "Exported successfully" : "Pending";

        if (data.count > lastCount) {
            const table = document.getElementById("bookTable");

            data.books.slice(lastCount).forEach((book, index) => {
                const row = document.createElement("tr");

                [
                    lastCount + index + 1,
                    book.title,
                    book.price,
                    book.availability,
                    book.rating
                ].forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);
                });

                table.appendChild(row);
            });

            lastCount = data.count;
        }

        if (data.status === "Completed" || data.status.startsWith("Error:")) {
            document.getElementById("startBtn").disabled = false;
            document.getElementById("startBtn").innerText = "Start Again";
        }

    } catch (error) {
        console.log("Dashboard update error:", error);
    }
}

setInterval(updateData, 1000);
</script>

</body>
</html>
""")


@app.route("/start", methods=["POST"])
def start():
    global is_running

    if not is_running:
        is_running = True
        threading.Thread(target=scrape_books, daemon=True).start()
        return jsonify({"message": "Scraping started"})

    return jsonify({"message": "Scraping is already running"})


@app.route("/data")
def data():
    return jsonify({
        "books": books_data.copy(),
        "count": len(books_data),
        "page": current_page,
        "pages": total_pages,
        "status": status
    })


@app.route("/download/csv")
def download_csv():
    return send_file(
        os.path.join(OUTPUT_DIR, "products.csv"),
        as_attachment=True
    )


@app.route("/download/json")
def download_json():
    return send_file(
        os.path.join(OUTPUT_DIR, "products.json"),
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
