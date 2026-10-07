# CodeLens AI

CodeLens AI is an AI-powered codebase intelligence platform designed to help developers understand unfamiliar GitHub repositories faster.

It analyzes repository structure, detects frontend and backend relationships, identifies request and data flows, surfaces engineering insights, and provides repository-grounded AI assistance.

---

## Features

- GitHub repository analysis
- Repository overview generation
- Architecture detection
- Component graph generation
- Frontend-to-backend request flow detection
- Data flow analysis
- External API detection
- Database and data-layer detection
- Dependency analysis
- Engineering insights
- Route coverage analysis
- File hotspot analysis
- Repository-grounded AI assistant
- Retrieval-Augmented Generation (RAG)
- ChromaDB vector storage
- Groq LLM integration
- Repository history
- Persistent analysis caching
- Commit SHA-aware cache validation
- Structured error handling
- Multi-repository support

---

## Problem Statement

Understanding an unfamiliar codebase can take a significant amount of time.

Developers often need to manually inspect:

- folders
- configuration files
- dependencies
- frontend API calls
- backend routes
- controllers
- services
- databases
- external APIs
- architecture patterns

CodeLens AI reduces this effort by automatically analyzing a GitHub repository and presenting important architectural and engineering information in one place.

---

## How It Works

```text
GitHub Repository
        ↓
Repository Metadata
        ↓
Repository Tree
        ↓
Source File Discovery
        ↓
Language / Framework Detection
        ↓
Import Analysis
        ↓
Frontend Request Detection
        ↓
Backend Route Detection
        ↓
Controller / Service Resolution
        ↓
Database & External API Detection
        ↓
Relationship Graph
        ↓
Architecture + Request Flow + Data Flow
        ↓
Engineering Insights
        ↓
RAG Indexing
        ↓
ChromaDB
        ↓
Groq LLM
        ↓
Repository-Grounded AI Answers
```

---

## System Architecture

CodeLens AI follows a client-server architecture.

```text
React + Vite Frontend
        ↓
FastAPI Backend
        ↓
GitHub API
        ↓
Repository Analyzer
        ↓
Architecture Engine
        ↓
Insights Engine
        ↓
RAG Pipeline
        ↓
ChromaDB
        ↓
Groq LLM
```

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- Axios
- React Router
- React Markdown
- Remark GFM
- Lucide React
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- HTTPX
- Pydantic
- python-dotenv

### AI / RAG

- Groq API
- ChromaDB
- Hugging Face tooling
- Semantic retrieval
- Lexical reranking
- Repository-grounded context generation

### Storage

- SQLite
- ChromaDB
- File-based analysis cache

### External Integration

- GitHub REST API

---

## Repository Analysis

The repository analyzer provides high-level information about a repository.

It detects:

- repository name
- repository owner
- description
- default branch
- programming languages
- primary language
- primary framework
- build tool
- architecture type
- dependencies
- file count
- folder count
- root modules

---

## Architecture Analyzer

The architecture engine performs deeper static analysis of the repository.

It can detect:

- frontend files
- backend files
- components
- pages
- controllers
- services
- middleware
- routes
- configuration files
- entry points
- internal imports
- external dependencies
- frontend requests
- backend endpoints
- data technologies
- external APIs

It then builds relationships between those elements.

---

## Request Flow Detection

CodeLens AI connects detected frontend requests with backend routes.

Example:

```text
Frontend Component
        ↓
API Service
        ↓
POST /api/example
        ↓
Backend Route
        ↓
Controller
        ↓
Service
```

Supported request and routing patterns include:

- Axios
- Axios instances
- Fetch API
- API wrappers
- Dynamic URLs
- Template strings
- Express routes
- Express routers
- FastAPI routes
- Flask routes
- Spring-style routes

---

## Data Flow Detection

CodeLens AI detects database and data-layer technologies based on repository usage.

Examples include:

- PostgreSQL
- Prisma
- Redis
- MongoDB
- Mongoose
- SQLite
- SQLAlchemy
- Firebase
- Supabase
- DynamoDB
- MySQL

Example:

```text
Frontend
   ↓
Backend Route
   ↓
Controller
   ↓
Service
   ↓
Prisma
   ↓
PostgreSQL
```

The analyzer attempts to distinguish actual runtime usage from configuration-only references to reduce false positives.

---

## External API Detection

CodeLens AI can detect external services such as:

- Groq
- OpenAI
- Anthropic
- Google Gemini
- Mistral
- Cohere
- Hugging Face
- Stripe
- SendGrid
- Twilio

Example:

```text
Frontend Request
       ↓
Backend Route
       ↓
Controller
       ↓
LLM Service
       ↓
Groq API
```

---

## Engineering Insights

The Insights module provides engineering-level information about the repository.

It includes:

