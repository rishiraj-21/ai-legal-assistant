# Product Requirements Document (PRD)
# AI-Based Legal Assistant for Personalized Legal Decision Support

**Version:** 1.1
**Last Updated:** 2026-05-02
**Status:** In Development

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Problem Statement](#2-problem-statement)
3. [System Vision](#3-system-vision)
4. [Core Features](#4-core-features)
5. [System Architecture](#5-system-architecture)
6. [Data Flow](#6-data-flow)
7. [AI Pipeline Design](#7-ai-pipeline-design)
8. [RAG Implementation Plan](#8-rag-implementation-plan)
9. [Knowledge Base Design](#9-knowledge-base-design)
10. [Backend API Design](#10-backend-api-design)
11. [Database Schema](#11-database-schema)
12. [Frontend Integration Plan](#12-frontend-integration-plan)
13. [Phase-wise Development Plan](#13-phase-wise-development-plan)
14. [Tech Stack Justification](#14-tech-stack-justification)
15. [Deployment Plan](#15-deployment-plan)
16. [Risks & Mitigation](#16-risks--mitigation)

---

## 1. Product Overview

An AI-powered legal decision support system built for Indian citizens navigating the legal system. The platform uses a **Hybrid Legal AI Framework** combining rule-based reasoning, knowledge graphs, case-based reasoning, and RAG-powered LLM generation to provide personalized, explainable, and jurisdiction-aware legal guidance.

**What this is NOT:**
- A generic legal chatbot
- A static FAQ system
- A document template generator

**What this IS:**
- A dual-agent adversarial reasoning system
- A dynamic legal pathway generator
- A quantitative risk scoring engine
- A RAG-powered, citation-backed legal analysis platform

---

## 2. Problem Statement

Indian citizens face significant barriers to legal understanding:

- **130 crore+ population** with limited access to affordable legal counsel
- Legal language is complex, jurisdiction-specific, and procedurally dense
- Existing legal tools provide static, generic answers without case-specific analysis
- No tool performs adversarial analysis (what the other side will argue)
- Risk assessment is subjective and inconsistent

**Gap:** No existing system combines adversarial reasoning, dynamic risk scoring, RAG-backed citations, and jurisdiction-aware pathway generation in a single platform.

---

## 3. System Vision

```
User describes legal issue
        ↓
NLP extracts entities, jurisdiction, case type
        ↓
RAG retrieves relevant laws, precedents, sections
        ↓
Dual-Agent System generates adversarial analysis
        ↓
Risk Engine computes quantitative score
        ↓
Pathway Generator creates step-by-step legal roadmap
        ↓
XAI layer explains every recommendation with citations
        ↓
Frontend renders dynamic, personalized results
```

The system delivers **four dynamic outputs** for every query:
1. **Legal Pathway** — step-by-step procedure with jurisdiction-specific details
2. **Risk Score** — 0–100 quantitative assessment with factor breakdown
3. **Adversarial Analysis** — Advocate AI vs Opponent AI arguments
4. **Settlement Strategy** — negotiation position and probability assessment

---

## 4. Core Features

### 4.1 RAG-Powered Legal Intelligence
- Custom legal knowledge base with Indian laws, case precedents, IPC/BNS sections
- Vector similarity search for contextually relevant retrieval
- Every answer backed by specific citations (Act, Section, Case)

### 4.2 Dual-Agent Adversarial System
- **Advocate AI**: Builds the strongest case FOR the user
- **Opponent AI**: Builds the strongest case AGAINST the user
- Output: Strength points, weaknesses, vulnerabilities, confidence scores

### 4.3 Dynamic Risk Scoring Engine
- Score: 0–100 computed from weighted factors
- Factors: Evidence strength, legal precedent alignment, financial exposure, case complexity, jurisdiction history
- Output: Score + Label (Low/Medium/High/Critical) + factor breakdown

### 4.4 Dynamic Legal Pathway Generation
- Jurisdiction-aware step-by-step legal procedure
- Court hierarchy mapping (District → High Court → Supreme Court)
- Timeline estimates and document requirements per step

### 4.5 Settlement Strategy Engine
- Settlement probability calculation
- Optimal negotiation position analysis
- BATNA (Best Alternative to Negotiated Agreement) assessment

### 4.6 Explainable AI (XAI)
- Every recommendation includes: why, which law, which precedent, confidence level
- Transparency layer showing reasoning chain

### 4.7 Geo-Aware Jurisdiction System
- Indian state/territory detection
- Court hierarchy mapping per jurisdiction
- State-specific procedural variations

### 4.8 Lawyer Consultation (Future)
- Directory with specialization matching
- Chat and video consultation (WebRTC)

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Angular 21)                        │
│  Landing │ Dashboard │ Analysis (4 sections) │ Consult │ Signup     │
│  ───────────────────────────────────────────────────────────────     │
│  Components: HeroInput, LegalPathway, RiskScore, Adversarial,      │
│              Negotiation, LawyerDirectory, Chat                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP / REST
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   API GATEWAY (ASP.NET Core 8)                      │
│                                                                     │
│  /api/analysis/submit    → Orchestrates full analysis pipeline      │
│  /api/analysis/{id}      → Fetch cached analysis result             │
│  /api/lawyers            → Lawyer directory                         │
│  /api/auth/*             → Authentication endpoints                 │
│                                                                     │
│  Services: RequestValidation, AuthService, CacheService,            │
│            PipelineOrchestrator, **ResponseAdapterLayer**           │
│            (calls Python AI layer via HTTP, normalizes response)    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP (internal)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   AI ENGINE (Python / FastAPI)                       │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  NLP Module   │  │  RAG Engine   │  │  Gemini Integration     │  │
│  │  - Entity     │  │  - Query      │  │  - Prompt construction  │  │
│  │    extraction │  │    embedding  │  │  - Response parsing     │  │
│  │  - Case type  │  │  - Vector     │  │  - Multi-turn context   │  │
│  │    detection  │  │    search     │  │                         │  │
│  │  - Jurisdiction│  │  - Re-ranking │  │                         │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬──────────────┘  │
│         │                 │                       │                  │
│         ▼                 ▼                       ▼                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   REASONING ENGINE                           │    │
│  │                                                             │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │    │
│  │  │ Advocate AI  │  │ Opponent AI  │  │ Risk Scoring      │  │    │
│  │  │ (Pro-user)   │  │ (Anti-user)  │  │ Engine            │  │    │
│  │  └─────────────┘  └──────────────┘  └───────────────────┘  │    │
│  │                                                             │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │    │
│  │  │ Pathway     │  │ Settlement   │  │ XAI Layer         │  │    │
│  │  │ Generator   │  │ Analyzer     │  │ (Explainability)  │  │    │
│  │  └─────────────┘  └──────────────┘  └───────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                   │
│                                                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────────┐  │
│  │ Vector DB      │  │ SQL Database   │  │ Knowledge Graph      │  │
│  │ (FAISS/        │  │ (PostgreSQL)   │  │ (Neo4j/in-memory)    │  │
│  │  ChromaDB)     │  │                │  │                      │  │
│  │ - Embeddings   │  │ - Users        │  │ - Act → Section      │  │
│  │ - Legal docs   │  │ - Sessions     │  │ - Section → Cases    │  │
│  │ - Case chunks  │  │ - Analysis     │  │ - Court hierarchy    │  │
│  │                │  │   results      │  │ - Jurisdiction map   │  │
│  └────────────────┘  └────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Data Flow

### 6.1 Analysis Request Flow (End-to-End)

```
Step 1: User types legal issue in Dashboard HeroInput
        → POST /api/analysis/submit { issue, caseType }

Step 2: ASP.NET validates request, creates session
        → Forwards to Python AI Engine: POST /ai/analyze

Step 3: NLP Module processes input
        → Extracts: entities, jurisdiction, case type, key terms
        → Output: StructuredQuery object

Step 4: RAG Engine retrieves context
        → Embeds query using sentence-transformers
        → Searches vector DB for top-K relevant chunks
        → Re-ranks by relevance score
        → Output: RelevantContext[] with citations

Step 5: Advocate AI generates pro-user arguments
        → Prompt: system context + retrieved laws + user case
        → Gemini API call with advocate persona
        → Output: strength points, supporting precedents

Step 6: Opponent AI generates counter-arguments
        → Prompt: system context + retrieved laws + user case
        → Gemini API call with opponent persona
        → Output: weaknesses, vulnerabilities, counter-precedents

Step 7: Risk Scoring Engine computes score
        → Inputs: NLP output, RAG context, advocate/opponent analysis
        → Weighted formula across 5 factors
        → Output: score (0–100), label, factor breakdown

Step 8: Pathway Generator creates legal roadmap
        → Inputs: case type, jurisdiction, risk level
        → Rule-based step selection + Gemini enrichment
        → Output: ordered steps with details

Step 9: Settlement Analyzer computes strategy
        → Inputs: risk score, advocate/opponent balance, case type
        → Output: settlement probability, recommendation

Step 10: XAI Layer attaches explanations
         → Each output gets: reasoning, citations, confidence

Step 11: Response Adapter Layer normalizes AI output
         → Validates all required fields exist
         → Fills missing sections with partial-response fallbacks
         → Maps AI output to frontend-expected JSON contract
         → Ensures type safety and default values

Step 12: Response returned to frontend
         → ASP.NET → Angular frontend
         → Frontend renders into existing UI sections
         → Partial results shown immediately (e.g., pathway ready, adversarial still loading)
```

### 6.2 Response Structure

```json
{
  "analysisId": "uuid",
  "timestamp": "ISO-8601",
  "legalPathway": {
    "steps": [
      {
        "order": 1,
        "title": "Send Legal Notice",
        "detail": "Under Section 80 CPC...",
        "estimatedDuration": "15-30 days",
        "documents": ["Notice draft", "Proof of delivery"],
        "citation": "Section 80, Code of Civil Procedure, 1908"
      }
    ],
    "jurisdiction": "Delhi High Court",
    "estimatedTotalDuration": "12-18 months"
  },
  "riskScore": {
    "overall": 72,
    "label": "High",
    "factors": [
      { "label": "Evidence Strength", "value": 65 },
      { "label": "Legal Precedent", "value": 78 },
      { "label": "Financial Exposure", "value": 80 },
      { "label": "Case Complexity", "value": 70 },
      { "label": "Jurisdiction History", "value": 68 }
    ],
    "explanation": "High risk due to significant financial exposure..."
  },
  "adversarial": {
    "advocate": {
      "points": ["...", "..."],
      "confidence": 0.74,
      "keyPrecedents": ["Case A v. Case B (2019)"]
    },
    "opponent": {
      "points": ["...", "..."],
      "confidence": 0.61,
      "keyPrecedents": ["Case C v. Case D (2021)"]
    },
    "vulnerabilities": ["...", "..."]
  },
  "settlement": {
    "probability": 68,
    "recommendation": "Negotiate",
    "optimalRange": { "min": 500000, "max": 750000 },
    "reasoning": "Based on precedent and risk factors..."
  },
  "xai": {
    "lawsUsed": ["Section 73, Indian Contract Act", "..."],
    "precedentsUsed": ["Case name, Year, Court"],
    "confidenceOverall": 0.72,
    "reasoningChain": ["Step 1: ...", "Step 2: ..."]
  }
}
```

---

## 7. AI Pipeline Design

### 7.1 NLP Module

**Purpose:** Extract structured information from free-text legal queries.

| Component | Method | Output |
|-----------|--------|--------|
| Entity Extraction | spaCy + custom NER model | Parties, dates, amounts, locations |
| Case Type Detection | Text classification (fine-tuned or rule-based) | Civil, Criminal, Family, Property, Consumer, Corporate, IP |
| Jurisdiction Detection | Keyword + geo extraction | State, court level |
| Key Term Extraction | TF-IDF + legal vocabulary | Relevant legal terms |

### 7.2 RAG Engine

```
Query → Embedding Model (sentence-transformers/all-MiniLM-L6-v2)
     → Vector Search (FAISS, top-20)
     → Re-ranking (cross-encoder/ms-marco-MiniLM-L-6-v2)
     → Top-5 chunks with metadata (Act, Section, Court, Year)
```

### 7.3 Gemini Integration

**Model:** `gemini-2.0-flash` (free tier, high throughput)

**Prompt Architecture:**

```
SYSTEM: You are a legal analysis AI specializing in Indian law.
You must ONLY use the provided legal context for your analysis.
Every claim must cite specific Act, Section, or Case.

CONTEXT: {retrieved_chunks_with_citations}

USER CASE: {structured_query}

TASK: {specific_task_prompt}
```

**Separate prompts for each agent:**
- Advocate prompt: "Build the strongest legal argument supporting this case..."
- Opponent prompt: "Identify every weakness and build counter-arguments..."
- Pathway prompt: "Generate step-by-step legal procedure for this jurisdiction..."
- Settlement prompt: "Analyze settlement viability given these factors..."

### 7.4 Risk Scoring Formula

```
RiskScore = (w1 × EvidenceStrength) + (w2 × PrecedentAlignment) +
            (w3 × FinancialExposure) + (w4 × CaseComplexity) +
            (w5 × JurisdictionHistory)

Default weights: w1=0.25, w2=0.25, w3=0.20, w4=0.15, w5=0.15

Each factor scored 0–100 by Gemini with structured output parsing.

Labels:
  0–25:  Low Risk
  26–50: Medium Risk
  51–75: High Risk
  76–100: Critical Risk
```

---

## 8. RAG Implementation Plan

### 8.1 Document Sources

| Source | Type | URL Pattern | Priority |
|--------|------|-------------|----------|
| India Code | Acts & Sections | indiacode.nic.in | P0 |
| Indian Kanoon | Case Law | indiankanoon.org | P0 |
| Bare Acts | Statutes | bareactslive.com | P1 |
| SCC Online | Judgments | scc-online summaries | P1 |
| Legal Services Authority | Procedures | nalsa.gov.in | P2 |
| E-Courts | Court data | ecourts.gov.in | P2 |

### 8.2 Ingestion Pipeline

```
Source → Crawler (Scrapy/BeautifulSoup)
     → Raw Storage (filesystem / S3)
     → Cleaner (remove HTML, headers, footers)
     → Chunker (recursive text splitter, 512 tokens, 50 overlap)
     → Metadata Extractor (Act name, Section no., Court, Year, Jurisdiction)
     → Embedding (sentence-transformers)
     → Vector DB (FAISS index + metadata store)
```

### 8.3 Chunking Strategy

- **Acts/Sections:** One chunk per section with metadata (Act name, section number)
- **Case Laws:** Split into facts, arguments, judgment, ratio decidendi
- **Procedures:** One chunk per procedural step

### 8.4 Retrieval Strategy

1. **Dense retrieval:** Embedding similarity (FAISS)
2. **Sparse retrieval:** BM25 keyword match (as fallback)
3. **Hybrid:** Reciprocal Rank Fusion (RRF) to combine both
4. **Re-ranking:** Cross-encoder for final top-5 selection

---

## 9. Knowledge Base Design

### 9.1 Components

```
Knowledge Base
├── Raw Document Store
│   ├── /acts/           → Full text of Indian Acts
│   ├── /cases/          → Case law documents
│   ├── /procedures/     → Court procedures by jurisdiction
│   └── /metadata/       → Source tracking, crawl dates
│
├── Vector Store (FAISS)
│   ├── legal_acts.index       → Embeddings for acts/sections
│   ├── case_law.index         → Embeddings for case law
│   └── procedures.index       → Embeddings for procedures
│
├── Structured Store (PostgreSQL)
│   ├── acts                   → Act name, year, category
│   ├── sections               → Section text, act_id, keywords
│   ├── cases                  → Case name, court, year, outcome
│   └── jurisdictions          → State, court hierarchy, procedures
│
└── Knowledge Graph (Neo4j / in-memory)
    ├── (Act)-[:CONTAINS]->(Section)
    ├── (Section)-[:CITED_IN]->(Case)
    ├── (Case)-[:DECIDED_BY]->(Court)
    ├── (Court)-[:PART_OF]->(Jurisdiction)
    └── (Section)-[:AMENDED_BY]->(Amendment)
```

### 9.2 Update Pipeline

| Task | Frequency | Method |
|------|-----------|--------|
| New case law crawl | Weekly | Scheduled Scrapy job |
| Act amendments | Monthly | Manual review + crawler |
| Vector index rebuild | Weekly | Batch re-embedding |
| Knowledge graph update | Monthly | Delta updates |
| Data quality audit | Monthly | Automated + manual spot check |

---

## 10. Backend API Design

### 10.1 ASP.NET Core Endpoints (API Gateway)

```
POST   /api/analysis/submit
       Body: { issue: string, caseType: string, jurisdiction?: string }
       Response: { analysisId: string, status: "processing" }
       → Initiates async analysis pipeline

GET    /api/analysis/{id}
       Response: Full AnalysisResult (see Section 6.2)
       → Returns completed or partial analysis

GET    /api/analysis/{id}/status
       Response: { status: "processing" | "completed" | "failed", progress: number }
       → Polling endpoint for analysis status

GET    /api/lawyers
       Query: ?specialization=&jurisdiction=
       Response: Lawyer[]

POST   /api/auth/signup
       Body: { email, password, name }

POST   /api/auth/login
       Body: { email, password }
       Response: { token, user }

GET    /api/jurisdictions
       Response: Jurisdiction[] (states, court hierarchy)
```

### 10.2 Python AI Engine Endpoints (Internal)

```
POST   /ai/analyze
       Body: { issue, caseType, jurisdiction }
       Response: Full analysis pipeline result

POST   /ai/extract-entities
       Body: { text }
       Response: { entities, caseType, jurisdiction }

POST   /ai/search
       Body: { query, filters }
       Response: { chunks[], scores[] }

GET    /ai/health
       Response: { status, vectorDbLoaded, geminiConnected }
```

### 10.3 Communication Pattern

```
Angular → ASP.NET (REST, JSON)
ASP.NET → Python (internal HTTP, JSON)
Python  → Gemini (Google AI SDK)
Python  → FAISS (in-process)
ASP.NET → PostgreSQL (EF Core)
```

### 10.4 Response Adapter Layer (CRITICAL)

**Purpose:** Prevent UI breakage by normalizing raw AI output into a stable, frontend-safe JSON contract.

**Problem without it:**
```
Gemini returns inconsistent keys, missing fields, or unexpected types
→ Raw JSON forwarded to Angular
→ UI crashes or shows blank sections
```

**Solution:**
```
Python AI Engine returns raw result
    ↓
ASP.NET ResponseAdapter service:
    1. Schema validation   → Checks all required fields exist
    2. Type coercion       → Ensures score is int, points are string[]
    3. Default filling     → Missing sections get safe defaults
    4. Partial response    → Marks sections as "available" or "unavailable"
    5. Contract mapping    → Maps to exact frontend interface shape
    ↓
Frontend receives stable, typed JSON every time
```

**Partial Response Strategy:**
Each section in the response includes an `available` flag:
```json
{
  "legalPathway": { "available": true, "steps": [...] },
  "riskScore":    { "available": true, "overall": 72, ... },
  "adversarial":  { "available": false, "error": "Gemini timeout", "fallbackMessage": "Adversarial analysis is temporarily unavailable. Your other results are ready." },
  "settlement":   { "available": true, "probability": 68, ... }
}
```

**Rules:**
- Frontend NEVER receives raw AI output — always adapter-processed
- If a section fails, other sections still return successfully
- Every field has a defined default value (empty array, 0, "N/A")
- Response shape MUST match `analysis.model.ts` interfaces exactly

---

## 11. Database Schema

### 11.1 PostgreSQL (ASP.NET managed)

```sql
-- Users & Auth
CREATE TABLE users (
    id              UUID PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    name            VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Analysis Sessions
CREATE TABLE analyses (
    id              UUID PRIMARY KEY,
    user_id         UUID REFERENCES users(id),
    issue_text      TEXT NOT NULL,
    case_type       VARCHAR(50),
    jurisdiction    VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'processing',
    result_json     JSONB,
    created_at      TIMESTAMP DEFAULT NOW(),
    completed_at    TIMESTAMP
);

-- Lawyer Directory
CREATE TABLE lawyers (
    id              UUID PRIMARY KEY,
    name            VARCHAR(100),
    specialization  VARCHAR(100),
    rating          DECIMAL(2,1),
    reviews         INT,
    chat_rate       INT,
    video_rate      INT,
    experience_yrs  INT,
    is_online       BOOLEAN,
    initials        VARCHAR(5),
    languages       VARCHAR(100),
    jurisdiction    VARCHAR(100)
);

-- Knowledge Base Metadata
CREATE TABLE legal_documents (
    id              UUID PRIMARY KEY,
    source_type     VARCHAR(20),  -- 'act', 'case', 'procedure'
    title           VARCHAR(500),
    source_url      VARCHAR(1000),
    jurisdiction    VARCHAR(100),
    year            INT,
    crawled_at      TIMESTAMP,
    chunk_count     INT
);
```

### 11.2 FAISS Vector Store

```
Index: legal_knowledge
  - Dimension: 384 (all-MiniLM-L6-v2)
  - Metric: L2 / Inner Product
  - Metadata sidecar (JSON): doc_id, source_type, act_name, section_no, court, year
```

---

## 12. Frontend Integration Plan

### 12.1 Rule: Frontend is a LOCKED UI Layer

The Angular frontend is **fully built** with premium UI/UX. No visual changes are permitted.

**Allowed modifications ONLY:**
- Replace hardcoded/mock data with API responses
- Add/modify Angular services for HTTP calls
- Update signal-based state management to consume API data
- Add loading states to existing component structure

### 12.2 Current State → Target State

| Component | Current (Hardcoded) | Target (Dynamic) |
|-----------|-------------------|------------------|
| Dashboard HeroInput | Navigates to `/analysis` with static state | POST to `/api/analysis/submit`, navigate with `analysisId` |
| Legal Pathway section | `mock-data.ts` steps | Render from `response.legalPathway.steps` |
| Risk Score section | `mock-data.ts` score/factors | Render from `response.riskScore` |
| Adversarial section | `mock-data.ts` advocate/opponent | Render from `response.adversarial` |
| Settlement section | `mock-data.ts` probability | Render from `response.settlement` |
| Lawyer directory | Backend returns static array | Backend returns DB-backed lawyers with filtering |

### 12.3 Service Changes

**`analysis.service.ts`** — Expand to:
```typescript
// Add HTTP methods
submitAnalysis(issue: string, caseType: string): Observable<{ analysisId: string }>
getAnalysis(id: string): Observable<AnalysisResult>
pollStatus(id: string): Observable<AnalysisStatus>

// Add signal for full result
readonly result = signal<AnalysisResult | null>(null);
readonly loading = signal<boolean>(false);
```

**`analysis.model.ts`** — Expand interfaces to match API response (Section 6.2)

**New: `api.service.ts`** — Base HTTP service with error handling, auth headers

### 12.4 Data Binding Updates

Each analysis section component will:
1. Inject `AnalysisService`
2. Read from `result()` signal (computed/derived signals for each section)
3. Show loading skeleton while `loading()` is true
4. Display actual data when `result()` populates

---

## 13. Phase-wise Development Plan

---

### PHASE 1: Foundation — Basic Backend + Gemini Integration + Simple RAG
**Duration:** 3–4 weeks
**Status:** `NOT STARTED`

#### Goals
- Stand up Python AI engine alongside existing ASP.NET backend
- Integrate Gemini API for text generation
- Build minimal RAG with a small seed dataset
- Build Response Adapter Layer in ASP.NET
- Replace **two** frontend sections (Legal Pathway + Risk Score) with dynamic data to validate the full structure early
- Implement Gemini retry logic and partial-response fallback from Day 1

#### Tasks

| # | Task | Details |
|---|------|---------|
| 1.1 | Set up Python FastAPI project | Project structure, virtual env, Docker setup |
| 1.2 | Gemini API integration | Google AI SDK, prompt templates, response parsing, error handling, rate limiting |
| 1.3 | Gemini retry + fallback | Exponential backoff (3 attempts), partial response support — if pathway succeeds but risk fails, still return pathway |
| 1.4 | Seed legal dataset | Manually curate 50–100 key Indian legal sections (IPC, CPC, Contract Act, Consumer Protection Act) as text files |
| 1.5 | Basic embedding pipeline | sentence-transformers, chunk seed data, build FAISS index |
| 1.6 | Simple RAG endpoint | `/ai/analyze` → embed query → search FAISS → inject context → Gemini → structured response (pathway + risk) |
| 1.7 | Response Adapter Layer | ASP.NET service that validates, normalizes, and fills defaults for AI responses before sending to frontend |
| 1.8 | ASP.NET proxy endpoint | `POST /api/analysis/submit` → Python AI → Response Adapter → frontend-safe JSON |
| 1.9 | Frontend: Connect Legal Pathway | Update `AnalysisService` to call real API, render dynamic steps in Legal Pathway section |
| 1.10 | Frontend: Connect Risk Score | Render dynamic risk score (overall + factors) from API — validates the scoring pipeline early |
| 1.11 | Basic error handling | Timeout handling, Gemini quota errors, partial response UI (show what's available) |

#### Deliverables
- [ ] Python FastAPI running on port 8000
- [ ] Gemini generating legal pathway + risk score from user query + RAG context
- [ ] Response Adapter normalizing AI output to stable frontend contract
- [ ] Legal Pathway section showing dynamic AI-generated steps
- [ ] Risk Score section showing dynamic AI-generated score + factors
- [ ] Gemini retry logic with exponential backoff working
- [ ] Partial response: if risk fails, pathway still renders (and vice versa)
- [ ] End-to-end flow validated across 2 sections: User input → API → AI → Adapter → Dynamic UI

---

### PHASE 2: Knowledge Base — Crawler + Vector DB + Structured Storage
**Duration:** 3–4 weeks
**Status:** `NOT STARTED`

#### Goals
- Build automated legal data crawling pipeline
- Scale vector DB from seed data to thousands of legal documents
- Add structured metadata storage (PostgreSQL)
- Improve retrieval quality with hybrid search

#### Tasks

| # | Task | Details |
|---|------|---------|
| 2.1 | India Code crawler | Scrapy spider for indiacode.nic.in — extract acts, sections, text |
| 2.2 | Indian Kanoon crawler | Spider for case law — extract judgment text, court, year, citations |
| 2.3 | Document processing pipeline | HTML cleaning, text extraction, chunking (512 tokens), metadata extraction |
| 2.4 | PostgreSQL setup | `legal_documents` table, `sections` table, `cases` table |
| 2.5 | Scale FAISS index | Re-build index with full crawled dataset, add metadata sidecar |
| 2.6 | Hybrid retrieval | Add BM25 sparse search, implement RRF fusion with dense search |
| 2.7 | Re-ranking | Cross-encoder re-ranking for top-K results |
| 2.8 | Retrieval quality testing | Build eval set of 50 queries, measure recall@5, precision@5 |
| 2.9 | Update pipeline scheduling | Cron/scheduler for weekly crawls, index rebuilds |

#### Deliverables
- [ ] 10,000+ legal document chunks indexed
- [ ] Automated weekly crawl pipeline
- [ ] Hybrid retrieval (dense + sparse + re-rank)
- [ ] Retrieval recall@5 > 0.7 on eval set

---

### PHASE 3: Adversarial AI System
**Duration:** 2–3 weeks
**Status:** `NOT STARTED`

#### Goals
- Implement dual-agent adversarial reasoning
- Generate Advocate and Opponent arguments dynamically
- Identify vulnerabilities through argument comparison
- Connect to Adversarial section in frontend

#### Tasks

| # | Task | Details |
|---|------|---------|
| 3.1 | Advocate AI agent | Prompt engineering: "You are a senior advocate. Build the strongest case for the user using ONLY the provided legal context..." |
| 3.2 | Opponent AI agent | Prompt engineering: "You are opposing counsel. Find every weakness, counter-argument, and vulnerability..." |
| 3.3 | Vulnerability extraction | Compare advocate vs opponent outputs, identify gaps and contradictions |
| 3.4 | Confidence scoring | Score each argument based on citation strength, precedent recency, jurisdiction relevance |
| 3.5 | Structured output parsing | Force Gemini to return JSON with points[], confidence, precedents[] |
| 3.6 | Concurrent execution | Run Advocate and Opponent prompts in parallel (asyncio) |
| 3.7 | Frontend: Connect Adversarial section | Render advocate points, opponent points, vulnerabilities from API |
| 3.8 | Prompt iteration | Test with 20+ real legal scenarios, refine prompts for quality |

#### Deliverables
- [ ] Dual-agent system producing distinct, citation-backed arguments
- [ ] Vulnerability analysis identifying case weaknesses
- [ ] Adversarial section rendering dynamic AI output
- [ ] Average response time < 15 seconds for full adversarial analysis

---

### PHASE 4: Advanced Risk Scoring + Settlement Engine
**Duration:** 2–3 weeks
**Status:** `NOT STARTED`

#### Goals
- Upgrade basic risk scoring (from Phase 1) to multi-factor weighted engine
- Build dedicated prompts for each risk factor (not single-prompt extraction)
- Add settlement probability engine
- Calibrate against known case outcomes

#### Tasks

| # | Task | Details |
|---|------|---------|
| 4.1 | Risk factor extraction prompts | Separate Gemini prompts for each factor: evidence strength, precedent alignment, financial exposure, case complexity, jurisdiction history |
| 4.2 | Scoring normalization | Ensure each factor outputs 0–100, handle edge cases |
| 4.3 | Weighted aggregation | Implement formula: `Σ(wi × fi)` with configurable weights |
| 4.4 | Risk label assignment | Threshold-based labeling (Low/Medium/High/Critical) |
| 4.5 | Explanation generation | Gemini prompt to explain overall risk in 2–3 sentences with citations |
| 4.6 | Settlement probability | Derive from risk score + adversarial balance: `settlement_prob = f(risk, advocate_confidence, opponent_confidence)` |
| 4.7 | Frontend: Connect Risk Score section | Render score, factors, gauge visualization from API |
| 4.8 | Frontend: Connect Settlement section | Render probability, recommendation from API |
| 4.9 | Calibration | Test against 30+ known case outcomes, adjust weights |

#### Deliverables
- [ ] Risk score computed dynamically for every query
- [ ] 5-factor breakdown with individual scores
- [ ] Risk Score and Settlement sections rendering dynamic data
- [ ] Score calibration accuracy > 65% on test set

---

### PHASE 5: Full Frontend Integration — Replace All Hardcoded Data
**Duration:** 2 weeks
**Status:** `NOT STARTED`

#### Goals
- Remove ALL mock data from frontend
- Every section powered by dynamic backend
- Add loading states, error states, retry logic
- End-to-end polish

#### Tasks

| # | Task | Details |
|---|------|---------|
| 5.1 | Remove `mock-data.ts` | Delete mock data file, ensure no component references it |
| 5.2 | Expand `AnalysisService` | Full signal-based state: `result`, `loading`, `error`, polling |
| 5.3 | Expand `analysis.model.ts` | Interfaces matching full API response (Section 6.2) |
| 5.4 | Create `ApiService` | Base HTTP service with interceptors: auth, error handling, retry |
| 5.5 | Loading states | Show skeleton/spinner in each section while analysis runs |
| 5.6 | Error states | Show error message with retry button if API fails |
| 5.7 | Analysis polling | Poll `/api/analysis/{id}/status` until complete, then fetch result |
| 5.8 | Lawyer directory | Connect to backend with filtering by specialization |
| 5.9 | XAI display | Show citations, reasoning chain in expandable section within each UI block |
| 5.10 | End-to-end testing | Test 10 different legal scenarios through full pipeline |

#### Deliverables
- [ ] Zero hardcoded data in frontend
- [ ] All 4 analysis sections rendering dynamic AI output
- [ ] Loading, error, and empty states handled gracefully
- [ ] Full pipeline working end-to-end for all supported case types

---

### PHASE 6: Optimization + XAI + Production Readiness
**Duration:** 2–3 weeks
**Status:** `NOT STARTED`

#### Goals
- Optimize response times
- Enhance explainability
- Add caching, rate limiting, monitoring
- Prepare for deployment

#### Tasks

| # | Task | Details |
|---|------|---------|
| 6.1 | Response caching | Cache analysis results in PostgreSQL, serve repeat queries instantly |
| 6.2 | Prompt optimization | Reduce token usage, improve output quality, minimize Gemini calls |
| 6.3 | Parallel pipeline execution | Run Advocate AI, Opponent AI, Risk Scoring concurrently |
| 6.4 | XAI enhancements | Reasoning chain visualization, citation linking, confidence breakdown |
| 6.5 | Rate limiting | Per-user rate limits on analysis endpoint |
| 6.6 | Monitoring & logging | Structured logging, response time tracking, error rate alerts |
| 6.7 | Input validation & sanitization | Prevent prompt injection, validate case types, sanitize user input |
| 6.8 | API documentation | OpenAPI/Swagger docs for all endpoints |
| 6.9 | Performance benchmarks | Target: < 20s total response time, < 5s per individual agent |
| 6.10 | Security audit | Auth flow, data encryption, CORS, input sanitization |

#### Deliverables
- [ ] Average response time < 20 seconds
- [ ] XAI citations displayed for every recommendation
- [ ] Rate limiting and caching operational
- [ ] Production-ready API with documentation

---

## 14. Tech Stack Justification

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Angular 21 + Tailwind v4 | Already built, premium UI, signals for reactive state |
| **API Gateway** | ASP.NET Core 8 | Already scaffolded, strong typing, Swagger, CORS configured |
| **AI Engine** | Python + FastAPI | Ecosystem for ML/NLP (spaCy, sentence-transformers, FAISS), async support |
| **LLM** | Gemini 2.0 Flash | Free tier, fast, good at structured output, sufficient for legal reasoning |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | Free, fast, 384-dim, good semantic similarity |
| **Vector DB** | FAISS (local) → Pinecone (production) | FAISS is free and fast for dev; Pinecone for managed production scale |
| **Database** | PostgreSQL | JSONB for flexible analysis storage, reliable, free |
| **Knowledge Graph** | Neo4j Community (or in-memory graph) | Model legal relationships (Act→Section→Case→Court) |
| **Crawling** | Scrapy + BeautifulSoup | Scrapy for structured crawling, BS4 for ad-hoc parsing |
| **Re-ranking** | cross-encoder/ms-marco-MiniLM | Free, accurate re-ranking for RAG quality |

---

## 15. Deployment Plan

### 15.1 Development Environment

```
Local Machine:
  - Angular dev server    → localhost:4200
  - ASP.NET backend       → localhost:5058
  - Python AI engine      → localhost:8000
  - PostgreSQL            → localhost:5432
  - FAISS                 → in-process (Python)
```

### 15.2 Staging / Production

```
Option A: Single VPS (Budget)
  - Docker Compose with 4 containers:
    1. Angular (Nginx)
    2. ASP.NET Core
    3. Python FastAPI
    4. PostgreSQL
  - Reverse proxy: Nginx / Caddy

Option B: Cloud (Scalable)
  - Frontend: Vercel / Azure Static Web Apps
  - ASP.NET: Azure App Service / Railway
  - Python: Azure App Service / Railway
  - DB: Azure PostgreSQL / Supabase
  - Vector DB: Pinecone (managed)
```

### 15.3 CI/CD

```
GitHub Actions:
  - On push to main:
    1. Lint + test Angular
    2. Build .NET + test
    3. Build Python + test
    4. Docker build + push
    5. Deploy to staging
  - On release tag:
    6. Deploy to production
```

---

## 16. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Gemini API rate limits / quota exhaustion | Pipeline fails | Medium | **Retry:** Exponential backoff (3 attempts, 1s→2s→4s). **Partial fallback:** If adversarial agent fails, still return pathway + risk score. **Cache:** Store successful responses, serve cached results for repeat queries. **Queue:** Rate-limit requests to stay within free-tier quota. |
| Gemini partial failure (1 agent succeeds, 1 fails) | Incomplete analysis | Medium | Response Adapter marks failed sections as `unavailable` with fallback message. Frontend shows available sections immediately. User can retry failed section independently. |
| Legal data accuracy / hallucination | Wrong legal advice | High | RAG-only answers (no pure LLM), citation requirement, confidence thresholds, disclaimer |
| Web scraping blocked by source sites | Knowledge base stale | Medium | Respect robots.txt, rotate user agents, cache aggressively, manual data curation as backup |
| Slow response times (>30s) | Poor UX | Medium | Parallel agent execution, caching, streaming responses, progress indicators |
| Prompt injection via user input | Security breach | Low | Input sanitization, prompt guardrails, output validation |
| Scope creep across phases | Delays | High | Strict phase gates, MVP-first mindset, defer nice-to-haves |
| Legal liability for AI advice | Legal risk | Medium | Clear disclaimers ("not legal advice"), encourage lawyer consultation, never replace professional counsel |
| FAISS index corruption / data loss | Knowledge base down | Low | Regular backups, rebuild scripts, index versioning |

---

## Appendix A: Progress Tracker

| Phase | Description | Status | Completion |
|-------|-------------|--------|------------|
| Phase 1 | Foundation — Backend + Gemini + Simple RAG | `NOT STARTED` | 0% |
| Phase 2 | Knowledge Base — Crawler + Vector DB | `NOT STARTED` | 0% |
| Phase 3 | Adversarial AI System | `NOT STARTED` | 0% |
| Phase 4 | Risk Scoring Engine | `NOT STARTED` | 0% |
| Phase 5 | Full Frontend Integration | `NOT STARTED` | 0% |
| Phase 6 | Optimization + XAI + Production | `NOT STARTED` | 0% |

---

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| **RAG** | Retrieval-Augmented Generation — retrieve relevant documents before generating LLM response |
| **XAI** | Explainable AI — every output includes reasoning and citations |
| **FAISS** | Facebook AI Similarity Search — vector similarity search library |
| **BNS** | Bharatiya Nyaya Sanhita — new Indian penal code (replacing IPC) |
| **BATNA** | Best Alternative to Negotiated Agreement — negotiation strategy concept |
| **RRF** | Reciprocal Rank Fusion — method to combine multiple ranked result lists |
| **NER** | Named Entity Recognition — extracting entities (names, dates, amounts) from text |

---

*This document is the single source of truth for the AI Legal Assistant project. Update the Progress Tracker as phases are completed.*
