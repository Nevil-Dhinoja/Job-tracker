<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:6366f1,100:06b6d4&height=200&section=header&text=Job%20Application%20Tracker&fontSize=42&fontColor=ffffff&fontAlignY=38&desc=n8n%20%2B%20Selenium%20%2B%20Google%20Sheets%20%2B%20Python&descAlignY=58&descSize=16&animation=fadeIn" />
</p>

<p align="center">
  <a href="https://github.com/nevildhinoja/job-tracker/graphs/visitors">
    <img src="https://visitor-badge.laobi.icu/badge?page_id=nevildhinoja.job-tracker&left_color=1e293b&right_color=6366f1&left_text=repo%20visits" alt="visitors" />
  </a>
  &nbsp;
  <img src="https://img.shields.io/github/stars/nevildhinoja/job-tracker?style=flat&color=6366f1&labelColor=1e293b" />
  &nbsp;
  <img src="https://img.shields.io/badge/status-active-06b6d4?style=flat&labelColor=1e293b" />
  &nbsp;
  <img src="https://img.shields.io/badge/made%20with-python-6366f1?style=flat&labelColor=1e293b&logo=python&logoColor=white" />
</p>

<br/>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=6366F1&center=true&vCenter=true&multiline=true&repeat=true&width=700&height=100&lines=Drop+a+.txt+file...;Watch+Chrome+fill+the+form+itself+%F0%9F%A4%96;Job+tracked.+Sheet+updated.+Email+sent.+%E2%9C%85" alt="Typing SVG" />
</p>

---

## ⚡ What Happens When You Drop a File

```
 📄 anthropic_job.txt dropped into watch/
          │
          ▼
 👁️  watcher.py detects it instantly
          │
          ▼
 🔗  n8n webhook fires
          │
          ▼
 🐍  Flask scraper extracts job details
          │
          ▼
 📊  Google Sheets → new row (status: pending)
          │
          ▼
 🤖  Selenium opens form → fills → submits
          │
          ▼
 📸  Screenshot saved to /screenshots
          │
          ▼
 ✅  Sheet updates to DONE
          │
          ▼
 📧  Gmail notification sent
```

---

## 🛠️ Tech Stack

<p align="left">
  <img src="https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white" />
  <img src="https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=googlesheets&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Gmail-EA4335?style=for-the-badge&logo=gmail&logoColor=white" />
  <img src="https://img.shields.io/badge/Chrome-4285F4?style=for-the-badge&logo=googlechrome&logoColor=white" />
</p>

---

## 📁 Project Structure

```
job-tracker/
├── 🐳 docker-compose.yml       → spins up n8n
├── 👁️  watcher.py              → watches for dropped .txt files
├── 📂 watch/
│   ├── your_job.txt            → drop files here
│   └── processed/              → auto-moved after handling
├── 📸 screenshots/             → one PNG per processed job
├── 🔑 credentials/
│   └── google-creds.json       → service account (gitignored)
└── 🐍 scraper/
    ├── app.py                  → Flask API (scrape + trigger)
    ├── scraper.py              → BeautifulSoup job extractor
    ├── submit.py               → Selenium form filler
    ├── form.html               → demo form page
    ├── form_server.py          → serves form on :5002
    └── requirements.txt
```

---

## 🚀 Setup

### 1. Clone & install

```bash
git clone https://github.com/nevildhinoja/job-tracker
cd job-tracker
pip install -r scraper/requirements.txt
```

### 2. Google Sheets credentials

1. [console.cloud.google.com](https://console.cloud.google.com) → New Project → Enable **Google Sheets API**
2. Create **Service Account** → download JSON key → rename to `google-creds.json` → place in `credentials/`
3. Create a Google Sheet named `Job Tracker` with headers:

   | Company | Role | Salary | Deadline | URL | Status | Timestamp |
   |---------|------|--------|----------|-----|--------|-----------|

4. Share the sheet with the service account email as **Editor**

### 3. Gmail app password

> Google Account → Security → 2-Step Verification → App Passwords → create → paste into n8n Email node

### 4. Start everything

```bash
# Terminal 1 — n8n
docker-compose up -d

# Terminal 2 — Flask scraper
cd scraper && python app.py

# Terminal 3 — Demo form
cd scraper && python form_server.py

# Terminal 4 — File watcher
python watcher.py
```

---

## 🎯 Usage

Create a `.txt` file and drop it into `watch/`:

```
url: https://jobsite.com/job/123
company: OpenAI
role: ML Research Engineer
salary: $200k
deadline: 2025-11-01
```

> Only `url` is required. Everything else gets scraped automatically.

**Watch it work in real time:**

```
[NEW]  Detected: openai_job.txt
[SEND] Processing → {'company': 'OpenAI', 'role': 'ML Research Engineer' ...}
[OK]   n8n accepted openai_job.txt
[MOVE] openai_job.txt → processed/ (done)
```

Chrome opens → form fills → screenshot saved → sheet updates to ✅ done → email arrives.

---

## 📊 Google Sheet Output

| Company | Role | Salary | Deadline | URL | Status | Timestamp |
|---------|------|--------|----------|-----|--------|-----------|
| OpenAI | ML Research Engineer | $200k | 2025-11-01 | https://... | ✅ done | 2026-05-19 15:30 |
| Anthropic | AI Engineer | $220k | 2025-12-15 | https://... | ✅ done | 2026-05-19 15:45 |

---

## 🔑 Environment Notes

- n8n runs locally on `http://localhost:5678`
- Flask scraper on `http://localhost:5001`
- Demo form on `http://localhost:5002/form`
- n8n reaches Flask via `http://host.docker.internal:5001` (Docker → host bridge)

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:06b6d4,100:6366f1&height=120&section=footer&animation=fadeIn" />
</p>
