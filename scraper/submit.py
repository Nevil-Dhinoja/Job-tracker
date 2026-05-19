from requests.api import options
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from google.oauth2.service_account import Credentials

# ── Config ────────────────────────────────────────────────────────────────────
FORM_URL       = "http://localhost:5002/form"
CREDS_PATH     = os.path.join(os.path.dirname(__file__), "..", "credentials", "credentials.json")
SHEET_NAME     = "Job Tracker"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
SCOPES         = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# ── Google Sheets helpers ─────────────────────────────────────────────────────
def get_sheet():
    creds  = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def find_row_by_url(sheet, url: str):
    """Return 1-based row index of the first row matching the URL."""
    records = sheet.get_all_values()
    for i, row in enumerate(records[1:], start=2):   # skip header
        if len(row) >= 5 and row[4] == url:
            return i
    return None


def update_status(sheet, row_index: int, status: str, log: str = ""):
    sheet.update_cell(row_index, 6, status)           # col F = Status
    if log:
        # Append log to col H (create if needed)
        sheet.update_cell(row_index, 8, log)


# ── Selenium logic ────────────────────────────────────────────────────────────
def fill_and_submit(data: dict) -> dict:
    """
    Opens the demo form, fills it, submits, saves screenshot.
    Returns {"success": bool, "screenshot": path, "error": str}
    """
    options = Options()
    options.add_argument("--start-maximized")
    # Remove headless so you can watch it run
    # options.add_argument("--headless=new")

    # driver = webdriver.Chrome(
    #     service=Service(ChromeDriverManager().install()),
    #     options=options
    # )
    from selenium.webdriver.chrome.service import Service as ChromeService

# Let Selenium 4.6+ auto-manage ChromeDriver (no webdriver-manager needed)
    driver = webdriver.Chrome(options=options)

    result = {"success": False, "screenshot": None, "error": None}

    try:
        driver.get(FORM_URL)

        wait = WebDriverWait(driver, 10)

        # Fill fields
        wait.until(EC.presence_of_element_located((By.ID, "company")))

        driver.find_element(By.ID, "company").clear()
        driver.find_element(By.ID, "company").send_keys(data.get("company", ""))

        driver.find_element(By.ID, "role").clear()
        driver.find_element(By.ID, "role").send_keys(data.get("role", ""))

        driver.find_element(By.ID, "salary").clear()
        driver.find_element(By.ID, "salary").send_keys(data.get("salary", ""))

        driver.find_element(By.ID, "deadline").clear()
        driver.find_element(By.ID, "deadline").send_keys(data.get("deadline", ""))

        # Click submit
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(1)

        # Verify submission — page title changes to SUBMITTED
        assert "SUBMITTED" in driver.title or \
               "submitted" in driver.find_element(By.ID, "result").text.lower(), \
               "Submission confirmation not found"

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)

    finally:
        # Save screenshot regardless of success/fail
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_slug = data.get("company", "unknown").replace(" ", "_")
        filename = f"{company_slug}_{ts}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(filepath)
        result["screenshot"] = filepath
        driver.quit()

    return result


# ── Main entry point ──────────────────────────────────────────────────────────
def process_job(data: dict):
    """
    Full pipeline: find sheet row → mark processing →
    run Selenium → update status to done/failed.
    """
    sheet = get_sheet()
    url   = data.get("url", "")

    row_index = find_row_by_url(sheet, url)
    if not row_index:
        return {"error": f"Row not found for URL: {url}"}

    # Mark as processing
    update_status(sheet, row_index, "processing")

    # Run Selenium
    selenium_result = fill_and_submit(data)

    # Update final status
    if selenium_result["success"]:
        update_status(sheet, row_index, "done",
                      f"Screenshot: {selenium_result['screenshot']}")
    else:
        update_status(sheet, row_index, "failed",
                      selenium_result.get("error", "Unknown error"))

    return selenium_result