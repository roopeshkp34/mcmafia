# Forensic Equity (FE-v1.0) — The Divergence Engine

Forensic Equity is a specialized financial intelligence platform designed to identify the **"Say-Do Gap"**: the delta between management's qualitative narrative and the quantitative reality of their financial filings.

The project, codenamed **"Divergence Engine,"** utilizes a **Stateful Multi-Agent System** and **Elasticsearch Hybrid Search** to detect when management’s story deviates from the hard numbers.

## 🚀 Key Features

- **The Forensic Schema**: Detects 25 Red Flag categories (e.g., Revenue Pull-Forward, Inventory Bloat, Linguistic Hedging).
- **Hybrid Search**: Combines BM25 keyword matching for exact financial figures with kNN dense vector search for thematic sentiment.
- **Stateful Multi-Agent System**: Leverages LangGraph and specialized agents (like the "Forensic Critic") to analyze filings and transcripts.
- **Deep Traceability**: Every AI claim includes citations with `doc_id`, `page_number`, and `source` metadata.
- **RAG-based Analysis**: "Chat with the Auditor" feature for interactive exploration of indexed financial documents.

## 🛠 Technology Stack

- **Backend**: Python 3.12, FastAPI
- **Coordination**: LangGraph, LangGraph-Supervisor
- **LLM**: Azure OpenAI (GPT models)
- **Search & Vector DB**: Elasticsearch (Hybrid Search)
- **Data Storage**: MongoDB (Motor driver)
- **Parsing**: LlamaParse
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)

## 📦 Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed
- Docker & Docker Compose
- API Keys for Azure OpenAI, Elasticsearch, MongoDB, and LlamaParse.

## ⚙️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:roopeshkp34/mcmafia.git
   cd mcmafia
   ```

2. **Configure Environment Variables**:
   Copy the `sample.env` to `.env` and fill in the required credentials:
   ```bash
   cp sample.env .env
   ```

3. **Install Dependencies**:
   ```bash
   uv sync
   ```

4. **Start Infrastructure (Optional/Docker)**:
   If you wish to run the entire stack via Docker:
   ```bash
   make devb
   ```

## 🏃 Usage

### Running the Backend
To start the FastAPI server with auto-reload:
```bash
make run
```
The server will be available at `http://localhost:8000`.

### API Documentation
Once the server is running, you can access the interactive API docs:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints
- `POST /document-extractor`: Upload and process financial documents.
- `GET /chat`: Interact with the "Chat with the Auditor" agent.

## 🧪 Development

### Makefile Commands
- `make format`: Format code using Ruff.
- `make lint`: Lint code using Ruff.
- `make type`: Run Mypy type checks.
- `make test`: Run Pytest.
- `make up`: Start the environment using Docker Compose.

## 🏗 Architecture Overview

The system operates in four main phases:
1. **Ingestion**: PDFs (10-Ks, 10-Qs) are parsed via LlamaParse and indexed into Elasticsearch.
2. **Hybrid Search**: The "Forensic Critic" agent queries the index using a mix of vector and keyword searches to identify "smoke" signals.
3. **Relational Analysis**: Aggregating sentiment against numerical data to identify contradictions.
4. **Reporting**: Generating forensic tear sheets and evidence-backed summaries for analysts.

---

*Developed by the Thoughtminds Team.*