- analyzed source file count
- frontend file count
- backend file count
- shared file count
- import relationships
- external dependencies
- external API calls
- data connections
- detected data technologies
- largest files
- most imported files
- files with highest outgoing imports
- route coverage
- engineering findings

---

## Route Coverage

CodeLens AI compares detected frontend requests with detected backend routes.

Example:

```text
Frontend Requests: 17
Backend Routes: 25
Matched Requests: 17
Unmatched Requests: 0
Coverage: 100%
```

This helps identify potentially broken or unmatched API relationships.

---

## AI Assistant

CodeLens AI includes a repository-grounded AI assistant.

Developers can ask questions such as:

```text
Where is authentication implemented?

Which file handles image generation?

How does the frontend communicate with the backend?

Which database is used?

Where is the Groq API called?

Explain the request flow for this endpoint.
```

Instead of relying only on general LLM knowledge, the assistant retrieves relevant repository content before generating an answer.

---

## RAG Pipeline

The assistant uses Retrieval-Augmented Generation.

```text
Repository Files
      ↓
Source File Filtering
      ↓
Code Chunking
      ↓
Metadata Generation
      ↓
Embeddings
      ↓
ChromaDB
      ↓
User Question
      ↓
Semantic Retrieval
      ↓
Lexical + Path + Symbol Reranking
      ↓
Relevant Code Context
      ↓
Groq LLM
      ↓
Grounded Answer
```

---

## Caching

CodeLens AI includes persistent analysis caching.

Cache entries are associated with:

- repository owner
- repository name
- analysis type
- commit SHA
- analyzer version

If the repository has not changed, CodeLens AI can reuse previous analysis instead of running everything again.

Example:

```json
{
  "cached": true,
  "status": "insights cache current"
}
```

---

## Repository History

The application stores previously analyzed repositories using SQLite.

Stored information can include:

- repository URL
- repository name
- owner
- description
- primary language
- primary framework
- architecture
- default branch
- commit SHA
- analysis count
- timestamps

---

## Error Handling

The backend includes structured error handling for invalid input, GitHub failures, network issues, and unexpected server errors.

```text
200 - Successful analysis

400 - Invalid GitHub repository URL

404 - Repository not found or inaccessible

422 - Repository contains no analyzable files

429 - GitHub API rate limit reached

503 - External service unavailable

504 - External service timeout

500 - Unexpected internal server error
```

Raw internal Python errors are not exposed directly to the frontend.

---

## Project Structure

```text
CodeLens AI/
│
├── backend/
│   │
│   ├── models/
│   │   ├── architecture.py
│   │   ├── history.py
│   │   ├── insights.py
│   │   └── repository.py
│   │
│   ├── routes/
│   │   ├── architecture.py
│   │   ├── assistant.py
│   │   ├── history.py
│   │   ├── insights.py
│   │   └── repository.py
│   │
│   ├── services/
│   │   ├── analysis_cache_service.py
│   │   ├── architecture_service.py
│   │   ├── github_service.py
│   │   ├── history_service.py
│   │   ├── insights_service.py
│   │   ├── llm_service.py
│   │   ├── overview_service.py
│   │   └── rag_service.py
│   │
│   ├── analysis_cache/
│   ├── chroma_db/
│   ├── data/
│   │   └── codelens.db
│   │
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

## API Endpoints

### System

```http
GET /
GET /health
```

### Repository Analysis

```http
POST /api/repository/analyze
```

### Architecture Analysis

```http
POST /api/architecture/analyze
```

### Engineering Insights

```http
POST /api/insights/analyze
```

### AI Assistant

```http
POST /api/assistant/status
POST /api/assistant/index
POST /api/assistant/retrieve
POST /api/assistant/ask
```

### Repository History

```http
POST /api/history
GET /api/history
GET /api/history/repository
DELETE /api/history/repository
DELETE /api/history
```

---

## Example Request

```json
{
  "repo_url": "https://github.com/username/repository"
}
```

---

# Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/CSWcdr/codelens-ai.git
cd codelens-ai
```

---

## 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```bash
touch .env
```

Add:

```env
APP_NAME=CodeLens AI API
APP_VERSION=1.0.0

ENVIRONMENT=development
DEBUG=true

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

GITHUB_TOKEN=your_github_personal_access_token_here

GROQ_API_KEY=your_groq_api_key_here

GROQ_MODEL=openai/gpt-oss-120b
```

Start the backend:

```bash
uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## 3. Frontend Setup

Open another terminal.

Navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a `.env` file:

```bash
touch .env
```

Add:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

---

## Production Build

Build the frontend with:

```bash
npm run build
```

The production build will be generated inside:

```text
frontend/dist/
```

---

## Deployment Architecture

The planned production deployment is:

```text
Vercel
   ↓
React / Vite Frontend
   ↓
Railway
   ↓
FastAPI Backend
   ↓
GitHub API
Groq API
ChromaDB
SQLite
Analysis Cache
```

Frontend environment variable:

