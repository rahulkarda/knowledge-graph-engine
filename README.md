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
| 🌙 **Dark UI** | Clean, distraction-free dark interface |

---

## 🖼️ Demo

> The app runs locally — open **http://localhost:5173** after setup.

**Dashboard** — overview of recent captures, stats, and discovered connections  
**Capture** — 4-tab input panel: Note · File · URL · Voice  
**Graph View** — click any node to open an inline detail panel without leaving the graph  
**Ask AI** — type any question, get an answer with source citations  
**Search** — ranked semantic search across your entire knowledge base  
**Connections** — auto-discovered thematic links between notes  
**Timeline** — all knowledge sorted newest-first, grouped by date  

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
| **Railway** | Python backend container |
| **Vercel** | React frontend |
| **Supabase** | PostgreSQL + file storage |
| **Qdrant Cloud** | Persistent vector store |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (for local Qdrant)

### 1. Start Qdrant
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Backend
```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install fastapi "uvicorn[standard]" pydantic pydantic-settings \
    sqlalchemy aiosqlite greenlet python-multipart httpx beautifulsoup4 lxml

cp .env.example .env               # defaults use SQLite + local Qdrant

uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 4. (Optional) Enable full AI features
```bash
# Semantic search + embeddings
pip install sentence-transformers qdrant-client

# Entity extraction
pip install spacy && python -m spacy download en_core_web_sm

# Voice transcription
pip install openai-whisper
brew install ffmpeg              # macOS
# apt install ffmpeg             # Ubuntu

# Q&A generation
pip install transformers sentencepiece
```

### One-command local stack
```bash
docker-compose up --build
# backend: http://localhost:8000
# frontend: http://localhost:5173
```

---

## 🌍 Deployment

### Backend → Railway

1. Push this repo to GitHub
2. New project on [railway.app](https://railway.app) → **Deploy from GitHub**
3. Set root directory to `backend/`
4. Add environment variables:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db   # from Supabase
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-key
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
ALLOWED_ORIGINS=["https://your-app.vercel.app"]
SECRET_KEY=your-32-char-secret
```

### Frontend → Vercel

1. New project on [vercel.com](https://vercel.com) → import repo
2. Set root directory to `frontend/`
3. Add environment variable:

```env
VITE_API_BASE_URL=https://your-backend.up.railway.app
```

### Services to set up first

| Service | Link | What to do |
|---------|------|------------|
| Supabase | [supabase.com](https://supabase.com) | Create project → copy PostgreSQL URL + anon key |
| Qdrant Cloud | [cloud.qdrant.io](https://cloud.qdrant.io) | Free cluster → copy URL + API key |

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
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

Full interactive docs: **http://localhost:8000/docs**

---

## 🗂 Project Structure

```
knowledge-graph-engine/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
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
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── pages/               # Dashboard, Capture, GraphView, Search, …
│       ├── components/          # graph, ingest, search, qa, layout
│       ├── api/hooks/           # TanStack Query hooks
│       └── store/uiStore.js     # Zustand UI state
│
└── docker-compose.yml
```

---

## 🔮 Roadmap

- [ ] User authentication (Supabase Auth)
- [ ] Mobile-responsive layout
- [ ] Export graph as JSON / CSV
- [ ] Obsidian / Notion import
- [ ] Scheduled digest emails ("your connections this week")
- [ ] Public share links for individual nodes

---

## 📄 License

MIT — use it, fork it, build on it.

---

<p align="center">Built with ❤️ by <a href="https://github.com/rahulkarda">Rahul Karda</a></p>
