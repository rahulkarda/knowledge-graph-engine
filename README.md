<h1 align="center">🧠 Knowledge Graph Engine</h1>

<p align="center">
  <strong>Your personal second brain — capture everything, connect the dots, ask questions.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi" />
  <img src="https://img.shields.io/badge/React-18.3-61DAFB?style=flat-square&logo=react" />
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-security">Security</a> •
  <a href="#-deployment">Deployment</a> •
  <a href="#-api">API</a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **4 Input Types** | Write notes, upload PDF/DOCX/TXT, paste URLs to scrape, or record voice |
| 🕸️ **Auto Knowledge Graph** | Every note is analysed for entities and linked to related notes automatically |
| 🔍 **Semantic Search** | Search by meaning, not just keywords — finds related notes even with different words |
| 🤖 **Ask AI** | Chat-style Q&A over your entire knowledge base with cited sources |
| 🌐 **Interactive Graph** | Visual force-directed graph of all your nodes and connections |
| 🔗 **Connection Discovery** | Surface non-obvious links between ideas you didn't know were related |
| 🏷️ **Auto-Tagging** | Notes are automatically tagged on ingest |
| 🕐 **Timeline** | Chronological feed of all captured knowledge |
| 🔒 **API Key Auth** | All routes protected — only you can read or write your notes |

---

## 🖼️ Demo

> **Live app:** open the frontend URL after deployment.

**Dashboard** — overview of recent captures, stats, and discovered connections  
**Capture** — 4-tab input panel: Note · File · URL · Voice  
**Graph View** — click any node to open an inline detail panel without leaving the graph  
**Ask AI** — type any question, get an answer with source citations  
**Search** — ranked semantic search across your entire knowledge base  
**Connections** — auto-discovered thematic links between notes  
**Timeline** — all knowledge sorted newest-first, grouped by date  

---

## 🔒 Security

**Your notes are private.** Every API route is protected by a static API key. Without it, all requests return `401 Unauthorized`.

### How it works
- The backend checks for `Authorization: Bearer <API_KEY>` on every request
- The frontend sends the key automatically via `VITE_API_KEY` (a Vercel env var — never exposed in the repo)
- `/health` is the only public endpoint (needed for uptime checks)

### Setting up auth

**Backend (Render):** Set the `API_KEY` environment variable in your Render dashboard:
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Frontend (Vercel):** Add the same key as `VITE_API_KEY` in Vercel project settings → Environment Variables → Production.

> ⚠️ **Local dev:** Leave `API_KEY` empty in `.env` to disable auth completely — no key needed during development.

---

## 🛠 Tech Stack

### Backend
- **FastAPI** — REST API with async SQLAlchemy
- **SQLite** (dev) / **PostgreSQL via Supabase** (prod)
- **Qdrant** — vector embeddings for semantic search (local or Qdrant Cloud)
- **sentence-transformers** `all-MiniLM-L6-v2` — local embeddings, no API key
- **Whisper** `base` — local voice transcription, no API key
- **spaCy** `en_core_web_sm` — NER entity extraction (optional; regex fallback built-in)
- **NetworkX** — graph algorithms for connection discovery
- **PyMuPDF** + **python-docx** — PDF and DOCX parsing
- **BeautifulSoup4** — URL scraping

### Frontend
- **React 18** + **Vite**
- **react-force-graph-2d** — interactive graph visualization
- **TanStack Query** — server state management
- **Zustand** — client UI state
- **Tailwind CSS** — dark-mode design system
- **react-dropzone** — file uploads
- **date-fns** — date formatting

### Deployment (all free tiers)
| Service | Role |
|---------|------|
| **Render.com** | Python backend (auto-deploys on push) |
| **Vercel** | React frontend (auto-deploys on push) |
| **Supabase** | PostgreSQL + file storage (optional) |
| **Qdrant Cloud** | Persistent vector store (optional) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional, for local Qdrant)

### 1. Clone
```bash
git clone https://github.com/rahulkarda/knowledge-graph-engine.git
cd knowledge-graph-engine
```

### 2. Backend
```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install fastapi "uvicorn[standard]" pydantic pydantic-settings \
    sqlalchemy aiosqlite greenlet python-multipart httpx beautifulsoup4 lxml \
    networkx PyMuPDF python-docx apscheduler qdrant-client

cp .env.example .env
# API_KEY is empty by default → auth disabled locally (safe for personal use)

uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

### 4. (Optional) Enable full AI features
```bash
# Semantic search + embeddings
pip install sentence-transformers qdrant-client

# Entity extraction (spaCy)
pip install spacy && python -m spacy download en_core_web_sm

