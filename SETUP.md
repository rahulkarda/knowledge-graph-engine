# Knowledge Graph Engine — Setup Guide

## Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional, for local Qdrant)

---

## Local Development (Quickest Start)

### 1. Start Qdrant (vector database) via Docker
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Backend
```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy env and configure
cp .env.example .env
# Edit .env if needed (defaults use SQLite + local Qdrant)

# Start the API server
uvicorn app.main:app --reload
```
API available at: http://localhost:8000
Swagger docs: http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
App available at: http://localhost:5173

---

## Full Stack via Docker Compose
```bash
docker-compose up --build
```
This starts backend + Qdrant + frontend together.

---

## Cloud Deployment (Free Tier)

### 1. Supabase (PostgreSQL + file storage)
1. Create account at supabase.com
2. New project → copy the PostgreSQL connection string
3. Create a storage bucket named `uploads`
4. Copy `SUPABASE_URL` and `SUPABASE_KEY` (anon key)

### 2. Qdrant Cloud (vector store)
1. Create account at cloud.qdrant.io
2. Free cluster → copy the cluster URL and API key

### 3. Railway (backend)
1. Connect your GitHub repo to Railway
2. Select the `backend/` folder as the root
3. Set environment variables:
   ```
   DATABASE_URL=postgresql+asyncpg://...supabase.com/postgres
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=...
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=...
   ALLOWED_ORIGINS=["https://your-app.vercel.app"]
   ```

### 4. Vercel (frontend)
1. Connect your GitHub repo to Vercel
2. Set root directory to `frontend/`
3. Set environment variable:
   ```
   VITE_API_BASE_URL=https://your-backend.up.railway.app
   ```

---

## Phase Completion Checklist

- [x] Phase 1 — Backbone: notes, REST API, React UI (no NLP)
- [ ] Phase 2 — NLP + Semantic Search: run `pip install sentence-transformers spacy` then search works
- [ ] Phase 3 — File/URL/Audio: all 4 input types need PyMuPDF, Whisper, httpx, bs4
- [ ] Phase 4 — Graph Visualization: GraphView page uses react-force-graph-2d (already installed)
- [ ] Phase 5 — Connection Discovery + Q&A: `transformers` + flan-t5-base
- [ ] Phase 6 — Timeline, Tags, Polish: already implemented; add DB indexes

---

## Note on NLP Heavy Dependencies

The backend degrades gracefully — if `sentence-transformers`, `spacy`, or `whisper` are not installed, ingest still works but without NLP enrichment. Install them when ready:

```bash
# Phase 2 NLP
pip install sentence-transformers spacy
python -m spacy download en_core_web_sm

# Phase 3 Audio
pip install openai-whisper ffmpeg-python
# Also requires: brew install ffmpeg  (macOS)

# Phase 5 Q&A
pip install transformers sentencepiece
```
