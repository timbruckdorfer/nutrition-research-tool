# Nutrition Research Paper Analyzer

AI-powered web application that automatically extracts structured data from nutrition and health research papers (PDFs) and exports results to Excel.

## What It Does

Upload research papers → AI extracts key information → Download formatted Excel spreadsheet

**Extracted Fields:**
- Authors, Publication Year, Journal, DOI, Country
- Paper Type (original/review/cohort/etc.)
- Study Objective & Methodology
- Sample Size, Duration, Inclusion Criteria
- Conclusions

## Tech Stack

**Backend (Python):** FastAPI, OpenAI GPT-4o, PyMuPDF, OpenPyXL, MCP Architecture

**Frontend (JavaScript):** React 18, Material UI, Vite, Axios

## Deployment

| Service  | Platform | URL |
|----------|----------|-----|
| Frontend | Vercel   | https://nutrition-research-tool.vercel.app |
| Backend  | Render   | https://nutrition-research-api.onrender.com |

The backend runs on Render's free tier and spins down after 15 minutes of inactivity. The first request after inactivity takes ~30-60 seconds while the server starts up.

## Local Development

### 1. Backend

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create backend/.env with your OpenAI key:
# OPENAI_API_KEY=your-key-here
# OPENAI_MODEL=gpt-4o

uvicorn api.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Project Structure

```
├── render.yaml                 # Render deployment blueprint
├── backend/
│   ├── api/
│   │   ├── main.py             # FastAPI endpoints
│   │   ├── mcp_client.py       # MCP tool orchestration
│   │   └── excel_generator.py  # Excel generation
│   ├── mcp_server/
│   │   ├── tools/              # PDF extractor, LLM analyzer
│   │   └── prompts/            # GPT-4o prompt templates
│   ├── requirements.txt
│   └── .env                    # API keys (not committed)
│
└── frontend/
    ├── src/
    │   ├── App.jsx             # Main app with state management
    │   ├── theme.js            # MUI theme configuration
    │   └── components/         # UI components
    ├── package.json
    └── vite.config.js
```

## Cost Estimate

- ~$0.11 per paper (GPT-4o)
- ~30-60 seconds processing per paper

---

Built with FastAPI, React, and GPT-4o