# Voice transcription
pip install openai-whisper && brew install ffmpeg   # macOS

# Local Q&A generation
pip install transformers sentencepiece
```

### One-command local stack (with Qdrant)
```bash
docker-compose up --build
```

---

## 🌍 Deployment

### Option A — Render + Vercel (recommended, no credit card)

**Backend → Render.com**

1. Connect your GitHub repo to [render.com](https://render.com)
2. The `render.yaml` at repo root configures everything automatically
3. After deploy, go to **Environment** → copy the auto-generated `API_KEY`

**Frontend → Vercel**

1. Connect your GitHub repo to [vercel.com](https://vercel.com)
2. Set root directory to `frontend/`
3. Add these environment variables:
```env
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_API_KEY=<same API_KEY from Render>
```

### Option B — Railway + Vercel

1. Connect repo to [railway.app](https://railway.app) (requires free account with payment method on file)
2. Set root directory to `backend/`
3. Add environment variables (see `backend/.env.example`)
4. Deploy frontend to Vercel as above

### Required environment variables (backend)

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes (prod) | Secret key to protect all routes |
| `DATABASE_URL` | No | Defaults to SQLite. Use `postgresql+asyncpg://...` for Postgres |
| `QDRANT_URL` | No | Qdrant endpoint. Defaults to localhost |
| `QDRANT_API_KEY` | No | Required if using Qdrant Cloud |
| `SECRET_KEY` | No | App secret, auto-generated |
| `ALLOWED_ORIGINS` | No | JSON array of allowed CORS origins |

---

## 📡 API Reference

All endpoints require `Authorization: Bearer <API_KEY>` (except `/health`).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (public) |
| `POST` | `/api/v1/ingest/note` | Ingest a text note |
| `POST` | `/api/v1/ingest/file` | Upload PDF, DOCX, or TXT |
| `POST` | `/api/v1/ingest/url` | Scrape and ingest a URL |
| `POST` | `/api/v1/ingest/audio` | Transcribe and ingest audio |
| `GET` | `/api/v1/nodes` | List all nodes (paginated) |
| `GET` | `/api/v1/nodes/{id}` | Get node with entities and edges |
| `DELETE` | `/api/v1/nodes/{id}` | Delete a node |
| `POST` | `/api/v1/search/semantic` | Semantic similarity search |
| `GET` | `/api/v1/search/keyword` | Full-text keyword search |
| `GET` | `/api/v1/graph/full` | Full graph for visualization |
| `GET` | `/api/v1/graph/connections` | Auto-discovered connections |
| `POST` | `/api/v1/graph/discover` | Re-run connection discovery |
| `POST` | `/api/v1/graph/edges` | Create a manual edge |
| `POST` | `/api/v1/qa/ask` | Ask a question over your knowledge base |
| `GET` | `/api/v1/tags` | List all tags |
| `GET` | `/api/v1/timeline` | Chronological knowledge feed |

Interactive docs: **`<your-backend-url>/docs`**

---

## 🗂 Project Structure

```
knowledge-graph-engine/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + CORS + auth
│   │   ├── auth.py              # API key authentication dependency
│   │   ├── config.py            # Settings from .env
│   │   ├── database.py          # SQLAlchemy async engine
│   │   ├── models/              # ORM: Node, Edge, Entity, Tag
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── routes/              # API route handlers
│   │   └── services/
│   │       ├── ingestion/       # text, file, url, audio processors
│   │       ├── nlp/             # entity extractor, auto-tagger
│   │       ├── graph/           # graph builder, connection discovery
│   │       ├── embedding_service.py
│   │       ├── vector_store.py  # Qdrant wrapper
│   │       └── qa_service.py    # RAG pipeline
│   ├── .env.example
│   ├── Dockerfile
│   ├── render.yaml
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── pages/               # Dashboard, Capture, GraphView, Search, …
│       ├── components/          # graph, ingest, search, qa, layout
│       ├── api/
│       │   ├── client.js        # Axios + API key injection
│       │   └── hooks/           # TanStack Query hooks
│       └── store/uiStore.js     # Zustand UI state
│
├── render.yaml                  # Render.com auto-deploy config
└── docker-compose.yml           # Local dev stack
```

---

## 🔮 Roadmap

- [ ] User authentication with multiple accounts (Supabase Auth)
- [ ] Mobile-responsive layout
- [ ] Export graph as JSON / CSV
- [ ] Obsidian / Notion import
- [ ] Scheduled digest emails ("your connections this week")
- [ ] Public share links for individual nodes

---

## 📄 License

MIT — use it, fork it, build on it.

---

<p align="center">Built by <a href="https://github.com/rahulkarda">Rahul Karda</a></p>
