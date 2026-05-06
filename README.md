# ULGA_IntelligentQnASystem# ULGA By-Law Question-Answering System

This project scaffold implements the required stack:
- Frontend: React (Vite)
- Backend: Django + Django REST Framework
- DB: MySQL (`ulgaragsystem` on `localhost:3306`)
- RAG: LangChain + FAISS
- Local LLM: Ollama with `qwen3-coder:latest`

Source document expected at:
- `project-code/resources/university-of-lethbridge-and-ulgsa-2025-collective-agreement.pdf`

## Project Structure

- `backend/` Django API, auth, RBAC, document ingestion, RAG, analytics
- `frontend/` React UI for login, Q&A, history, feedback, upload, admin operations
- `resources/` by-law source files
- `docker-compose.yml` local orchestration (MySQL + backend + frontend)

## Backend Features Implemented

- JWT login endpoint
- Role-based access (`member`, `executive`, `admin`)
- Question submission with validation and restricted content checks
- RAG retrieval from FAISS with grounded answer generation via Ollama
- Source citations in answer payload
- Document upload (PDF, DOCX, TXT/MD), chunking, embedding, FAISS indexing
- Version list endpoint and admin index rebuild endpoint
- Search history and threaded follow-up support (`parent_id`)
- Helpful / Not Helpful feedback endpoint
- FAQ auto-generation from repeated questions
- Admin analytics endpoint and manual answer override endpoint
- Access logging and audit logging models

## Quick Start (Docker)

1. Ensure Ollama is running on host and model exists:
   - `ollama pull qwen3-coder:latest`
   - `ollama pull qwen3-embedding:latest`
2. From `project-code/` run:
   - `docker compose up --build`
3. Backend API: `http://localhost:8000/api/`
4. Frontend UI: `http://localhost:5173`

## Quick Start (Without Docker)

### Backend

1. Open terminal in `project-code/backend`
2. Create `.env` from `.env.example`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run migrations and create admin user:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py createsuperuser`
5. Start server:
   - `python manage.py runserver`

### Frontend

1. Open terminal in `project-code/frontend`
2. Install dependencies:
   - `npm install`
3. Create `.env` from `.env.example`
4. Start frontend:
   - `npm run dev`

## Important Notes

- To include `role` in JWT payload for frontend role display, add a custom token serializer in backend if needed.
- Initial ingestion can be done by logging in as executive/admin and uploading the PDF from the UI.
- For production, enable TLS, tighten CORS, and configure secure secrets management.

## RAG Tuning (Ollama)

- Recommended starting values: `OLLAMA_EMBED_BATCH_SIZE=1`, `RAG_CHUNK_SIZE=400`, `RAG_CHUNK_OVERLAP=80`
- `OLLAMA_EMBED_BATCH_SIZE` controls how many chunks are embedded per request during index build/append.
   - Lower values reduce Ollama context-length errors on large corpora (safe default: `1`).
   - Higher values may improve indexing speed on stronger machines.
- `RAG_CHUNK_SIZE` controls text length per chunk before embedding (default: `400`).
- `RAG_CHUNK_OVERLAP` controls overlap between adjacent chunks (default: `80`).
   - If rebuild fails with input/context errors, lower `RAG_CHUNK_SIZE` and/or keep `OLLAMA_EMBED_BATCH_SIZE` low.
=======
# ULGA_IntelligentQnASystem# ULGA By-Law Question-Answering System

This project scaffold implements the required stack:
- Frontend: React (Vite)
- Backend: Django + Django REST Framework
- DB: MySQL (`ulgaragsystem` on `localhost:3306`)
- RAG: LangChain + FAISS
- Local LLM: Ollama with `qwen3-coder:latest`

Source document expected at:
- `project-code/resources/university-of-lethbridge-and-ulgsa-2025-collective-agreement.pdf`

## Project Structure

- `backend/` Django API, auth, RBAC, document ingestion, RAG, analytics
- `frontend/` React UI for login, Q&A, history, feedback, upload, admin operations
- `resources/` by-law source files
- `docker-compose.yml` local orchestration (MySQL + backend + frontend)

## Backend Features Implemented

- JWT login endpoint
- Role-based access (`member`, `executive`, `admin`)
- Question submission with validation and restricted content checks
- RAG retrieval from FAISS with grounded answer generation via Ollama
- Source citations in answer payload
- Document upload (PDF, DOCX, TXT/MD), chunking, embedding, FAISS indexing
- Version list endpoint and admin index rebuild endpoint
- Search history and threaded follow-up support (`parent_id`)
- Helpful / Not Helpful feedback endpoint
- FAQ auto-generation from repeated questions
- Admin analytics endpoint and manual answer override endpoint
- Access logging and audit logging models

## Quick Start (Docker)

1. Ensure Ollama is running on host and model exists:
   - `ollama pull qwen3-coder:latest`
   - `ollama pull qwen3-embedding:latest`
2. From `project-code/` run:
   - `docker compose up --build`
3. Backend API: `http://localhost:8000/api/`
4. Frontend UI: `http://localhost:5173`

## Quick Start (Without Docker)

### Backend

1. Open terminal in `project-code/backend`
2. Create `.env` from `.env.example`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run migrations and create admin user:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py createsuperuser`
5. Start server:
   - `python manage.py runserver`

### Frontend

1. Open terminal in `project-code/frontend`
2. Install dependencies:
   - `npm install`
3. Create `.env` from `.env.example`
4. Start frontend:
   - `npm run dev`

## Important Notes

- To include `role` in JWT payload for frontend role display, add a custom token serializer in backend if needed.
- Initial ingestion can be done by logging in as executive/admin and uploading the PDF from the UI.
- For production, enable TLS, tighten CORS, and configure secure secrets management.

## RAG Tuning (Ollama)

- Recommended starting values: `OLLAMA_EMBED_BATCH_SIZE=1`, `RAG_CHUNK_SIZE=400`, `RAG_CHUNK_OVERLAP=80`
- `OLLAMA_EMBED_BATCH_SIZE` controls how many chunks are embedded per request during index build/append.
   - Lower values reduce Ollama context-length errors on large corpora (safe default: `1`).
   - Higher values may improve indexing speed on stronger machines.
- `RAG_CHUNK_SIZE` controls text length per chunk before embedding (default: `400`).
- `RAG_CHUNK_OVERLAP` controls overlap between adjacent chunks (default: `80`).
   - If rebuild fails with input/context errors, lower `RAG_CHUNK_SIZE` and/or keep `OLLAMA_EMBED_BATCH_SIZE` low.

