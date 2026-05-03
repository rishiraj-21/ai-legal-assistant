# B.Tech Final Year Project Report
# AI-Based Legal Assistant for Personalized Legal Decision Support

---

## 1. PROJECT OVERVIEW (FROM CODE)

| Attribute | Detail |
|-----------|--------|
| **Project Type** | Full-stack AI-powered web application (SPA + API Gateway + AI Engine) |
| **Core Purpose** | Personalized legal decision support for Indian citizens using RAG-powered LLM analysis, dual-agent adversarial reasoning, quantitative risk scoring, and dynamic legal pathway generation |
| **Domain** | Legal Technology (LegalTech) |
| **Target Users** | Indian citizens seeking legal guidance without immediate access to lawyers |

**Key Features Implemented:**
1. RAG-powered legal analysis over Indian statutes and case law
2. Dual-agent adversarial system (Advocate AI vs Opponent AI)
3. Quantitative risk scoring engine (0-100) with 5 weighted factors
4. Dynamic legal pathway generation with document checklists
5. Settlement probability and recommendation engine
6. Hybrid retrieval (FAISS dense + BM25 sparse + RRF fusion + cross-encoder reranking)
7. Automated web crawling of India Code and Indian Kanoon
8. Lawyer directory with real-time chat interface
9. XAI (Explainable AI) with factor-level explanations and risk summaries
10. Production hardening: caching, rate limiting, correlation ID tracing, input validation

---

## 2. FEATURE LIST (STRICT - FROM CODE)

### User-Visible Features

| # | Feature | Description | Implementation |
|---|---------|-------------|----------------|
| 1 | Case Submission | User describes legal issue + selects case type (10 categories) | `frontend/src/app/shared/components/hero-input/hero-input.ts` |
| 2 | Legal Pathway | AI-generated 4-6 step legal procedure with required documents | `frontend/src/app/pages/analysis/sections/legal-pathway/legal-pathway.ts` |
| 3 | Risk Score Gauge | Animated SVG circular gauge showing 0-100 risk with label | `frontend/src/app/pages/analysis/sections/risk-score/risk-score.ts` |
| 4 | Risk Factor Breakdown | 5 bar charts with % value and AI explanation per factor | `risk-score.html` |
| 5 | Adversarial Analysis | Side-by-side Advocate vs Opponent arguments with confidence | `frontend/src/app/pages/analysis/sections/adversarial/adversarial.ts` |
| 6 | Vulnerability Detection | AI-identified weaknesses in user's legal position | `adversarial.ts` (computed from API) |
| 7 | Settlement Strategy | Probability score + recommendation (Negotiate/Litigate/Settle) + reasoning | `frontend/src/app/pages/analysis/sections/negotiation/negotiation.ts` |
| 8 | Lawyer Directory | 6 verified lawyers with filtering by specialization and search | `frontend/src/app/pages/consult/consult.ts` |
| 9 | Lawyer Chat | Real-time messaging UI with selected lawyer | `frontend/src/app/shared/components/chat-dialog/` |
| 10 | Toast Notifications | Success/error/info toasts (rate limit, network error, server error) | `frontend/src/app/core/services/toast.service.ts` |
| 11 | Scroll Spy Navigation | Sticky tab bar that highlights active section on scroll | `analysis.ts` (IntersectionObserver) |
| 12 | Loading Animation | 5-step staggered loader during AI analysis | `frontend/src/app/shared/components/analysis-loader/analysis-loader.ts` |
| 13 | User Signup | Registration with localStorage persistence | `frontend/src/app/pages/signup/signup.ts` |

### API-Driven Features

