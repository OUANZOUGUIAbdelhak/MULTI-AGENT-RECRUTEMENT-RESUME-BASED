# Technical Documentation: Multi-Agent Candidate Selection System

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Multi-Agent System Theory](#multi-agent-system-theory)
4. [RAG (Retrieval Augmented Generation) System](#rag-retrieval-augmented-generation-system)
5. [Agent Architecture & Methodology](#agent-architecture--methodology)
6. [Scoring Algorithms](#scoring-algorithms)
7. [LLM Integration & Fallback Mechanism](#llm-integration--fallback-mechanism)
8. [Vector Database & Embeddings](#vector-database--embeddings)
9. [Frontend Architecture](#frontend-architecture)
10. [Backend API Design](#backend-api-design)
11. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
12. [Technology Stack](#technology-stack)
13. [Evaluation Methodology](#evaluation-methodology)
14. [Performance & Scalability](#performance--scalability)

---

## Executive Summary

The **Multi-Agent Candidate Selection System** is an intelligent recruitment platform that leverages artificial intelligence, multi-agent systems, and Retrieval Augmented Generation (RAG) to automate and enhance the candidate evaluation process. The system uses five specialized AI agents working in coordination to analyze job offers, evaluate candidate profiles, and generate comprehensive rankings with AI-generated justifications.

### Key Innovations

- **Multi-Agent Architecture**: Five specialized agents collaborate to provide comprehensive candidate evaluation
- **RAG-Powered Retrieval**: Semantic search using vector embeddings to find relevant candidates
- **Hybrid Scoring System**: Combines rule-based algorithms with LLM-generated insights
- **Real-Time Progress Tracking**: Live updates of agent processing and document indexing
- **Modern Web Interface**: React-based dashboard with glassmorphism design and smooth animations

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (UI)                       │
│  - File Selection (DATA/jobs, DATA/raw)                     │
│  - Real-time Progress Tracking                              │
│  - Candidate Visualization                                  │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────────┐
│              FastAPI Backend Server                          │
│  - File Upload & Management                                  │
│  - Evaluation Orchestration                                  │
│  - Progress State Management                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         Multi-Agent Pipeline Orchestrator                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ RH Agent │→ │Profile   │→ │Technical │→ │Soft Skills│  │
│  └──────────┘  │Agent     │  │Agent     │  │Agent     │   │
│                 └──────────┘  └──────────┘  └──────────┘   │
│                          ↓                                   │
│                 ┌──────────────┐                            │
│                 │Decision Agent│                            │
│                 └──────────────┘                            │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              RAG System (LlamaIndex)                         │
│  - Document Loading & Chunking                               │
│  - Embedding Generation (HuggingFace)                        │
│  - Vector Search (ChromaDB)                                  │
│  - LLM Query Engine (Groq/Gemini)                            │
└──────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User Input**: Job offer file + Selected resume files
2. **Backend Processing**: 
   - File storage in DATA directories
   - RAG index building (if needed)
   - Multi-agent evaluation pipeline
3. **Agent Coordination**: Sequential processing with state updates
4. **Result Aggregation**: Decision agent combines all evaluations
5. **Frontend Display**: Real-time updates via polling

---

## Multi-Agent System Theory

### What is a Multi-Agent System?

A **Multi-Agent System (MAS)** is a computational framework where multiple autonomous agents interact to solve complex problems that are beyond the capability of a single agent. Each agent has:
- **Autonomy**: Can operate independently
- **Specialization**: Focused expertise in a specific domain
- **Coordination**: Ability to communicate and collaborate
- **Goal-Oriented**: Works toward a common objective

### Why Multi-Agent for Recruitment?

Traditional single-model approaches have limitations:
- **Limited Perspective**: One model tries to evaluate everything
- **Bias**: Single evaluation method may miss important aspects
- **Scalability**: Hard to improve individual components independently

**Multi-Agent Benefits:**
- **Specialization**: Each agent excels in its domain (technical skills, soft skills, etc.)
- **Modularity**: Easy to improve individual agents without affecting others
- **Transparency**: Clear separation of concerns makes decisions explainable
- **Robustness**: If one agent fails, others continue working
- **Parallel Processing**: Agents can work simultaneously on different aspects

### Our Multi-Agent Architecture

Our system implements a **Sequential Multi-Agent Pipeline** with **Specialized Agents**:

```
Job Offer → RH Agent → Profile Agent → Technical Agent → Soft Skills Agent → Decision Agent → Final Ranking
```

Each agent:
- Receives input from previous agents
- Performs specialized analysis
- Produces structured output
- Passes results to next agent

---

## RAG (Retrieval Augmented Generation) System

### What is RAG?

**Retrieval Augmented Generation (RAG)** is a technique that combines:
1. **Information Retrieval**: Finding relevant documents from a knowledge base
2. **Language Generation**: Using LLMs to generate answers based on retrieved context

### RAG Architecture in Our System

```
┌─────────────────────────────────────────────────────────┐
│                    Document Ingestion                    │
│  - Load CVs from DATA/raw                               │
│  - Extract text (PDF/TXT)                               │
│  - Chunk documents (1024 tokens, 128 overlap)           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Embedding Generation                    │
│  Model: BAAI/bge-large-en-v1.5                          │
│  - Converts text chunks to 1024-dim vectors             │
│  - Semantic meaning preserved                           │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Vector Storage (ChromaDB)                   │
│  - Persistent vector database                            │
│  - Stores embeddings + metadata                          │
│  - Enables fast similarity search                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                    Query Processing                      │
│  1. User query → Embedding                               │
│  2. Vector similarity search (cosine similarity)        │
│  3. Retrieve top-K relevant chunks                       │
│  4. LLM generates answer from context                    │
└──────────────────────────────────────────────────────────┘
```

### Why RAG for Candidate Selection?

**Problem**: Traditional keyword search misses semantic relationships
- "Machine Learning" ≠ "ML" ≠ "Deep Learning" (but related)
- "Python developer" should match "Python, Django, Flask"

**Solution**: Semantic search via embeddings
- Similar concepts cluster together in vector space
- Finds candidates even with different terminology
- Understands context and relationships

### RAG Implementation Details

#### 1. Document Processing

**Chunking Strategy**:
- **Chunk Size**: 1024 tokens
- **Overlap**: 128 tokens (prevents information loss at boundaries)
- **Method**: Sentence-aware splitting (preserves sentence integrity)

**Why Chunking?**
- LLMs have token limits
- Smaller chunks = better retrieval precision
- Overlap ensures context continuity

#### 2. Embedding Model

**Model**: `BAAI/bge-large-en-v1.5`
- **Type**: Dense embedding model
- **Dimensions**: 1024
- **Training**: Optimized for semantic similarity
- **Language**: English (works well for technical CVs)

**Embedding Process**:
```
Text Chunk → Tokenization → Transformer Encoder → 1024-dim Vector
```

#### 3. Vector Database (ChromaDB)

**Why ChromaDB?**
- **Persistent Storage**: Vectors saved to disk (DATA/vectorstore)
- **Fast Retrieval**: Optimized for similarity search
- **Metadata Support**: Stores file names, page numbers, etc.
- **Lightweight**: No external database server needed

**Storage Structure**:
```
ChromaDB Collection: "rag_collection"
├── IDs: Unique document chunk identifiers
├── Embeddings: 1024-dim vectors
├── Documents: Original text chunks
└── Metadata: {file_name, page_label, ...}
```

#### 4. Retrieval Process

**Similarity Search Algorithm**:
1. **Query Embedding**: Convert job requirements to vector
2. **Cosine Similarity**: Calculate similarity with all stored vectors
3. **Top-K Retrieval**: Return K most similar chunks (default: 10)
4. **Relevance Filtering**: Filter by similarity threshold

**Mathematical Foundation**:
```
similarity = cosine(query_vector, document_vector) = (q · d) / (||q|| × ||d||)
```

---

## Agent Architecture & Methodology

### Agent 1: RH Agent (Job Analysis Agent)

**Role**: Analyzes job descriptions and extracts structured requirements

**Input**: 
- Raw job description text
- Optional recruiter criteria (experience, salary, location)

**Processing Methodology**:

1. **Job Title Extraction**
   - Pattern matching for common formats
   - LLM-assisted extraction if available
   - Fallback: First line or filename

2. **Seniority Level Detection**
   - Keywords: "junior", "senior", "lead", "principal"
   - Experience-based inference

3. **Experience Requirements**
   - Regex patterns: "X years", "minimum Y years"
   - Override with explicit criteria if provided

4. **Skills Extraction**
   - **Required Skills**: Must-have competencies
   - **Optional Skills**: Nice-to-have competencies
   - Pattern matching + LLM extraction

5. **Location & Salary Parsing**
   - Structured field extraction
   - Normalization (e.g., "Paris, France" → standardized format)

**Output Structure**:
```python
{
    "poste": "Data Scientist Senior",
    "seniorite": "Senior",
    "exp_min": 5,
    "exp_max": 10,
    "skills_obligatoires": ["Python", "Machine Learning", "SQL"],
    "skills_optionnelles": ["AWS", "Docker", "Kubernetes"],
    "langues": ["Français", "Anglais"],
    "lieu": "Paris, France",
    "salaire": "55K€ - 70K€"
}
```

**Techniques Used**:
- **Named Entity Recognition (NER)**: Extracting structured entities
- **Pattern Matching**: Regex for structured data
- **LLM Enhancement**: Groq API for complex parsing

---

### Agent 2: Profile Agent (CV Analysis Agent)

**Role**: Extracts structured information from candidate CVs

**Input**:
- CV text content
- Optional cover letter
- Job profile (from RH Agent)

**Processing Methodology**:

1. **Personal Information Extraction**
   - **Name**: Pattern matching, LLM extraction
   - **Email**: Regex pattern `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
   - **Phone**: International format recognition

2. **Experience Extraction**
   - **Date Parsing**: "2020-2023", "Jan 2020 - Present"
   - **Position Titles**: Job role identification
   - **Company Names**: Organization extraction
   - **Responsibilities**: Bullet point extraction

3. **Education Extraction**
   - **Degree Levels**: Bachelor's, Master's, PhD
   - **Institutions**: University/college names
   - **Fields of Study**: Major/specialization
   - **Graduation Dates**: Timeline extraction

4. **Skills Extraction**
   - **Technical Skills**: Programming languages, frameworks, tools
   - **Method**: Keyword matching + context analysis
   - **Normalization**: "Python" = "python" = "PYTHON"

5. **Language Detection**
   - **Proficiency Levels**: Native, Fluent, Intermediate, Basic
   - **Pattern Matching**: "Français: Courant", "English: Fluent"

**Scoring Algorithm**:
```python
score_profil = (
    experience_match_score * 0.30 +  # 30 points
    skills_match_score * 0.50 +        # 50 points
    education_score * 0.20             # 20 points
)
```

**Experience Score**:
- Exact match: 30 points
- 70% of required: 20 points
- 50% of required: 10 points
- Below 50%: 0 points

**Skills Score**:
- Required skills match: (matched / total_required) × 40 points
- Optional skills match: (matched / total_optional) × 10 points

**Output Structure**:
```python
{
    "nom": "Marie Dubois",
    "email": "marie.dubois@email.com",
    "years_experience": 5.5,
    "skills_list": ["Python", "Machine Learning", "SQL", "AWS"],
    "education": [{"degree": "Master", "field": "Data Science"}],
    "languages": ["Français", "Anglais"],
    "score_profil": 87.5,
    "commentaire_profil": "Strong profile with 5+ years..."
}
```

**Techniques Used**:
- **Information Extraction**: Structured data parsing
- **Scoring Heuristics**: Rule-based matching algorithms
- **LLM Enhancement**: Complex extraction tasks

---

### Agent 3: Technical Agent

**Role**: Evaluates technical skills against job requirements

**Input**:
- Candidate skills list (from Profile Agent)
- Job profile with required/optional skills (from RH Agent)

**Processing Methodology**:

1. **Skill Matching Algorithm**
   ```python
   For each required skill:
       - Exact match: Full credit
       - Partial match: Partial credit (e.g., "Python" matches "Python 3.9")
       - Synonym match: Context-aware matching
   ```

2. **Skill Normalization**
   - Case-insensitive matching
   - Variant handling: "ML" = "Machine Learning" = "ML/AI"
   - Framework grouping: "Django" grouped with "Python web frameworks"

3. **Scoring Calculation**
   ```python
   score_technique = (
       (matched_required / total_required) × 80 +  # Required: 80%
       (matched_optional / total_optional) × 20    # Optional: 20%
   )
   ```

**Example**:
- Required: ["Python", "SQL", "ML"]
- Candidate has: ["Python", "PostgreSQL", "Machine Learning"]
- Matched: 3/3 required = 80 points
- Optional: ["AWS", "Docker"] → Candidate has 1/2 = 10 points
- **Total**: 90/100

**Output Structure**:
```python
{
    "score_technique": 90.0,
    "skills_correspondantes": ["Python", "SQL", "Machine Learning"],
    "skills_manquantes": [],
    "skills_optionnelles_trouvees": ["AWS"],
    "commentaire_technique": "Excellent technical match..."
}
```

**Techniques Used**:
- **Fuzzy Matching**: Handles variations and synonyms
- **Weighted Scoring**: Prioritizes required over optional skills
- **Context Awareness**: Understands skill relationships

---

### Agent 4: Soft Skills Agent

**Role**: Evaluates interpersonal skills, motivation, and cultural fit

**Input**:
- CV text
- Cover letter (if available)
- Experience descriptions
- Job profile

**Processing Methodology**:

1. **Soft Skills Detection**
   - **Keywords**: "teamwork", "leadership", "communication"
   - **Context Analysis**: How skills are demonstrated
   - **Experience Indicators**: Leadership roles, team projects

2. **Motivation Assessment**
   - **Cover Letter Analysis**: Enthusiasm, alignment with role
   - **Career Progression**: Upward trajectory indicates motivation
   - **Relevant Experience**: Shows interest in domain

3. **Cultural Fit Indicators**
   - **Language Proficiency**: Required languages
   - **Work Style**: Remote vs. on-site preferences
   - **Values Alignment**: Extracted from cover letter

**Scoring Algorithm**:
```python
score_softskills = (
    communication_score × 0.30 +
    teamwork_score × 0.25 +
    leadership_score × 0.20 +
    motivation_score × 0.15 +
    cultural_fit_score × 0.10
)
```

**Detection Methods**:
- **Keyword Frequency**: Count of soft skill mentions
- **Context Analysis**: How skills are demonstrated
- **LLM Evaluation**: Groq API for nuanced assessment

**Output Structure**:
```python
{
    "score_softskills": 85.0,
    "soft_skills_detectes": ["Communication", "Teamwork", "Leadership"],
    "motivation": "High",
    "commentaire_softskills": "Strong interpersonal skills..."
}
```

**Techniques Used**:
- **Sentiment Analysis**: Assesses motivation and enthusiasm
- **Pattern Recognition**: Identifies soft skill indicators
- **LLM-Based Evaluation**: Nuanced understanding of human qualities

---

### Agent 5: Decision Agent (Final Ranking Agent)

**Role**: Aggregates all evaluations and generates final ranking

**Input**:
- All agent evaluations (Profile, Technical, Soft Skills)
- Job profile

**Processing Methodology**:

1. **Global Score Calculation**
   ```python
   score_global = (
       score_profil × 0.30 +      # Profile: 30%
       score_technique × 0.40 +    # Technical: 40%
       score_softskills × 0.30     # Soft Skills: 30%
   )
   ```

2. **Recommendation Generation**
   ```python
   if score_global >= 80: "Fortement recommandé"
   elif score_global >= 65: "Recommandé"
   elif score_global >= 50: "À considérer"
   else: "À rejeter"
   ```

3. **Justification Generation**
   - Combines all agent comments
   - Highlights strengths and weaknesses
   - Provides actionable insights
   - Uses LLM for natural language generation

4. **Ranking Algorithm**
   - Sort by `score_global` (descending)
   - Break ties using individual scores
   - Generate comparative analysis

**Output Structure**:
```python
{
    "score_global": 91.7,
    "recommandation": "Fortement recommandé",
    "justification": "Comprehensive AI-generated text...",
    "rank": 1
}
```

**Techniques Used**:
- **Weighted Aggregation**: Combines multiple scores
- **Ranking Algorithms**: Multi-criteria sorting
- **LLM Text Generation**: Natural language justifications

---

## Scoring Algorithms

### Multi-Criteria Scoring Framework

Our system uses a **hierarchical scoring approach**:

```
Level 1: Individual Agent Scores (0-100)
    ├── Profile Score (Agent 2)
    ├── Technical Score (Agent 3)
    └── Soft Skills Score (Agent 4)

Level 2: Global Score (Weighted Average)
    score_global = Σ(agent_score × weight)

Level 3: Recommendation Category
    Based on score_global thresholds
```

### Score Calculation Details

#### Profile Score Formula
```python
profile_score = (
    experience_match(exp_candidate, exp_required) × 30 +
    skills_match(skills_candidate, skills_required) × 50 +
    education_score(education_candidate) × 20
)
```

**Experience Matching**:
- `exp_candidate >= exp_required`: 30 points
- `exp_candidate >= 0.7 × exp_required`: 20 points
- `exp_candidate >= 0.5 × exp_required`: 10 points
- Otherwise: 0 points

**Skills Matching**:
- Required skills: `(matched / total_required) × 40`
- Optional skills: `(matched / total_optional) × 10`

#### Technical Score Formula
```python
technical_score = (
    (matched_required_skills / total_required) × 80 +
    (matched_optional_skills / total_optional) × 20
)
```

**Rationale**: Technical skills are critical (80% weight on required)

#### Soft Skills Score Formula
```python
softskills_score = (
    communication × 0.30 +
    teamwork × 0.25 +
    leadership × 0.20 +
    motivation × 0.15 +
    cultural_fit × 0.10
)
```

**Rationale**: Balanced assessment of interpersonal qualities

#### Global Score Formula
```python
global_score = (
    profile_score × 0.30 +
    technical_score × 0.40 +
    softskills_score × 0.30
)
```

**Rationale**: 
- Technical skills are most important (40%)
- Profile and soft skills equally important (30% each)
- Reflects real-world hiring priorities

### Score Normalization

All scores are normalized to **0-100 scale**:
- Ensures comparability across agents
- Provides intuitive interpretation
- Enables consistent threshold-based recommendations

---

## LLM Integration & Fallback Mechanism

### LLM Providers

#### Primary: Groq API

**Model**: `llama-3.3-70b-versatile`
- **Provider**: Groq (high-speed inference)
- **Use Cases**: 
  - Job offer parsing
  - CV information extraction
  - Justification generation
  - Complex reasoning tasks

**Advantages**:
- **Speed**: Optimized inference hardware
- **Cost**: Competitive pricing
- **Quality**: Strong performance on structured tasks

#### Fallback: Google Gemini

**Model**: `gemini-2.0-flash`
- **Provider**: Google AI
- **Activation**: When Groq API fails or unavailable

**Fallback Logic**:
```python
try:
    result = groq_llm.generate(prompt)
except:
    result = gemini_llm.generate(prompt)  # Fallback
```

### LLM Usage Patterns

#### 1. Structured Extraction
**Task**: Extract structured data from unstructured text
**Example**: Job offer → Structured profile
**Prompt Template**:
```
Extract the following information from this job description:
- Job title
- Required skills
- Experience requirements
- Location
- Salary range

Job description: {job_text}
```

#### 2. Information Generation
**Task**: Generate natural language justifications
**Example**: Candidate evaluation → Justification text
**Prompt Template**:
```
Based on the following evaluation:
- Profile Score: {score_profil}
- Technical Score: {score_technique}
- Soft Skills Score: {score_softskills}

Generate a comprehensive justification explaining why this candidate
is {recommendation} for the {job_title} position.
```

#### 3. Complex Reasoning
**Task**: Multi-step analysis requiring context
**Example**: Soft skills assessment
**Prompt Template**:
```
Analyze the following CV and cover letter for soft skills:
- Communication abilities
- Teamwork experience
- Leadership indicators
- Motivation level

CV: {cv_text}
Cover Letter: {cover_letter}
```

### Fallback Mechanism Implementation

**Design Pattern**: Chain of Responsibility
```python
def create_llm_with_fallback():
    try:
        return GroqLLM()  # Try primary
    except:
        try:
            return GeminiLLM()  # Try fallback
        except:
            return None  # Work without LLM
```

**Graceful Degradation**:
- System works without LLM (rule-based fallback)
- LLM enhances quality but not required
- Ensures system reliability

---

## Vector Database & Embeddings

### Embedding Model: BAAI/bge-large-en-v1.5

**Model Details**:
- **Architecture**: BGE (BAAI General Embedding) Large
- **Dimensions**: 1024
- **Training**: Optimized for semantic similarity
- **Language**: English (works for technical content)

**Why This Model?**
- **State-of-the-art**: Top performance on embedding benchmarks
- **Semantic Understanding**: Captures meaning, not just keywords
- **Technical Domain**: Good performance on technical documents

### Embedding Process

**Step-by-Step**:

1. **Text Preprocessing**
   ```
   Raw Text → Clean → Normalize → Tokenize
   ```

2. **Embedding Generation**
   ```
   Tokens → Transformer Encoder → 1024-dim Vector
   ```

3. **Vector Storage**
   ```
   Vector → ChromaDB → Persistent Storage
   ```

**Mathematical Representation**:
```
f: Text → ℝ¹⁰²⁴
embedding = f(text_chunk)
```

### Similarity Search

**Algorithm**: Cosine Similarity

**Formula**:
```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

**Why Cosine Similarity?**
- **Scale Invariant**: Normalized by vector magnitude
- **Semantic Focus**: Measures direction (meaning), not magnitude
- **Range**: [-1, 1] → [0, 1] after normalization

**Search Process**:
```
Query: "Data Scientist with Python and ML"
    ↓
Embedding: [0.23, -0.45, 0.67, ...] (1024 dims)
    ↓
Cosine Similarity with all CV embeddings
    ↓
Top-K Results: Most similar CVs
```

### ChromaDB Architecture

**Storage Structure**:
```
ChromaDB
└── Collection: "rag_collection"
    ├── IDs: ["chunk_1", "chunk_2", ...]
    ├── Embeddings: [[0.23, ...], [0.45, ...], ...]
    ├── Documents: ["CV text chunk 1", "CV text chunk 2", ...]
    └── Metadata: [
        {"file_name": "cv_marie_dubois.pdf", "page": 1},
        {"file_name": "cv_pierre_martin.txt", "page": 1},
        ...
    ]
```

**Persistence**:
- Stored in `DATA/vectorstore/`
- SQLite database (`chroma.sqlite3`)
- Survives server restarts
- Incremental updates (add new documents without full rebuild)

---

## Frontend Architecture

### Technology Stack

**Core Framework**: React 18 with TypeScript
- **Build Tool**: Vite (fast development, optimized builds)
- **Styling**: TailwindCSS (utility-first CSS)
- **Animations**: Framer Motion (smooth transitions)
- **Charts**: Recharts (data visualization)
- **Icons**: Lucide React

### Component Architecture

```
App.tsx (Root Component)
├── Header (Status Display)
├── JobOfferForm
│   ├── FileSelector (DATA/jobs)
│   └── Manual Input Form
├── FileUpload
│   ├── FileSelector (DATA/raw)
│   └── Drag & Drop Upload
├── IndexBuildProgress (RAG Index Building)
├── EvaluationControl (Start Button)
├── AgentProgressSection
│   └── AgentCard × 5
├── CandidateTable
│   └── CandidateRow (Expandable)
├── CandidateDetails
│   ├── Score Breakdown
│   └── Radar Chart
└── DecisionOutput (Final Recommendation)
```

### State Management

**React Hooks Pattern**:
- `useState`: Component-level state
- `useEffect`: Side effects (polling, cleanup)
- `useRef`: Persistent references (polling cleanup)

**State Flow**:
```
User Action → API Call → State Update → UI Re-render
```

### Real-Time Updates

**Polling Mechanism**:
```typescript
pollEvaluationStatus(evaluationId, onUpdate, 2000ms)
```

**How It Works**:
1. Start evaluation → Get evaluation_id
2. Poll `/api/evaluation/{id}` every 2 seconds
3. Update UI with latest agent status
4. Stop polling when status = "completed"

**Why Polling?**
- Simple to implement
- Works with any backend
- No WebSocket complexity
- Sufficient for this use case (2s updates)

### UI/UX Design Principles

**Glassmorphism**:
- **Effect**: Frosted glass appearance
- **Implementation**: `backdrop-blur-md` + `bg-white/10`
- **Purpose**: Modern, premium feel

**Color System**:
- **Blue/Purple**: AI-related, primary actions
- **Green**: Success, recommended candidates
- **Yellow**: Processing, in-progress
- **Red**: Rejected, low scores

**Animations**:
- **Fade-in**: Sequential agent card appearance
- **Progress Bars**: Smooth width transitions
- **Hover Effects**: Scale transforms, shadow changes
- **Loading States**: Spinning indicators

---

## Backend API Design

### RESTful API Architecture

**Design Principles**:
- **RESTful**: Standard HTTP methods (GET, POST)
- **Stateless**: Each request contains all needed information
- **Resource-Based**: URLs represent resources
- **JSON**: Standard data format

### API Endpoints

#### File Management

**GET `/api/files/resumes`**
- Lists all resume files in `DATA/raw`
- Returns: `{files: [{id, filename, size, type, path}]}`

**GET `/api/files/job-offers`**
- Lists all job offer files in `DATA/jobs`
- Returns: `{files: [{id, filename, size, type, path}]}`

**GET `/api/files/job-offers/{file_id}`**
- Gets content of specific job offer file
- Handles PDF extraction
- Returns: `{id, filename, content, size}`

**POST `/api/upload-cvs`**
- Uploads CV files (multipart/form-data)
- Saves to `DATA/raw/`
- Automatically rebuilds RAG index
- Returns: `{success, files, build_id}`

#### Index Management

**POST `/api/build-index`**
- Manually rebuilds RAG vector index
- Returns: `{success, build_id, message}`

**GET `/api/index-build-progress/{build_id}`**
- Gets real-time index build progress
- Returns: `{status, step, progress, message, ...}`

**POST `/api/process-resumes`**
- Processes selected resumes and rebuilds index
- Body: `{file_ids: [string]}`
- Returns: `{success, build_id}`

#### Evaluation

**POST `/api/start-evaluation`**
- Starts multi-agent evaluation
- Body: `{job_offer, cv_ids, use_rag, max_candidates}`
- Returns: `{evaluation_id, status, message}`

**GET `/api/evaluation/{evaluation_id}`**
- Gets evaluation status and results
- Returns: `{status, agents, candidates, decision}`

### Background Task Processing

**Architecture**: FastAPI BackgroundTasks

**Why Background Tasks?**
- **Non-Blocking**: API returns immediately
- **Long-Running**: Evaluation takes minutes
- **Progress Tracking**: State stored, pollable

**Implementation**:
```python
@app.post("/api/start-evaluation")
async def start_evaluation(request, background_tasks):
    evaluation_id = uuid.uuid4()
    # Initialize state
    evaluation_states[evaluation_id] = {...}
    # Start background task
    background_tasks.add_task(run_evaluation, evaluation_id, ...)
    return {"evaluation_id": evaluation_id}
```

**State Management**:
- Global dictionary: `evaluation_states[evaluation_id]`
- Updated by background task
- Read by polling endpoint
- Persists until completion

---

## Data Flow & Processing Pipeline

### Complete Evaluation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   1. User Input                             │
│  - Upload/Select Job Offer (DATA/jobs)                     │
│  - Select/Upload Resumes (DATA/raw)                         │
└────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│             2. Backend Receives Request                    │
│  POST /api/start-evaluation                                │
│  {job_offer, cv_ids, use_rag, max_candidates}             │
└────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│          3. RAG System (If use_rag = true)                 │
│  - Query: Job requirements → Embedding                     │
│  - Vector Search: Find similar CVs                         │
│  - Retrieve: Top-K candidate documents                     │
└────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           4. Multi-Agent Pipeline                          │
│                                                             │
│  Step 1: RH Agent                                          │
│    Input: Job description                                  │
│    Output: Structured job profile                          │
│    Status: processing → completed                          │
│                                                             │
│  Step 2: Profile Agent (for each candidate)                │
│    Input: CV text + Job profile                            │
│    Output: Candidate profile + score_profil                │
│    Status: processing → completed                          │
│                                                             │
│  Step 3: Technical Agent (for each candidate)             │
│    Input: Candidate skills + Job profile                   │
│    Output: Technical score + matched skills                │
│    Status: processing → completed                          │
│                                                             │
│  Step 4: Soft Skills Agent (for each candidate)            │
│    Input: CV + Cover letter + Job profile                  │
│    Output: Soft skills score + assessment                  │
│    Status: processing → completed                          │
│                                                             │
│  Step 5: Decision Agent                                    │
│    Input: All agent evaluations                            │
│    Output: Ranked candidates + justifications              │
│    Status: processing → completed                          │
└────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           5. Result Formatting                             │
│  - Convert backend format → frontend format                │
│  - Map scores to visualizations                            │
│  - Generate decision output                                │
└────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           6. Frontend Display                              │
│  - Real-time agent progress (polling)                       │
│  - Candidate table with scores                            │
│  - Detailed breakdowns (expandable)                        │
│  - Final decision card                                     │
└─────────────────────────────────────────────────────────────┘
```

### Data Transformation Pipeline

**Backend → Frontend Mapping**:

```python
# Backend Format
{
    "score_profil": 95.0,
    "score_technique": 92.0,
    "score_softskills": 88.0,
    "score_global": 91.7,
    "recommandation": "Fortement recommandé"
}

# Frontend Format
{
    "scores": {
        "profile": 95.0,
        "technical": 92.0,
        "softSkills": 88.0,
        "global": 91.7
    },
    "recommendation": "strongly-recommended"
}
```

---

## Technology Stack

### Backend Technologies

**Core Framework**:
- **Python 3.9+**: Main programming language
- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server

**AI/ML Libraries**:
- **LlamaIndex**: RAG framework
- **ChromaDB**: Vector database
- **HuggingFace Transformers**: Embedding models
- **Sentence Transformers**: Embedding utilities

**LLM Integration**:
- **Groq SDK**: Primary LLM provider
- **Google Generative AI**: Fallback LLM provider

**Data Processing**:
- **pdfplumber**: PDF text extraction
- **PyYAML**: Configuration management
- **python-dotenv**: Environment variables

### Frontend Technologies

**Core**:
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool

**Styling & UI**:
- **TailwindCSS**: Utility-first CSS
- **Framer Motion**: Animation library
- **Lucide React**: Icon library

**Data Visualization**:
- **Recharts**: Chart library (radar charts, bar charts)

**Utilities**:
- **clsx + tailwind-merge**: Conditional class names

### Infrastructure

**Storage**:
- **File System**: DATA/raw, DATA/jobs
- **ChromaDB**: Vector storage (SQLite-based)
- **Vectorstore**: DATA/vectorstore/

**APIs**:
- **Groq API**: LLM inference
- **Gemini API**: LLM fallback

---

## Evaluation Methodology

### Candidate Evaluation Process

#### Phase 1: Job Analysis (RH Agent)

**Input Processing**:
1. Parse job description text
2. Extract structured requirements
3. Normalize and validate data

**Output Quality**:
- **Completeness**: All required fields extracted
- **Accuracy**: Correct interpretation of requirements
- **Structured Format**: Ready for downstream agents

#### Phase 2: Candidate Retrieval

**RAG-Based Retrieval** (if enabled):
1. Generate query embedding from job profile
2. Search vector database for similar CVs
3. Rank by similarity score
4. Return top-K candidates

**Fallback Retrieval** (if RAG unavailable):
1. Load all CVs from DATA/raw
2. Process sequentially
3. No semantic filtering

#### Phase 3: Multi-Agent Evaluation

**Parallel Processing** (conceptually):
- Each candidate evaluated by all agents
- Agents work independently
- Results aggregated later

**Sequential Agent Processing** (implementation):
- Agents process candidates one by one
- Ensures consistent state
- Easier to track progress

#### Phase 4: Ranking & Decision

**Aggregation Algorithm**:
```python
for candidate in candidates:
    global_score = weighted_average(
        profile_score, technical_score, softskills_score
    )
    recommendation = categorize(global_score)
    justification = generate_justification(candidate)
```

**Ranking Criteria**:
1. **Primary**: Global score (descending)
2. **Secondary**: Technical score (if global score tied)
3. **Tertiary**: Profile score (if still tied)

### Quality Assurance

**Validation Checks**:
- **Input Validation**: File formats, required fields
- **Score Bounds**: All scores in [0, 100] range
- **Data Consistency**: Matching IDs, complete records

**Error Handling**:
- **Graceful Degradation**: System works without LLM
- **Fallback Mechanisms**: Multiple LLM providers
- **Error Logging**: Detailed error messages

---

## Performance & Scalability

### Performance Characteristics

**Index Building**:
- **Time**: ~2-5 minutes for 10 CVs
- **Bottleneck**: Embedding generation
- **Optimization**: Batch processing, parallel embeddings

**Evaluation Speed**:
- **Per Candidate**: ~10-30 seconds
- **10 Candidates**: ~2-5 minutes
- **Bottleneck**: LLM API calls

**Real-Time Updates**:
- **Polling Interval**: 2 seconds
- **Response Time**: <100ms (local)
- **Scalability**: Handles 100+ concurrent evaluations

### Scalability Considerations

**Horizontal Scaling**:
- **Stateless Backend**: Can run multiple instances
- **Shared State**: Use Redis for evaluation_states
- **Load Balancing**: Distribute requests

**Vertical Scaling**:
- **Embedding Model**: GPU acceleration possible
- **Vector Database**: ChromaDB scales to millions of vectors
- **LLM API**: Groq handles high throughput

**Optimization Opportunities**:
- **Caching**: Cache job profile parsing
- **Batch Processing**: Process multiple candidates in parallel
- **Incremental Indexing**: Update index without full rebuild

---

## Advanced Features

### Progress Tracking

**Real-Time Updates**:
- **Agent Status**: Waiting → Processing → Completed
- **Progress Bars**: 0-100% with smooth animations
- **File Processing**: Current file, total files, chunks

**Implementation**:
- **State Storage**: Global dictionaries
- **Polling**: Frontend polls every 2 seconds
- **Updates**: Background tasks update state

### File Management

**Organized Structure**:
```
DATA/
├── raw/          # Candidate CVs
├── jobs/         # Job offer descriptions
└── vectorstore/  # ChromaDB storage
```

**File Selection**:
- Browse existing files
- Select multiple files
- Upload new files
- Remove files

### Error Handling & Resilience

**LLM Fallback**:
- Primary: Groq API
- Fallback: Gemini API
- Final: Rule-based (no LLM)

**System Resilience**:
- Works without RAG (file system fallback)
- Works without LLM (rule-based evaluation)
- Graceful error messages

---

## Future Enhancements

### Potential Improvements

1. **WebSocket Integration**: Real-time updates instead of polling
2. **Multi-Language Support**: Process CVs in multiple languages
3. **Advanced Matching**: ML-based skill similarity
4. **Interview Scheduling**: Integration with calendar systems
5. **Analytics Dashboard**: Statistics and trends
6. **A/B Testing**: Compare different scoring weights
7. **Feedback Loop**: Learn from recruiter decisions

### Research Directions

1. **Fine-Tuned Embeddings**: Domain-specific embedding models
2. **Reinforcement Learning**: Optimize scoring weights
3. **Explainable AI**: Better justification generation
4. **Bias Detection**: Identify and mitigate biases

---

## Conclusion

This Multi-Agent Candidate Selection System represents a comprehensive approach to AI-powered recruitment, combining:

- **Multi-Agent Systems**: Specialized agents for comprehensive evaluation
- **RAG Technology**: Semantic search for intelligent candidate retrieval
- **Modern Web Architecture**: Real-time, interactive user experience
- **Hybrid AI**: Rule-based algorithms + LLM intelligence

The system demonstrates how modern AI techniques can be applied to solve real-world HR challenges while maintaining transparency, explainability, and user control.

---

## References & Further Reading

### Key Concepts

- **Multi-Agent Systems**: Wooldridge, M. (2009). "An Introduction to MultiAgent Systems"
- **RAG**: Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- **Vector Embeddings**: Mikolov, T., et al. (2013). "Efficient Estimation of Word Representations"
- **ChromaDB**: Documentation at chromadb.ai

### Technologies

- **LlamaIndex**: llama-index.readthedocs.io
- **FastAPI**: fastapi.tiangolo.com
- **React**: react.dev
- **TailwindCSS**: tailwindcss.com

---

*This documentation provides a comprehensive technical overview suitable for creating presentations, academic papers, or technical reports.*

