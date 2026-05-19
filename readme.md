# Job Application Tracker

Automated job tracking pipeline — drop a `.txt` file, the rest handles itself.

## What it does

```
Drop .txt file into watch/
      ↓
watcher.py detects it instantly
      ↓
n8n webhook → Flask scraper extracts job details
      ↓
Google Sheets row added (status: pending)
      ↓
Selenium opens demo form, fills & submits
      ↓
Sheet updates to done + screenshot saved
      ↓
Gmail notification sent
```

## Stack

- **n8n** (Docker) — workflow orchestration
- **Python + Flask** — scraper API and webhook receiver
- **Selenium** — automated form submission
- **Google Sheets** — job tracking database
- **watchdog** — file system watcher

## Setup

### 1. Prerequisites

- Docker Desktop
- Python 3.x
- Chrome browser

### 2. Google Sheets credentials

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → New Project
2. Enable **Google Sheets API**
3. Create a **Service Account** → download JSON key
4. Rename it `google-creds.json` → place in `credentials/`
5. Create a Google Sheet named `Job Tracker` with headers:
   `Company | Role | Salary | Deadline | URL | Status | Timestamp`
6. Share the sheet with the service account email (Editor access)

### 3. Start n8n

```bash
docker-compose up -d
```

Open `http://localhost:5678` → import the workflow → activate it.

### 4. Gmail app password

Google Account → Security → 2-Step Verification → App Passwords → create one → paste into n8n Email node credentials.

### 5. Install dependencies

```bash
cd scraper
pip install -r requirements.txt
```

### 6. Run all services

Open 3 terminals:

```bash
# Terminal 1 — Flask scraper + trigger
cd scraper && python app.py

# Terminal 2 — Demo form server
cd scraper && python form_server.py

# Terminal 3 — File watcher
python watcher.py
```

## Usage

Create a `.txt` file and drop it into the `watch/` folder:

```
url: https://jobsite.com/job/123
company: OpenAI
role: ML Research Engineer
salary: $200k
deadline: 2025-11-01
```

Only `url` is required. Company, role, salary, deadline are optional — the scraper will attempt to extract them from the page.

The file moves to `watch/processed/` after handling. Screenshots save to `screenshots/`.

## Project structure

```
job-tracker/
├── docker-compose.yml
├── watcher.py
├── watch/
│   └── processed/
├── screenshots/
├── credentials/
│   └── google-creds.json
└── scraper/
    ├── app.py
    ├── scraper.py
    ├── submit.py
    ├── form.html
    ├── form_server.py
    └── requirements.txt
```

## Author

Nevil Dhinoja — [github.com/nevildhinoja](https://github.com/nevildhinoja)