| # | Feature | Endpoint | Implementation |
|---|---------|----------|----------------|
| 1 | Full Legal Analysis | `POST /api/analysis/submit` | `backend/Program.cs` -> `ai-engine/app/routers/analysis.py` |
| 2 | Lawyer Listing | `GET /api/lawyers` | `backend/Program.cs` |
| 3 | System Health Check | `GET /health` | `ai-engine/app/routers/health.py` |
| 4 | Admin: Trigger Crawl | `POST /admin/crawl` | `ai-engine/app/routers/admin.py` |
| 5 | Admin: Ingest Seed Data | `POST /admin/ingest-seed` | `ai-engine/app/routers/admin.py` |
| 6 | Admin: Rebuild Indexes | `POST /admin/rebuild-index` | `ai-engine/app/routers/admin.py` |
| 7 | Admin: Retrieval Eval | `POST /admin/evaluate` | `ai-engine/app/routers/admin.py` |
| 8 | Admin: Crawl History | `GET /admin/crawl-history` | `ai-engine/app/routers/admin.py` |

### AI/NLP Features

| # | Feature | Description | Implementation |
|---|---------|-------------|----------------|
| 1 | RAG Retrieval | Hybrid (FAISS + BM25 + RRF + Reranker) over legal corpus | `ai-engine/app/retrieval/hybrid_retriever.py` |
| 2 | Semantic Embeddings | all-MiniLM-L6-v2 (384-dim) for document + query encoding | `ai-engine/app/services/embedding_service.py` |
| 3 | Cross-Encoder Reranking | ms-marco-MiniLM-L-6-v2 for precision reranking | `ai-engine/app/retrieval/reranker.py` |
| 4 | Advocate AI Agent | Gemini prompt: build strongest case FOR user | `ai-engine/app/services/adversarial_service.py` |
| 5 | Opponent AI Agent | Gemini prompt: build strongest case AGAINST user | `ai-engine/app/services/adversarial_service.py` |
| 6 | Risk Factor Scoring | 5-factor weighted scoring with Gemini explanation | `ai-engine/app/services/risk_scoring_service.py` |
| 7 | Pathway Generation | Gemini-generated legal procedure with document list | `ai-engine/app/services/rag_service.py` |
| 8 | Input Sanitization | HTML stripping + whitespace normalization + field validators | `ai-engine/app/models/schemas.py`, `backend/Program.cs` |
| 9 | Automated Crawling | httpx + BeautifulSoup for indiacode.nic.in + indiankanoon.org | `ai-engine/app/crawlers/` |
| 10 | Text Chunking | 512-token paragraphs with 50-token overlap (tiktoken) | `ai-engine/app/processing/chunker.py` |

---

## 3. FUNCTIONAL REQUIREMENTS (DERIVED)

| ID | Requirement |
|----|-------------|
| FR1 | The system shall accept a legal issue description (10-5000 characters) and case type from the user |
| FR2 | The system shall validate case type against a predefined allowlist of 10 categories |
| FR3 | The system shall sanitize user input by stripping HTML tags and collapsing whitespace |
| FR4 | The system shall retrieve top-5 relevant legal documents using hybrid retrieval (dense + sparse + reranking) |
| FR5 | The system shall generate a 4-6 step legal pathway with required documents via Gemini LLM |
| FR6 | The system shall run dual-agent adversarial analysis (Advocate vs Opponent) in parallel |
| FR7 | The system shall compute a 0-100 risk score using 5 weighted factors with individual explanations |
| FR8 | The system shall determine settlement probability based on risk score and adversarial confidence |
| FR9 | The system shall provide a settlement recommendation (Negotiate, Litigate, or Settle) with reasoning |
| FR10 | The system shall display analysis results across 4 interactive sections with scroll-spy navigation |
| FR11 | The system shall cache analysis results for 30 minutes to avoid redundant AI processing |
| FR12 | The system shall rate-limit the analysis endpoint to 10 requests per 60-second window |
| FR13 | The system shall propagate correlation IDs across all three layers for request tracing |
| FR14 | The system shall fall back to mock data when the Python AI engine is unreachable |
| FR15 | The system shall display a searchable and filterable lawyer directory |
| FR16 | The system shall automatically crawl India Code and Indian Kanoon on a weekly schedule |
| FR17 | The system shall rebuild FAISS and BM25 indexes from the database on a scheduled basis |

---

## 4. NON-FUNCTIONAL REQUIREMENTS (INFERRED FROM CODE)

