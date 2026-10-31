
from flask import Flask, render_template_string, jsonify, request
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "books_database.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Database Ingestion Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #263445;
        }

        header {
            background: white;
            padding: 24px 6%;
            border-bottom: 1px solid #e5eaf1;
        }

        header h1 {
            margin: 0;
            color: #183b65;
        }

        header p { color: #718096; }

        .container {
            width: 90%;
            max-width: 1250px;
            margin: 30px auto;
        }

        .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin: 25px 0;
        }

        .card, .panel {
            background: white;
            padding: 22px;
            border-radius: 10px;
            box-shadow: 0 2px 10px #00000008;
        }

        .card p {
            color: #718096;
            margin-top: 0;
        }

        .card h2 {
            margin-bottom: 0;
            font-size: 27px;
            color: #183b65;
        }

        .panel { margin-bottom: 22px; }

        button {
            background: #2563eb;
            color: white;
            border: none;
            padding: 12px 18px;
            border-radius: 7px;
            cursor: pointer;
        }

        button:hover { background: #1d4ed8; }

        input {
            padding: 11px;
            border: 1px solid #dce3ed;
            border-radius: 7px;
            width: 260px;
            max-width: 100%;
        }

        .table-wrapper { overflow-x: auto; }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 650px;
        }

        th, td {
            text-align: left;
            padding: 13px;
            border-bottom: 1px solid #edf0f5;
            font-size: 13px;
        }

        th {
            background: #f5f8fc;
            color: #42536a;
        }

        .status {
            color: #15803d;
            font-weight: bold;
        }

        .columns {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        .muted { color: #718096; }

        .query-result {
            margin-top: 12px;
            line-height: 1.8;
        }

        @media(max-width: 800px) {
            .cards { grid-template-columns: repeat(2, 1fr); }
            .columns { grid-template-columns: 1fr; }
        }

        @media(max-width: 480px) {
            .cards { grid-template-columns: 1fr; }
            .container { width: 94%; }
        }
    </style>
</head>

<body>

<header>
    <h1>Database Ingestion Dashboard</h1>
    <p>Relational Database Auto-Ingestion and Upsert Engine</p>
</header>

<div class="container">

    <div class="top">
        <div>
            <h2>Database Overview</h2>
            <p class="muted">Live information from your SQLite database</p>
        </div>

        <button onclick="loadDashboard()">Refresh Dashboard</button>
    </div>

    <div class="cards">
        <div class="card">
            <p>Total Records</p>
            <h2 id="total">-</h2>
        </div>

        <div class="card">
            <p>Average Price</p>
            <h2 id="average">-</h2>
        </div>

        <div class="card">
            <p>Unique URLs</p>
            <h2 id="unique">-</h2>
        </div>

        <div class="card">
            <p>Database Status</p>
            <h2 class="status" id="status">Checking...</h2>
        </div>
    </div>

    <div class="columns">

        <div class="panel">
            <h3>Database Information</h3>
            <p>Database: <b>books_database.db</b></p>
            <p>Table: <b>books</b></p>
            <p>Primary Key: <b>product_url</b></p>
            <p>Database Engine: <b>SQLite</b></p>
            <p>Transaction Support: <b>Enabled in ingestion script</b></p>
        </div>

        <div class="panel">
            <h3>SQL Verification Results</h3>
            <div class="query-result">
                <p>Duplicate URLs: <b id="duplicates">-</b></p>
                <p>Missing Titles: <b id="missing">-</b></p>
                <p>Highest Price: <b id="highest">-</b></p>
                <p>Lowest Price: <b id="lowest">-</b></p>
            </div>
        </div>

    </div>

    <div class="panel">
        <h3>Rating Distribution</h3>
        <div id="ratings" class="query-result"></div>
    </div>

    <div class="panel">
        <h3>Top 5 Expensive Books</h3>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Book Title</th>
                        <th>Price</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody id="topBooks"></tbody>
            </table>
        </div>
    </div>

    <div class="panel">
        <h3>All Database Records</h3>

        <input
            type="text"
            id="search"
            placeholder="Search book title..."
            oninput="loadBooks()"
        >

        <p class="muted" id="recordInfo"></p>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Product URL</th>
                        <th>Book Title</th>
                        <th>Price</th>
                        <th>Availability</th>
                        <th>Rating</th>
                        <th>Currency</th>
                    </tr>
                </thead>
                <tbody id="bookTable"></tbody>
            </table>
        </div>

    </div>

</div>

<script>

async function loadDashboard() {
    try {
        const response = await fetch("/stats");
        const data = await response.json();

        if (data.error) {
            document.getElementById("status").innerText = "Error";
            return;
        }

        document.getElementById("total").innerText = data.total;
        document.getElementById("average").innerText =
            "£" + Number(data.average).toFixed(2);

        document.getElementById("unique").innerText = data.unique;
        document.getElementById("status").innerText = "Connected";

        document.getElementById("duplicates").innerText = data.duplicates;
        document.getElementById("missing").innerText = data.missing;
        document.getElementById("highest").innerText =
            "£" + Number(data.highest).toFixed(2);
        document.getElementById("lowest").innerText =
            "£" + Number(data.lowest).toFixed(2);

        const ratings = document.getElementById("ratings");
        ratings.innerHTML = "";

        data.ratings.forEach(item => {
            const p = document.createElement("p");
            p.textContent = "Rating " + item.rating + ": " + item.count + " books";
            ratings.appendChild(p);
        });

        const top = document.getElementById("topBooks");
        top.innerHTML = "";

        data.top_books.forEach(book => {
            const tr = document.createElement("tr");

            [book.title, "£" + Number(book.price).toFixed(2), book.rating]
                .forEach(value => {
                    const td = document.createElement("td");
                    td.textContent = value;
                    tr.appendChild(td);
                });

            top.appendChild(tr);
        });

        loadBooks();

    } catch (error) {
        document.getElementById("status").innerText = "Unavailable";
        console.log(error);
    }
}


async function loadBooks() {
    const search = document.getElementById("search").value;

    const response = await fetch(
        "/books?search=" + encodeURIComponent(search)
    );

    const data = await response.json();

    const table = document.getElementById("bookTable");
    table.innerHTML = "";

    data.books.forEach(book => {
        const tr = document.createElement("tr");

        [
            book.product_url,
            book.title,
            "£" + Number(book.price).toFixed(2),
            book.availability,
            book.rating,
            book.currency
        ].forEach(value => {
            const td = document.createElement("td");
            td.textContent = value;
            tr.appendChild(td);
        });

        table.appendChild(tr);
    });

    document.getElementById("recordInfo").innerText =
        "Showing " + data.books.length + " records";
}

loadDashboard();

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/stats")
def stats():
    if not os.path.exists(DATABASE):
        return jsonify({"error": "Database not found. Run ingestion.py first."}), 404

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM books")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT product_url) FROM books")
        unique = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(price), MAX(price), MIN(price) FROM books")
        average, highest, lowest = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*)
            FROM books
            WHERE title IS NULL OR TRIM(title) = ''
        """)
        missing = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) - COUNT(DISTINCT product_url)
            FROM books
        """)
        duplicates = cursor.fetchone()[0]

        cursor.execute("""
            SELECT rating, COUNT(*) AS count
            FROM books
            GROUP BY rating
            ORDER BY rating
        """)
        ratings = [
            dict(row) for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT title, price, rating
            FROM books
            ORDER BY price DESC
            LIMIT 5
        """)
        top_books = [
            dict(row) for row in cursor.fetchall()
        ]

        return jsonify({
            "total": total,
            "unique": unique,
            "average": average or 0,
            "highest": highest or 0,
            "lowest": lowest or 0,
            "missing": missing,
            "duplicates": duplicates,
            "ratings": ratings,
            "top_books": top_books
        })

    finally:
        connection.close()


@app.route("/books")
def books():
    if not os.path.exists(DATABASE):
        return jsonify({"books": [], "error": "Database not found"}), 404

    search = request.args.get("search", "").strip()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT product_url, title, price, availability, rating, currency
            FROM books
            WHERE title LIKE ?
            ORDER BY title
            LIMIT 1000
        """, ("%" + search + "%",))

        records = [dict(row) for row in cursor.fetchall()]

        return jsonify({"books": records})

    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
