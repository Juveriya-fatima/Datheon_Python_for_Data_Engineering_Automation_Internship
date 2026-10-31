
import os
import sys
import time
import shutil
import logging
import subprocess
import smtplib
import schedule

from pathlib import Path
from datetime import datetime
from email.message import EmailMessage


# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

TASK1 = BASE_DIR / "Task-1-Web-Scraper"
TASK2 = BASE_DIR / "Task-2-Data-Cleaning"
TASK3 = BASE_DIR / "Task-3-Database-Ingestion"

LOG_FILE = Path(__file__).resolve().parent / "pipeline.log"

SCHEDULE_TIME = "09:00"


# ==========================================
# 2. LOGGING CONFIGURATION
# ==========================================

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)


# ==========================================
# 3. EMAIL ALERT CONFIGURATION
# ==========================================

EMAIL_SENDER = os.getenv("ETL_EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("ETL_EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("ETL_EMAIL_RECEIVER")


def send_email(subject, body):

    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        logger.warning(
            "Email not configured. Skipping email notification."
        )
        print("Email alert skipped: Email settings are not configured.")
        return False

    try:
        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = EMAIL_SENDER
        message["To"] = EMAIL_RECEIVER

        message.set_content(body)

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, timeout=20
        ) as server:

            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(message)

        logger.info("Email notification sent successfully.")
        print("Email notification sent successfully!")

        return True

    except Exception as error:
        logger.exception("Email notification failed: %s", error)
        print("Email notification failed:", error)
        return False


# ==========================================
# 4. RUN PYTHON SCRIPTS
# ==========================================

def run_script(script_path, working_directory):

    logger.info("Starting script: %s", script_path.name)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(working_directory),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=3600
    )

    if result.stdout:
        logger.info("Output from %s:\n%s", script_path.name, result.stdout)

    if result.stderr:
        logger.warning("Errors/output from %s:\n%s", script_path.name, result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"{script_path.name} failed. Check pipeline.log for details."
        )

    logger.info("Completed successfully: %s", script_path.name)


# ==========================================
# 5. COMPLETE ETL PIPELINE
# ==========================================

def run_pipeline():

    start_time = datetime.now()

    logger.info("=" * 55)
    logger.info("ETL PIPELINE STARTED")
    logger.info("=" * 55)

    print("\n======================================")
    print("      AUTOMATED ETL PIPELINE")
    print("======================================")

    status = "FAILED"
    total_records = 0
    email_body = ""

    try:

        # STEP 1: EXTRACTION

        print("\nSTEP 1: Extracting data...")

        run_script(
            TASK1 / "scraper.py",
            TASK1
        )

        source_csv = TASK1 / "products.csv"

        if not source_csv.exists():
            raise FileNotFoundError("Task 1 products.csv was not generated.")

        import pandas as pd

        extracted_df = pd.read_csv(source_csv)
        total_records = len(extracted_df)

        logger.info("Extraction completed. Records: %s", total_records)

        print("Extraction completed!")
        print("Records extracted:", total_records)


        # STEP 2: TRANSFORMATION

        print("\nSTEP 2: Cleaning and transforming data...")

        shutil.copy2(
            source_csv,
            TASK2 / "products.csv"
        )

        run_script(
            TASK2 / "clean_data.py",
            TASK2
        )

        clean_csv = TASK2 / "clean_products.csv"

        if not clean_csv.exists():
            raise FileNotFoundError("Clean dataset was not generated.")

        clean_df = pd.read_csv(clean_csv)

        clean_count = len(clean_df)

        logger.info("Transformation completed. Clean records: %s", clean_count)

        print("Data cleaning completed!")
        print("Clean records:", clean_count)


        # STEP 3: LOADING

        print("\nSTEP 3: Loading data into SQLite...")

        shutil.copy2(
            clean_csv,
            TASK3 / "clean_products.csv"
        )

        run_script(
            TASK3 / "ingestion.py",
            TASK3
        )

        logger.info("Database loading completed.")

        print("Database loading completed!")


        # STEP 4: DATABASE VERIFICATION

        print("\nSTEP 4: Verifying database...")

        run_script(
            TASK3 / "verify_database.py",
            TASK3
        )

        import sqlite3

        database_path = TASK3 / "books_database.db"

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM books")

        database_count = cursor.fetchone()[0]

        connection.close()

        logger.info("Database records verified: %s", database_count)

        if database_count != clean_count:
            raise RuntimeError(
                "Database record count does not match cleaned dataset."
            )

        status = "SUCCESS"

        print("\nALL ETL STAGES COMPLETED SUCCESSFULLY!")


    except Exception as error:

        logger.exception("ETL PIPELINE FAILED: %s", error)

        print("\nETL PIPELINE FAILED!")
        print("Error:", error)


    # ======================================
    # 6. FINAL SUMMARY
    # ======================================

    end_time = datetime.now()

    duration = (end_time - start_time).total_seconds()

    summary = f"""
AUTOMATED ETL PIPELINE SUMMARY
================================

Execution Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}

Pipeline Status: {status}

Records Extracted: {total_records}

Execution Duration: {duration:.2f} seconds

Database: books_database.db

Log File: pipeline.log

Completed At: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
"""

    print(summary)

    logger.info("Pipeline status: %s", status)
    logger.info("Execution duration: %.2f seconds", duration)
    logger.info("ETL PIPELINE FINISHED")

    email_body = summary

    subject = f"ETL Pipeline {status} - {start_time.strftime('%Y-%m-%d')}"

    send_email(subject, email_body)

    print("Pipeline execution finished.")
    print("Check pipeline.log for detailed execution history.")


# ==========================================
# 7. AUTOMATIC SCHEDULER
# ==========================================

if __name__ == "__main__":

    print("ETL Scheduler Started")
    print("Scheduled execution time:", SCHEDULE_TIME)

    logger.info("ETL Scheduler started.")

    # Run once immediately for testing
    run_pipeline()

    # Schedule automatic daily execution
    schedule.every().day.at(SCHEDULE_TIME).do(run_pipeline)

    print("\nNext executions will happen daily at", SCHEDULE_TIME)
    print("Keep this program running for automatic scheduling.")
    print("Press CTRL+C to stop the scheduler.")

    try:

        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:

        print("\nETL Scheduler stopped.")

        logger.info("ETL Scheduler stopped by user.")