### Performance
| NFR | Justification |
|-----|---------------|
| The system shall respond to cached analysis requests in < 50ms | In-memory cache (`IMemoryCache`) with SHA256 lookup, no I/O |
| The system shall complete non-cached analysis in < 25 seconds | 3 parallel Gemini calls (pathway + advocate + opponent), 60s timeout |
| The frontend shall achieve initial page load in < 2 seconds | Lazy-loaded routes, SSR prerendering for landing page, Tailwind CSS (6KB gzipped) |
| The system shall support concurrent requests via async/await | .NET async handlers + Python asyncio + FAISS in-process |

### Security
| NFR | Justification |
|-----|---------------|
| The system shall sanitize all user input against XSS | HTML tag regex stripping in both .NET and Python layers |
| The system shall enforce rate limiting to prevent abuse | Fixed-window limiter: 10 req/60s per client, 429 response |
| The system shall validate input length boundaries | Min 10, Max 5000 characters enforced server-side |
| The system shall validate case type against allowlist | Prevents injection of arbitrary values |
| The system shall expose correlation IDs for traceability | `X-Correlation-Id` header propagated through all layers |

### Scalability
| NFR | Justification |
|-----|---------------|
| The system architecture supports horizontal scaling | Stateless API layers; FAISS/BM25 can be replaced with Pinecone |
| The knowledge base grows via automated weekly crawling | APScheduler with cron (Sunday 2AM crawl, Wednesday 3AM rebuild) |
| The system uses connection pooling | PostgreSQL async pool (5 main + 10 overflow), HTTP client pooling |

### Reliability
| NFR | Justification |
|-----|---------------|
| The system shall gracefully degrade on AI engine failure | .NET returns mock fallback data if Python returns null |
| Gemini calls include retry logic | 3 retries with exponential backoff (1s->2s->4s) for 429/503 |
| The system logs all errors with correlation IDs | JSON structured logging on both .NET and Python |
| Global error handler prevents unhandled crashes | Middleware catches exceptions, returns structured 500 JSON |

### Usability
| NFR | Justification |
|-----|---------------|
| The system shall display loading animations during analysis | 5-step staggered loader with 1500ms minimum display time |
| The system shall show contextual toast messages for errors | 429 -> "Too many requests", 0 -> "Network error", 500+ -> with correlation ID |
| The frontend shall be responsive across devices | Tailwind responsive utilities (md:, sm: breakpoints) throughout |
| The system shall prerender the landing page for SEO | Angular SSR with Express on port 4000 |

---

## 5. SYSTEM ARCHITECTURE (STRICT)

### Architecture Pattern: 3-Tier with AI Engine

```
+--------------------------------------------------------------------+
|                        FRONTEND (Angular 21)                        |
|  Port: 4200 (dev) / 4000 (SSR)                                    |
|  +----------+  +--------------+  +------------+  +-------------+  |
|  | Landing  |  |  Dashboard   |  |  Analysis  |  |   Consult   |  |
|  | (SSR)    |  |  (HeroInput) |  | (4 sections)|  | (Directory) |  |
|  +----------+  +--------------+  +------------+  +-------------+  |
|       | HTTP Interceptors (baseUrl + error)                        |
+--------------------------------------------------------------------+
                              | POST /api/analysis/submit
                              v
+--------------------------------------------------------------------+
|                    API GATEWAY (.NET 8 Minimal APIs)                |
|  Port: 5058 (HTTP) / 7235 (HTTPS)                                 |
|  +------------+  +----------+  +-----------+  +---------------+   |
|  | Validation |  | Caching  |  | Rate Limit|  | Correlation ID|   |
|  | Sanitize   |  | SHA256+  |  | 10/60s    |  | Middleware    |   |
|  | IValidate  |  | 30min TTL|  | FixedWin  |  | BeginScope    |   |
|  +------------+  +----------+  +-----------+  +---------------+   |
|       | PythonApiClient (HttpClient + CorrelationId)               |
+--------------------------------------------------------------------+
                              | POST /analyze
                              v
+--------------------------------------------------------------------+
|                     AI ENGINE (Python FastAPI)                      |
|  Port: 8000                                                        |
|  +---------------------------------------------------------+      |
|  |                 RAG SERVICE (Orchestrator)                |      |
|  | 1. Hybrid Retrieval -> 2. Parallel Gemini -> 3. Scoring  |      |
|  +---------------------------------------------------------+      |
|  +----------+  +----------+  +----------+  +----------------+     |
|  |  FAISS   |  |  BM25    |  | Reranker |  | Gemini 2.0     |     |
|  | (Dense)  |  | (Sparse) |  | (Cross-  |  | Flash (LLM)    |     |
|  | MiniLM   |  | rank-bm25|  | Encoder) |  | google-genai   |     |
|  +----------+  +----------+  +----------+  +----------------+     |
|  +------------------+  +----------------+  +------------------+   |
|  |   PostgreSQL     |  |   Crawlers     |  |   Scheduler      |   |
|  | (Documents/Cases)|  | IndiaCode +    |  | Sun 2AM + Wed 3AM|   |
|  |  asyncpg pool    |  | IndianKanoon   |  |  APScheduler     |   |
|  +------------------+  +----------------+  +------------------+   |
+--------------------------------------------------------------------+
```

