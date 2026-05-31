import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routes import nodes, ingest, search, graph, qa, tags, timeline, edges


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (dev convenience; use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Knowledge Graph Engine",
    description="Personal knowledge graph — ingest, connect, discover.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["nodes"])
app.include_router(edges.router, prefix="/api/v1/graph/edges", tags=["edges"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["qa"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["tags"])
app.include_router(timeline.router, prefix="/api/v1/timeline", tags=["timeline"])


@app.get("/health")
async def health():
    return {"status": "ok"}
