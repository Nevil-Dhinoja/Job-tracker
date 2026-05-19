import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def scrape_job(url: str) -> dict:
    """
    Scrape a job page and extract: company, role, salary, deadline.
    Falls back to empty strings if extraction fails.
    """
    result = {
        "company": "",
        "role": "",
        "salary": "",
        "deadline": "",
        "error": None
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # --- Extract Role (job title) ---
        # Try common patterns used by job sites
        role_candidates = [
            soup.find("h1"),
            soup.find(attrs={"class": re.compile(r"job.?title|position|role", re.I)}),
            soup.find("title"),
        ]
        for candidate in role_candidates:
            if candidate and candidate.get_text(strip=True):
                result["role"] = candidate.get_text(strip=True)[:100]
                break

        # --- Extract Company ---
        company_candidates = [
            soup.find(attrs={"class": re.compile(r"company|employer|org", re.I)}),
            soup.find(attrs={"itemprop": "hiringOrganization"}),
            soup.find("meta", attrs={"property": "og:site_name"}),
        ]
        for candidate in company_candidates:
            if candidate:
                text = candidate.get("content") or candidate.get_text(strip=True)
                if text:
                    result["company"] = text[:100]
                    break

        # --- Extract Salary ---
        full_text = soup.get_text()
        salary_match = re.search(
            r"(\₹|INR|USD|\$|LPA|lpa)[\s]?[\d,]+[\s]?([-–][\s]?[\d,]+)?[\s]?(LPA|lpa|per year|/yr|k)?",
            full_text
        )
        if salary_match:
            result["salary"] = salary_match.group(0).strip()[:50]

        # --- Extract Deadline ---
        deadline_match = re.search(
            r"(apply by|deadline|last date|closes?)[:\s]+([A-Za-z0-9\s,/-]+\d{4})",
            full_text, re.I
        )
        if deadline_match:
            result["deadline"] = deadline_match.group(2).strip()[:50]

        # Fallback: OG tags for company/role
        if not result["company"]:
            og_site = soup.find("meta", attrs={"property": "og:site_name"})
            if og_site:
                result["company"] = og_site.get("content", "")[:100]

        if not result["role"]:
            og_title = soup.find("meta", attrs={"property": "og:title"})
            if og_title:
                result["role"] = og_title.get("content", "")[:100]

    except Exception as e:
        result["error"] = str(e)

    return result