### Data Flow (Analysis Request)

1. User types legal issue -> HeroInput emits `{issue, caseType}`
2. `AnalysisService.setAnalysis()` stores in Angular signal -> navigate to `/analysis`
3. `AnalysisApiService.submitAnalysis()` -> POST `/api/analysis/submit`
4. **baseUrlInterceptor** prepends `http://localhost:5058`
5. **.NET Correlation ID middleware** generates/reads `X-Correlation-Id`
6. **.NET Validation** checks length, case type allowlist, sanitizes HTML
7. **.NET Cache check** - SHA256(issue|caseType) -> if HIT, return cached
8. **.NET PythonApiClient** -> POST `http://localhost:8000/analyze` with correlation ID
9. **Python CorrelationIdMiddleware** reads header, stores in ContextVar
10. **RAGService.analyze()** orchestrates:
    - Hybrid retrieval: FAISS(top-20) + BM25(top-20) -> RRF fusion -> Reranker(top-5)
    - Parallel Gemini calls: Pathway prompt + Advocate prompt + Opponent prompt
    - Risk scoring: 5 weighted factors + settlement computation
11. Response flows back -> .NET `ResponseAdapter.Adapt()` -> cache store -> JSON response
12. Angular receives response -> `AnalysisService.setResult()` -> 4 sections render via `computed()`

---

## 6. DATABASE DESIGN

### Database: PostgreSQL (async via asyncpg)

### Table: `legal_documents`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY, default uuid4 |
| source_type | VARCHAR | NOT NULL (statute / case_law / seed) |
| title | VARCHAR | NOT NULL |
| source_url | VARCHAR | NULLABLE |
| source_site | VARCHAR | NULLABLE |
| year | INTEGER | NULLABLE |
| category | VARCHAR | NULLABLE |
| raw_text | TEXT | NOT NULL |
| content_hash | VARCHAR | UNIQUE, NOT NULL (dedup key) |
| created_at | TIMESTAMP | DEFAULT now() |
| updated_at | TIMESTAMP | DEFAULT now(), ON UPDATE now() |

### Table: `sections`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY, default uuid4 |
| document_id | UUID | FOREIGN KEY -> legal_documents.id (CASCADE) |
| act_name | VARCHAR | NULLABLE |
| section_number | VARCHAR | NULLABLE |
| text | TEXT | NOT NULL (chunk content) |
| chunk_index | INTEGER | NOT NULL |
| token_count | INTEGER | NULLABLE |
| faiss_index_id | INTEGER | NULLABLE |

**Unique Constraint:** (document_id, chunk_index)

### Table: `cases`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY, default uuid4 |
| document_id | UUID | FOREIGN KEY -> legal_documents.id (CASCADE) |
| case_name | VARCHAR | NULLABLE |
| court | VARCHAR | NULLABLE |
| year | INTEGER | NULLABLE |
| citations | VARCHAR[] | ARRAY type (SCC, AIR references) |
| text | TEXT | NOT NULL (chunk content) |
| chunk_index | INTEGER | NOT NULL |
| faiss_index_id | INTEGER | NULLABLE |

