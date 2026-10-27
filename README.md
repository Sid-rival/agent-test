# RAG QA API

A production-grade **Retrieval-Augmented Generation (RAG) document Q&A service**.
Ingest documents, embed and index them into chunks, then ask natural-language
questions answered strictly from your own documents â a single project that
demonstrates the full stack:
FastAPI backend, JWT auth, chunking + embeddings, hybrid vector retrieval,
a pluggable LLM layer, Docker, and CI.

## Highlights (mapped to the roles it targets)
- **Backend / platform**: FastAPI, REST, JWT auth, SQLAlchemy, multi-tenant
  document isolation, health check, Docker + docker-compose, CI (GitHub Actions).
- **Generative AI**: RAG pipeline â chunking, embedding, vector similarity
  retrieval, and a grounded generation layer (pluggable LLM interface).
- **Engineering discipline**: unit tests across auth, RAG flow, tenant
  isolation, chunking, and embeddings.

## Quickstart (offline, no API keys)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then:
```bash
curl -s localhost:8000/health
API=http://localhost:8000/api/v1
curl -s -X POST $API/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"a@x.com","password":"secret123"}'
TOKEN=$(curl -s -X POST $API/auth/login -d 'username=a@x.com&password=secret123' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -X POST $API/documents -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"title":"RAG","content":"RAG combines retrieval with generation..."}'
curl -s -X POST $API/documents/query -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"question":"What is RAG?"}'
```

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Uses PostgreSQL in production; SQLite in tests/local.

## Architecture
```
Client âââ¶ FastAPI (/api/v1/auth|documents) âââ¶ SQLAlchemy
   auth â                                        âââ users
        â                                        âââ documents â chunks â embeddings
        âââ JWT                                  âââ RAG query: embed â retrieve â LLM
```
