# 🧠 ResearchMind AI

<p align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/ChromaDB-FC60A8?style=for-the-badge" alt="ChromaDB" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License" />
</p>

ResearchMind AI is an end-to-end, enterprise-grade AI research assistant designed to interact with scientific literature and documents using advanced **Retrieval-Augmented Generation (RAG)**. Users can upload research PDFs, automatically index their semantic contents into a vector database, and perform structured, multi-turn, source-cited conversations powered by Large Language Models.

---

### 🌐 Live Demo
* **Frontend Web App (Vercel):** [https://research-mind-ai-git-main-mohit-25-techs-projects.vercel.app](https://research-mind-ai-git-main-mohit-25-techs-projects.vercel.app)
* **Backend API Gateway (Render):** [https://researchmind-ai-2-nyd0.onrender.com](https://researchmind-ai-2-nyd0.onrender.com)

---

## ✨ Core Features

* 🔐 **Secure Google OAuth & JWT Sessions** — Full user isolation, storing private conversation histories, documents, and vector namespaces safely.
* 📄 **Automated PDF Processing** — Intelligent ingestion pipelines that handle parsing, clean text chunking, and metadata generation.
* ⚡ **High-Speed Cloud Embeddings** — Integrated with Google Gemini Embeddings (`text-embedding-004`) for high-fidelity semantic parsing without local RAM constraints.
* 📦 **Vector Database & Hybrid Search** — Uses ChromaDB for low-latency similarity queries across thousands of research passages.
* 💬 **Smart Suggested Questions** — Automatically presents context-relevant suggested prompts when documents are selected.
* 📈 **Contextual Source Citations** — Every generated answer includes exact references to retrieved document fragments and page numbers.
* ✏️ **Premium Conversation Workspace** — Smooth title generation, inline renaming, and clean, relative date-grouped threads.
* ⚙️ **Administrative Footers** — Global controls to quickly clear conversation histories or purge documents, resetting the vector collections cleanly.

---

## 🏗️ Architecture & Processing Workflow

### System Architecture
```
┌─────────────────┐        Google Token        ┌──────────────────┐
│  React Frontend  ├──────────────────────────>│  FastAPI Backend │
└────────┬────────┘                            └────────┬─────────┘
         │                                              │
         │ Fetch Details / Chat Query                   │ Invoke Chain
         ▼                                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LangChain Pipeline                        │
│                                                                 │
│   ┌───────────────┐     ┌──────────────┐     ┌──────────────┐   │
│   │   ChromaDB    │<────┤  Gemini Embed│     │   Groq LLM   │   │
│   │ (Vector Store)│     │(text-embed)  │     │(llama3-8b)   │   │
│   └───────┬───────┘     └──────────────┘     └──────┬───────┘   │
│           │                                         │           │
│           └────────────────> Retriever ─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
                                                        [Final Answer]
```

### PDF Ingestion & Query Lifecycle
```
[User Uploads PDF] ──> [PDF Parsing] ──> [Text Chunking] ──> [Vector Embedding] ──> [ChromaDB Save]
                                                                                            │
[LLM Response] <── [Prompt Assembly] <── [Semantic Context Retrieval] <── [User Question] ──┘
```

---

## 📂 Project Structure

```
├── app/                      # FastAPI Backend Application
│   ├── api/                  # REST Endpoint Routers (Chat, Documents, Uploads)
│   ├── auth/                 # Google OAuth Verification & JWT Helpers
│   ├── chains/               # RAG Pipeline Chains & Orchestration
│   ├── config/               # Settings, DB Path, & Env Bindings
│   ├── models/               # Pydantic Schemas & LLM Configurations
│   └── services/             # Database Connection & File Systems
├── frontend/                 # Vite + React Frontend Client
│   ├── src/
│   │   ├── api/              # Axios Client & Server Interfaces
│   │   ├── components/       # Reusable Layout Elements (Sidebar, ChatBox)
│   │   ├── context/          # Global Context Providers (Auth)
│   │   ├── hooks/            # Custom Hook Wrappers (useChat, useDocuments)
│   │   ├── pages/            # Core Views (Landing, Dashboard)
│   │   └── types/            # TypeScript Interface Declarations
└── requirements.txt          # Python Third-Party Dependencies
```

---

## 🔌 API Documentation

| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `POST` | `/auth/google` | Verifies Google credentials, auto-registers users, and issues JWT tokens. | No |
| `GET` | `/conversations` | Lists all active conversation threads for the logged-in user. | Yes |
| `PATCH` | `/conversations/{id}` | Renames a specific conversation title. | Yes |
| `DELETE` | `/conversations` | Purges all conversation history logs for the active user. | Yes |
| `POST` | `/upload` | Receives and chunks PDF documents, generating vector indexes. | Yes |
| `GET` | `/documents` | Lists all uploaded research documents for the user. | Yes |
| `DELETE` | `/documents` | Completely purges the user's document database and ChromaDB vectors. | Yes |
| `POST` | `/chat` | Processes queries synchronously returning context-aware answers. | Yes |
| `POST` | `/stream-chat` | Streams LLM response chunks in real-time. | Yes |

---

## ⚙️ Environment Variables Setup

### Backend Environment Variables (`.env`)
| Variable | Description |
|:---|:---|
| `GOOGLE_API_KEY` | Developer Google Cloud API Key (for Gemini Embeddings). |
| `GROQ_API_KEY` | Groq Console API Key (for Llama model inferencing). |
| `GOOGLE_CLIENT_ID` | Google Console client ID. |
| `JWT_SECRET` | Secret hash signature for signing session tokens. |
| `DATABASE_PATH` | Storage location path for SQLite. |
| `CHROMA_DB_PATH` | Directory for vector index files. |

### Frontend Environment Variables (`frontend/.env`)
| Variable | Description |
|:---|:---|
| `VITE_API_URL` | Base endpoint URL pointing to the FastAPI server. |
| `VITE_GOOGLE_CLIENT_ID` | Client credential matching the Google Login application. |

---

## 🚀 Installation & Local Development

### 1. Backend Service Configuration
Ensure Python 3.10+ is installed on your local host:
```bash
# Clone the repository
git clone https://github.com/Mohit-25-tech/ResearchMind-AI.git
cd ResearchMind-AI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start local backend reloading server
uvicorn app.main:app --reload
```
*The backend API server will listen at `http://localhost:8000`.*

### 2. Frontend Development Server
Ensure Node.js v18+ is installed on your system:
```bash
cd frontend

# Install package dependencies
npm install

# Start Vite live reload development server
npm run dev
```
*Open your browser and navigate to `http://localhost:5173`.*

---

## 🗺️ Future Roadmap

- [ ] **Multi-Document Comparative Search** — Ask questions across multiple papers simultaneously.
- [ ] **Dark Mode Support** — Seamless light/dark mode transitions.
- [ ] **Export Chat Logs** — Export conversation transcripts as Markdown or PDF.
- [ ] **ArXiv Integration** — Search and import papers directly using ArXiv IDs.
- [ ] **Shared Workspaces** — Collaborative workspaces for research teams.

---

## 🛡️ Security Implementations
1. **Google OAuth 2.0 Identity Token Verification** — Prevents credential spoofing.
2. **Stateful JWT Auth Guards** — Keeps endpoints secured from unauthenticated request payloads.
3. **Database Row-Level Separation** — Queries explicitly filter records by active `user_id`, maintaining strong security boundaries.

---

## 📄 License
This project is licensed under the terms of the [MIT License](LICENSE).

---

## 👤 Author
**Mohit Nirmal**
* **GitHub:** [@Mohit-25-tech](https://github.com/Mohit-25-tech)
* **LinkedIn:** [Mohit Nirmal](https://www.linkedin.com/in/mohit-nirmal-2a6951335/)
