# CodeLens AI

CodeLens AI is an AI-powered codebase intelligence platform that helps developers understand unfamiliar GitHub repositories faster.

It analyzes repository structure, detects frontend and backend relationships, identifies request flows, maps data connections, surfaces engineering insights, and provides repository-grounded AI assistance.

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
- File size and import hotspot analysis
- Route coverage analysis
- Repository-grounded AI assistant
- RAG-based codebase question answering
- ChromaDB vector storage
- Groq LLM integration
- Repository history
- Persistent analysis caching
- Commit SHA-aware cache validation
- Error handling for invalid and unavailable repositories
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

CodeLens AI reduces this effort by automatically analyzing a GitHub repository and presenting the important architectural and engineering information in one place.

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