```env
VITE_API_BASE_URL=https://your-backend-domain
```

Backend production environment example:

```env
APP_NAME=CodeLens AI API
APP_VERSION=1.0.0

ENVIRONMENT=production
DEBUG=false

CORS_ORIGINS=https://your-frontend-domain.vercel.app

GITHUB_TOKEN=your_github_token

GROQ_API_KEY=your_groq_api_key

GROQ_MODEL=openai/gpt-oss-120b
```

Backend production command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Regression Testing

CodeLens AI has been tested against multiple repository structures.

Testing included:

- repository analysis
- architecture analysis
- engineering insights
- frontend request detection
- backend route detection
- request flow matching
- external API detection
- data technology detection
- cache validation
- invalid URL handling
- unavailable repository handling

The analyzer was tested against multiple real repositories instead of being designed specifically for one project.

---

## Example End-to-End Flow

A detected full-stack application flow may look like:

```text
Frontend Page
     ↓
API Service
     ↓
POST /gateway/chat
     ↓
Backend Route
     ↓
Controller
     ↓
Service
     ↓
Groq API
     ↓
Prisma
     ↓
PostgreSQL
     ↓
Redis
```

---

# Engineering Challenges

## Generic Repository Analysis

One of the main challenges was ensuring that CodeLens AI did not work only for one specific repository.

The analyzer was designed around repository patterns instead of hardcoded repository names.

It supports different request and backend patterns such as:

```text
Axios
Fetch
Axios instances
API wrappers
Express
FastAPI
Flask
Spring
```

---

## Request Matching

Frontend and backend routes can represent parameters differently.

Example:

```text
Frontend:
/api/users/${id}

Backend:
/api/users/:id
```

or:

```text
Backend:
/api/users/{id}
```

CodeLens AI normalizes these patterns before attempting route matching.

---

## External Provider Detection

External APIs are not always called using direct HTTP requests.

Some repositories use SDKs instead.

CodeLens AI therefore detects providers using:

- SDK imports
- dependency information
- service usage
- import relationships
- source-code patterns

This allows external services such as Groq to be detected even when there is no direct external URL inside the code.

---

## Data-Layer Precision

Configuration variables alone should not prove that a database is actively being used.

CodeLens AI attempts to distinguish:

```text
Configuration Evidence
```

from:

```text
Runtime Data-Layer Usage
```

This helps reduce false positives.

---

## Performance

Repository analysis may involve fetching and inspecting many files.

CodeLens AI improves performance using:

- asynchronous HTTP requests
- concurrent file fetching
- repository filtering
- SHA-aware caching
- analyzer-version-aware caching
- persistent RAG indexing

---

# Current Limitations

CodeLens AI is based largely on static repository analysis and therefore cannot perfectly understand every possible codebase.

Current limitations include:

- highly dynamic runtime-generated routes may not be detected
- uncommon custom frameworks may require additional analyzers
- very large repositories may require further optimization
- complex custom API wrappers may be difficult to resolve statically
- external API detection depends on recognizable source-code or dependency patterns
- private repository support is currently limited
- some framework-specific patterns may require future improvements

---

# Future Improvements

Possible future improvements include:

- private GitHub repository support
- GitHub OAuth
- organization-level repository analysis
- multi-repository analysis
- improved Next.js support
- improved NestJS support
- AST-based parsing
- language server integration
- deeper symbol resolution
- function-level call graphs
- automatic documentation generation
- vulnerability analysis
- code quality scoring
- test coverage analysis
- repository comparison
- AI-generated onboarding documentation
- pull request analysis
- real-time repository synchronization
- persistent AI chat history
- authentication and user accounts
- cloud-based persistent storage

---

# Why CodeLens AI?

Developers frequently enter large codebases without enough documentation.

CodeLens AI provides a faster starting point by combining:

```text
Static Analysis
+
Architecture Discovery
+
Engineering Insights
+
Retrieval-Augmented Generation
+
Large Language Models
```

into one developer-focused codebase intelligence platform.

---

# Author

**Nabeel Ahmed**

GitHub:

```text
https://github.com/CSWcdr
```

---

# Repository

```text
https://github.com/CSWcdr/codelens-ai
```

---

# Project Status

```text
Core Development       ✅
Repository Analysis    ✅
Architecture Engine    ✅
Request Flow Engine    ✅
Data Flow Analysis     ✅
Engineering Insights   ✅
AI Assistant / RAG     ✅
Caching                ✅
Repository History     ✅
Error Hardening        ✅
Multi-Repo Testing     ✅
Deployment             🚧
```

---

# License

This project is intended for educational, portfolio, and development purposes.

---

# Final Note

CodeLens AI was built to make unfamiliar codebases easier to understand.

Instead of manually searching through hundreds of files, developers can use the platform to explore repository structure, architecture, dependencies, request flows, data connections, engineering insights, and repository-grounded AI answers from one workspace.
