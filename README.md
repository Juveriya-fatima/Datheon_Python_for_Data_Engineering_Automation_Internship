# Datheon – Python for Data Engineering & Automation Internship

## Project Overview

This repository contains the projects completed as part of the **Datheon Python for Data Engineering & Automation Internship**.

The internship focuses on developing practical skills in Python programming, web scraping, data cleaning, database management, and ETL pipeline automation.

Four tasks were implemented to demonstrate the complete data engineering workflow, from extracting raw data to storing and verifying processed data in a relational database.

## Tasks Completed

### Task 1: Autonomous Web Tracker and Data Extractor

**Objective:** Automate the extraction of book information from an online website.

- Extracted data from [Books to Scrape](https://books.toscrape.com/).
- Scraped 1,000 book records across 50 pages.
- Extracted book title, price, availability, rating, and product URL.
- Used Python Requests and BeautifulSoup.
- Exported extracted data into CSV and JSON files.

**Technologies:** Python, Requests, BeautifulSoup, CSV, JSON.

### Task 2: Automated Data Cleaning and Schema Transformation

**Objective:** Clean and transform raw extracted data into a structured dataset.

- Removed duplicate records.
- Handled missing values.
- Standardized text fields.
- Converted book prices into numeric values.
- Transformed ratings into numerical values.
- Validated the cleaned dataset.
- Generated a validation report.

**Technologies:** Python, Pandas.

### Task 3: Relational Database Auto-ingestion and Upsert Engine

**Objective:** Automatically load cleaned data into a relational database.

- Created a SQLite database.
- Designed a structured books table.
- Implemented automated data ingestion.
- Used an UPSERT operation to insert or update existing records.
- Verified database records using SQL queries.
- Analyzed prices, ratings, and duplicate records.

**Technologies:** Python, SQLite, SQL.

### Task 4: Scheduled End-to-End ETL Pipeline with Alerting

**Objective:** Integrate the previous three tasks into an automated ETL workflow.

- Automated the extraction, transformation, and loading stages.
- Integrated all three Python scripts into a single pipeline.
- Implemented scheduled execution using the Schedule library.
- Maintained execution logs for monitoring.
- Added optional Gmail email notifications for pipeline completion or failure.
- Verified database record counts after execution.

**Technologies:** Python, Schedule, Pandas, SQLite, Logging, SMTP.

## Project Folder Structure

```text
Datheon_Data_Engineering_Internship/
│
├── Task-1-Web-Scraper/
│   ├── scraper.py
│   ├── app.py
│   ├── products.csv
│   └── products.json
│
├── Task-2-Data-Cleaning/
│   ├── clean_data.py
│   ├── products.csv
│   ├── clean_products.csv
│   └── validation_report.txt
│
├── Task-3-Database-Ingestion/
│   ├── ingestion.py
│   ├── verify_database.py
│   ├── app.py
│   ├── clean_products.csv
│   └── books_database.db
│
├── Task-4-Automated-ETL-Pipeline/
│   ├── pipeline.py
│   └── pipeline.log
│
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project directory

```bash
cd Datheon_Data_Engineering_Internship
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## How to Run the Projects

Run each task from its respective folder.

**Task 1 – Web Scraping**

```bash
cd Task-1-Web-Scraper
python scraper.py
```

**Task 2 – Data Cleaning**

```bash
cd Task-2-Data-Cleaning
python clean_data.py
```

Ensure that `products.csv` is available in the folder.

**Task 3 – Database Ingestion**

```bash
cd Task-3-Database-Ingestion
python ingestion.py
python verify_database.py
```

Ensure that `clean_products.csv` is available in the folder.

**Task 4 – Automated ETL Pipeline**

```bash
cd Task-4-Automated-ETL-Pipeline
python pipeline.py
```

The pipeline runs once immediately and then schedules daily execution at 09:00. Keep the program running and the computer awake for scheduled execution.

## Email Alert Configuration

Email notifications are optional.

To enable Gmail notifications, configure the following environment variables in PowerShell:

```powershell
$env:ETL_EMAIL_SENDER="your_email@gmail.com"
$env:ETL_EMAIL_PASSWORD="your_gmail_app_password"
$env:ETL_EMAIL_RECEIVER="receiver_email@gmail.com"
```


## Key Learning Outcomes

- Practical experience with Python automation.
- Web scraping and data extraction.
- Data preprocessing and validation.
- Relational database management using SQLite.
- SQL queries and UPSERT operations.
- End-to-end ETL pipeline development.
- Task scheduling, logging, and email notifications.

## Acknowledgement

I would like to thank **Datheon** for providing this internship opportunity and helping me gain practical exposure to Python-based Data Engineering and Automation.

---

**Internship:** Python for Data Engineering & Automation  
**Organization:** Datheon  
**Repository:** Datheon_Python_for_Data_Engineering_&_Automation_Internship