**Unique Constraint:** (document_id, chunk_index)

### Table: `crawl_runs`

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY, default uuid4 |
| source_site | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL (running / completed / failed) |
| documents_found | INTEGER | DEFAULT 0 |
| documents_new | INTEGER | DEFAULT 0 |
| chunks_created | INTEGER | DEFAULT 0 |
| errors | JSONB | NULLABLE |
| started_at | TIMESTAMP | DEFAULT now() |
| finished_at | TIMESTAMP | NULLABLE |

### ER Relationships
```
legal_documents (1) ----> (N) sections    [ON DELETE CASCADE]
legal_documents (1) ----> (N) cases       [ON DELETE CASCADE]
crawl_runs                [standalone - audit log]
```

---

## 7. API ANALYSIS

### .NET Gateway Endpoints

| Method | Endpoint | Purpose | Rate Limited |
|--------|----------|---------|--------------|
| GET | `/api/lawyers` | Returns 6 lawyer objects | No |
| GET | `/api/analysis` | Returns mock analysis (demo) | No |
| POST | `/api/analysis/submit` | Full AI analysis pipeline | Yes (10/60s) |

### Python AI Engine Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/analyze` | Full RAG + LLM analysis |
| GET | `/health` | System component status |
| POST | `/admin/crawl` | Trigger crawl by source |
| POST | `/admin/ingest-seed` | Ingest 58 seed .txt files |
| POST | `/admin/rebuild-index` | Rebuild FAISS + BM25 |
| GET | `/admin/crawl-history` | Last N crawl runs |
| GET | `/admin/stats` | Total chunk count |
| POST | `/admin/evaluate` | Run retrieval evaluation |
| POST | `/admin/evaluate/compare` | Compare retrieval methods |

### POST `/api/analysis/submit` - Request/Response

**Request:**
```json
{
  "issue": "My landlord is refusing to return my security deposit after I vacated the property 3 months ago despite no damage to the premises.",
  "caseType": "Property"
}
```

**Response:**
```json
{
  "issue": "My landlord is refusing to return my security deposit...",
  "caseType": "Property",
  "analysis": {
    "riskScore": 45,
    "settlementProbability": 72,
    "advocatePoints": ["Strong documentary evidence...", "..."],
    "opponentPoints": ["Landlord may claim damages...", "..."],
    "vulnerabilities": ["Lack of written agreement...", "..."],
    "steps": [{"title": "Send Legal Notice", "detail": "..."}],
    "riskFactors": ["Evidence Strength:78", "..."],
    "riskSummary": "Your case has moderate risk due to...",
    "advocateConfidence": 0.75,
    "opponentConfidence": 0.55,
    "riskLabel": "Medium",
    "detailedFactors": [
      {"label": "Evidence Strength", "value": 78, "explanation": "Strong rental agreement..."}
    ],
    "settlementRecommendation": "Negotiate",
    "settlementReasoning": "Given strong evidence but slow jurisdiction...",
    "documents": ["Rent Agreement", "Bank Statements", "Photographs"]
  },
  "cached": false
}
```

---

## 8. MODULE BREAKDOWN

### Frontend Modules

| Module | Responsibility | Interactions |
|--------|---------------|--------------|
| **Pages/Landing** | Marketing page, user acquisition | RouterLink -> Signup/Dashboard |
| **Pages/Signup** | User registration, localStorage | -> Dashboard (redirect) |
| **Pages/Dashboard** | Case input, analysis trigger | AnalysisService -> Analysis page |
| **Pages/Analysis** | Display 4 AI analysis sections | AnalysisApiService -> .NET API |
| **Pages/Consult** | Lawyer directory + chat | Mock data (frontend-only) |
| **Core/Services** | State (signals), HTTP, toasts | Used by all pages |
| **Core/Interceptors** | Base URL prepend, error handling | Wraps all HTTP calls |
| **Shared/Components** | Navbar, HeroInput, Loader, Toast | Reused across pages |

### Backend Modules (.NET)

| Module | Responsibility | Interactions |
|--------|---------------|--------------|
| **Program.cs (Endpoints)** | Request routing, validation, caching | PythonApiClient, ResponseAdapter |
| **PythonApiClient** | HTTP communication with AI engine | Sends POST /analyze with correlation ID |
| **ResponseAdapter** | Maps Python response -> internal format | Used by POST handler |
| **Models/PythonModels** | JSON deserialization contracts | Used by PythonApiClient |
| **Middleware (inline)** | Correlation ID, error handling, rate limit | Wraps all requests |

### AI Engine Modules (Python)

| Module | Responsibility | Interactions |
|--------|---------------|--------------|
| **routers/analysis** | `/analyze` endpoint | RAGService |
| **services/rag_service** | Pipeline orchestrator | All services below |
| **services/gemini_service** | Gemini 2.0 Flash LLM calls | google-genai SDK |
| **services/embedding_service** | FAISS vector index + embeddings | sentence-transformers |
| **services/adversarial_service** | Dual-agent (Advocate + Opponent) | GeminiService + prompts |
| **services/risk_scoring_service** | 5-factor risk computation | GeminiService + formulas |
| **services/prompt_builder*** | LLM prompt templates | Used by RAG/adversarial |
| **retrieval/hybrid_retriever** | FAISS + BM25 + RRF + Reranker | EmbeddingService, BM25, Reranker |
| **retrieval/bm25_service** | BM25Okapi sparse retrieval | rank-bm25 library |
| **retrieval/reranker** | Cross-encoder reranking | sentence-transformers |
| **crawlers/** | Web scraping (IndiaCode, IndianKanoon) | httpx + BeautifulSoup |
| **processing/** | Chunking, cleaning, metadata extraction | tiktoken, bleach |
| **db/** | PostgreSQL ORM + repository | SQLAlchemy async + asyncpg |
| **scheduler/jobs** | Cron jobs (crawl + rebuild) | APScheduler |
| **evaluation/** | Retrieval quality metrics | eval_dataset.json |

---

## 9. PERFORMANCE METRICS (REALISTIC - BASED ON CODE)

| Metric | Estimated Value | Justification |
|--------|----------------|---------------|
| **Landing Page Load (SSR)** | < 1.5 seconds | Prerendered HTML + 88KB JS (gzipped), Express SSR on port 4000 |
| **SPA Route Navigation** | < 300ms | Lazy-loaded chunks (1-25KB), no server round-trip |
| **Cached Analysis Response** | < 50ms | In-memory `IMemoryCache` lookup by SHA256 hash |
| **Full Analysis (Cache Miss)** | 8-25 seconds | 3 parallel Gemini calls (pathway + advocate + opponent) + retrieval |
| **Hybrid Retrieval (FAISS + BM25 + Rerank)** | < 500ms | In-process FAISS L2 search + BM25 on loaded index + cross-encoder top-5 |
| **FAISS-only Search** | < 100ms | In-process L2 flat index, 384-dim vectors |
| **Gemini Single Call** | 3-8 seconds | Gemini 2.0 Flash with JSON mode, temperature 0.3 |
| **Rate Limit Response (429)** | < 10ms | Middleware short-circuits before handler |
| **Validation Error Response** | < 5ms | .NET returns immediately, no downstream call |
| **Angular Build Size (Initial)** | 88KB gzipped | Tree-shaking + lazy loading (324KB raw -> 88KB transfer) |
| **Database Query (get_all_chunks)** | < 200ms | Async connection pool (5+10), indexed UUID lookups |
| **Crawl Single Source** | 2-5 minutes | 3s delay between requests, max 20 acts or 150 case queries |

---

## 10. TEST CASES (DERIVED FROM LOGIC)

### Unit Test Cases

| ID | Feature | Input | Expected Output |
|----|---------|-------|-----------------|
| TC01 | Input Validation - Empty issue | `{ issue: "", caseType: "Civil" }` | 400 ValidationProblem: "Issue is required." |
| TC02 | Input Validation - Short issue | `{ issue: "short", caseType: "Civil" }` | 400 ValidationProblem: "Issue must be at least 10 characters." |
| TC03 | Input Validation - Invalid case type | `{ issue: "valid issue text here", caseType: "InvalidType" }` | 400 ValidationProblem: "CaseType must be one of: Civil, Criminal..." |
| TC04 | HTML Sanitization | `{ issue: "<script>alert('xss')</script>My landlord refuses deposit return" }` | Issue sanitized to "My landlord refuses deposit return", processed normally |
| TC05 | Cache Hit | Same issue+caseType submitted twice within 30 min | Second response has `"cached": true`, identical analysis |
| TC06 | Risk Score Clamping | Python returns `risk_score: 150` | .NET clamps to 100 via `Math.Clamp(value, 0, 100)` |
| TC07 | Case Type Case-Insensitivity | `{ issue: "valid text...", caseType: "CRIMINAL" }` | Accepted (HashSet with OrdinalIgnoreCase) |
| TC08 | Python Engine Timeout | Python unreachable (60s timeout) | .NET returns mock fallback data (riskScore: 72) |

### Integration Test Cases

| ID | Modules | Scenario | Expected |
|----|---------|----------|----------|
| IT01 | Angular -> .NET -> Python | Submit valid case, verify all 4 sections populated | Response contains non-null pathway, risk, adversarial; riskScore 0-100 |
| IT02 | .NET Rate Limiter | Send 11 requests in 60 seconds | First 10 succeed (200), 11th returns 429 with "Too many requests" toast |
| IT03 | Correlation ID Propagation | Submit request, check all layer logs | Same `X-Correlation-Id` value in .NET console, Python console, and response header |
| IT04 | Hybrid Retrieval | Query "landlord security deposit" | Returns chunks containing "Transfer of Property Act" or "Rent Control" with scores |
| IT05 | Crawler -> Index Rebuild | POST `/admin/crawl` then `/admin/rebuild-index` | FAISS index size increases, `/health` reports new count |

---

## 11. SECURITY FEATURES (FROM CODEBASE)

| Feature | Implementation | Layer |
|---------|---------------|-------|
| **Input Length Validation** | `[MinLength(10)]`, `[MaxLength(5000)]` on Issue | .NET + Python |
| **Allowlist Validation** | 10 permitted case types, case-insensitive check | .NET + Python |
| **HTML Tag Stripping** | Regex `<[^>]*>` replacement on all user input | .NET + Python |
| **Whitespace Normalization** | Collapse `\s+` to single space | .NET + Python |
| **Rate Limiting** | Fixed window: 10 requests per 60s per client | .NET |
| **CORS Restriction** | Only `localhost:4200` and `localhost:4000` allowed | .NET + Python |
| **Correlation ID Tracing** | 12-char GUID propagated across all layers | .NET + Python |
| **Global Error Handler** | Catches unhandled exceptions, hides stack traces | .NET |
| **Structured Logging** | JSON format with timestamps, scopes, correlation IDs | .NET + Python |
| **Timeout Protection** | 60-second HTTP client timeout to Python engine | .NET |
| **Graceful Degradation** | Falls back to mock data on AI engine failure | .NET |
| **Retry with Backoff** | 3 retries (1s, 2s, 4s) for Gemini 429/503 | Python |
| **Crawler Politeness** | 3s delay between requests, respects rate limits | Python |

**Not Found in Codebase:** Authentication (JWT/OAuth), Authorization (roles), Encryption (TLS certificates), Token management

---

## 12. TECHNOLOGY STACK (STRICT)

### Languages
| Language | Version | Usage |
|----------|---------|-------|
| TypeScript | 5.9.2 | Angular frontend |
| C# | 12 (implicit) | .NET 8 backend |
| Python | 3.11+ | AI engine |
| HTML/CSS | - | Templates + Tailwind |

### Frameworks
| Framework | Version | Layer |
|-----------|---------|-------|
| Angular | 21.2 | Frontend SPA + SSR |
| ASP.NET Core | 8.0 | API Gateway (Minimal APIs) |
| FastAPI | 0.115.0 | AI Engine REST API |
| Express | 5.1.0 | Angular SSR server |
| Tailwind CSS | 4.1.12 | Styling (utility-first) |

### Key Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| google-genai | 1.14.0 | Gemini 2.0 Flash LLM |
| sentence-transformers | 3.4.1 | Embedding model (MiniLM-L6-v2) |
| faiss-cpu | 1.9.0 | Vector similarity search |
| rank-bm25 | 0.2.2 | BM25 sparse retrieval |
| SQLAlchemy | 2.0.36 | Async ORM for PostgreSQL |
| asyncpg | 0.30.0 | PostgreSQL async driver |
| httpx | 0.28.0 | Async HTTP client (crawlers) |
| beautifulsoup4 | 4.12.3 | HTML parsing (crawlers) |
| tiktoken | 0.8.0 | Token counting (chunking) |
| bleach | 6.2.0 | HTML sanitization |
| apscheduler | 3.10.4 | Scheduled jobs (cron) |
| alembic | 1.14.0 | Database migrations |
| lucide-angular | 1.0.0 | Icon system (24+ icons) |
| @angular/cdk | 21.2.9 | Overlay/Dialog primitives |
| rxjs | 7.8.0 | Observable streams |
| Swashbuckle | 6.6.2 | Swagger/OpenAPI |

### Tools
| Tool | Purpose |
|------|---------|
| Angular CLI | Build, serve, generate |
| dotnet CLI | Build, run .NET |
| uvicorn | ASGI server for FastAPI |
| Alembic | Database migration tool |
| Vitest | Frontend unit test runner |
| PostCSS | CSS processing pipeline |
| Prettier | Code formatting |

---

## 13. UNIQUE FEATURES / INNOVATION

### 1. Dual-Agent Adversarial Reasoning
The system runs two independent Gemini LLM calls in parallel - one acting as the user's **Advocate** (building the strongest case FOR) and one as the **Opponent** (finding every weakness AGAINST). The confidence ratio between agents directly feeds into risk scoring. This adversarial pattern is novel in legal AI systems, providing balanced analysis rather than one-sided advice.

### 2. Hybrid 4-Stage Retrieval Pipeline
Unlike single-method RAG systems, this implements:
- Stage 1: Dense retrieval (FAISS, semantic similarity)
- Stage 2: Sparse retrieval (BM25, keyword matching)
- Stage 3: Reciprocal Rank Fusion (combines both ranked lists)
- Stage 4: Cross-encoder reranking (precision filtering)

This ensures both semantic relevance AND keyword precision in legal document retrieval.

### 3. Deterministic Risk Scoring with AI Explanation
Risk scores are computed deterministically in Python using weighted factors:
- Evidence Strength: 25%
- Precedent Alignment: 25%
- Financial Exposure: 20%
- Case Complexity: 15%
- Jurisdiction History: 15%

Gemini provides the factor analysis and explanations, but the final score is a deterministic formula. This ensures reproducibility while maintaining explainability.

### 4. XAI (Explainable AI) Layer
Every risk factor displays an AI-generated explanation. The overall risk summary is generated by Gemini, not hardcoded. Settlement recommendations include reasoning. The system does not just give a number - it explains **why** through:
- Per-factor explanations displayed below progress bars
- Risk summary paragraph dynamically generated
- Settlement reasoning text explaining the recommendation

### 5. Graceful Degradation Architecture
The system has a 3-level fallback hierarchy:
- Level 1: Full AI response (all sections populated by Gemini + retrieval)
- Level 2: Partial response (if one Gemini call fails, others still return)
- Level 3: Mock fallback (if entire Python engine is unreachable, .NET returns reasonable defaults)

This ensures the user always receives something useful regardless of AI engine state.

### 6. Self-Maintaining Knowledge Base
The system automatically crawls 20 Indian statutes (India Code) and 30 case law search queries (Indian Kanoon) on a weekly schedule, deduplicates by content hash, chunks into 512-token segments, and rebuilds both FAISS and BM25 indexes without manual intervention.

### 7. Correlation ID Distributed Tracing
A 12-character correlation ID propagates from Angular -> .NET -> Python, appearing in all structured JSON log entries and response headers. This enables end-to-end request debugging across all three service layers without centralized tracing infrastructure like Jaeger or Zipkin.

---

*Report generated from codebase analysis - all claims backed by actual source code files.*
