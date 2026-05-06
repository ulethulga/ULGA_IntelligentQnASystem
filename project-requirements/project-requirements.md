# System Requirements for ULGA By-Law Question-Answering System

## 1. Functional Requirements (FRs)

Functional requirements describe what the system must do.

### 1.1 User Authentication & Authorization

#### FR-1: User Login
The system must allow ULGA members to log in using:
- University Single Sign-On (preferred)
- Union-issued credentials
- Email-based verification

#### FR-2: Role-Based Access
The system must support at least the following roles:
- Member (default)
- ULGA Executive Team
- System Administrator

Only authorized roles may upload/update by-law documents.

#### FR-3: Session Management
The system must log out users automatically after inactivity (e.g., 30 minutes).

### 1.2 Question Input and Processing

#### FR-4: Natural Language Question Submission
Users must be able to type questions in natural language (English, Bengali optional).
The system must support desktop and mobile inputs.

#### FR-5: Question Validation
The system must validate questions for:
- Minimum length (e.g., > 5 characters)
- Restricted content (e.g., non-by-law-related personal data, harassment)

#### FR-6: Context Extraction
The system must extract key entities and subjects from the user question for retrieval.

### 1.3 Retrieval-Augmented Generation (RAG) Pipeline

#### FR-7: Document Retrieval
The system must query a vector database (e.g., Chroma, Pinecone, FAISS) to retrieve top-K relevant by-law passages.

#### FR-8: Chunking & Embedding
By-law documents must be:
- Pre-processed into chunks (e.g., 300–1000 tokens)
- Embedded using an embedding model (OpenAI, LLaMA, or local model)

#### FR-9: Grounded Answer Generation
The LLM must generate answers based strictly on:
- Retrieved by-law passages
- Official union policies

The system must minimize hallucinations by enforcing retrieval-grounded prompts.

#### FR-10: Source Citation
The system must display citations of the by-law sections used in the answer.
Users should be able to click links to open the relevant by-law sections.

### 1.4 By-Law Document Management

#### FR-11: Document Upload
Authorized users must be able to upload:
- PDF
- DOCX
- TXT/Markdown

Document versions must be tracked.

#### FR-12: Document Pre-processing
Each upload must automatically trigger:
- Text extraction
- Cleaning (removal of headers/footers)
- Chunking
- Embedding
- Indexing in vector store

#### FR-13: Version Control
Users must be able to view:
- Current version
- Previous versions
- Change logs

#### FR-14: Rebuild Index
Admins must be able to force re-embedding and index rebuild.

### 1.5 User Dashboard & Interaction Features

#### FR-15: Search History
Logged-in members can view:
- Previous questions
- System answers
- Time stamps

#### FR-16: Feedback Collection
Users must be able to rate answers:
- Helpful / Not Helpful
- Additional comments

#### FR-17: Follow-Up Questions
The system must allow threaded follow-up questions with context preserved.

#### FR-18: FAQ Auto-Generation
Frequently asked questions should be automatically stored and accessible as an FAQ page.

### 1.6 Administration Panel

#### FR-19: User Management
Admins can suspend, activate, or modify user roles.

#### FR-20: Analytics Dashboard
System must show:
- Number of questions asked
- Topic distribution (e.g., "membership", "finance", "elections")
- Accuracy feedback stats
- System usage over time

#### FR-21: Manual Answer Override
Admins can override an LLM-generated response and pin the corrected answer.

### 1.7 Security and Compliance

#### FR-22: Access Logging
All user activities must be logged.

#### FR-23: Audit Trails
Records of all changes to by-law documents must be stored securely.

## 2. Non-Functional Requirements (NFRs)

Non-functional requirements describe how well the system must perform.

### 2.1 Performance Requirements

#### NFR-1: Response Time
LLM + RAG answer generation must complete within 2–6 seconds for normal load.

#### NFR-2: Scalability
Must support 500+ members asking questions concurrently with no major slowdown.

#### NFR-3: High Availability
Service availability must be 99.5% or higher.

### 2.2 Usability Requirements

#### NFR-4: Mobile-Friendly Interface
The system must be fully responsive on:
- Android
- iOS
- Desktop browsers

#### NFR-5: Accessibility
Must comply with WCAG 2.1 AA accessibility standards.

#### NFR-6: Clear Explanation
Answers must be written at a Grade 8–10 English readability unless quoting legal text.

### 2.3 Reliability Requirements

#### NFR-7: Fault Tolerance
The system must gracefully handle:
- Vector DB downtime
- API failures
- Network delays

Retry and fallback mechanisms must be implemented.

#### NFR-8: Data Backup
By-law documents, embeddings, logs must be backed up daily.

### 2.4 Security Requirements

#### NFR-9: Data Encryption
All data must be encrypted:
- In transit (TLS 1.3)
- At rest (AES-256)

#### NFR-10: Sensitive Information Protection
System must not store:
- Personal chat content beyond retention window
- User passwords (must rely on OAuth/SAML)

#### NFR-11: Compliance
Must comply with:
- University data policies
- Alberta FOIP (Freedom of Information and Protection of Privacy Act)

### 2.5 Maintainability Requirements

#### NFR-12: Modular Architecture
System must be built with modular components:
- Front-end UI
- RAG engine
- Vector DB
- LLM client
- Admin dashboard
- Logging service

#### NFR-13: Documentation
Full documentation needed:
- API documentation
- Deployment guide
- System architecture diagrams

#### NFR-14: Testability
The system must include:
- Unit tests
- API integration tests
- LLM response evaluation tests
- Regression tests when by-law updates occur

### 2.6 Ethical & Transparency Requirements

#### NFR-15: Hallucination Mitigation
System must:
- Always cite retrieved supporting evidence
- Warn user when insufficient context exists
- Avoid making policy interpretations beyond written by-laws

#### NFR-16: Explainability
Answers must include:
- Source text snippets
- Section numbers
- Highlighted relevant clauses

### 2.7 Deployment Requirements

#### NFR-17: Cloud Compatibility
System must run on:
- Azure
- AWS
- On-prem servers (optional)

#### NFR-18: Containerization
Deployment must use:
- Docker containers
- Orchestration using Kubernetes or Docker Compose
Desktop browsers 



NFR-5: Accessibility 



Must comply with WCAG 2.1 AA accessibility standards. 



NFR-6: Clear Explanation 



Answers must be written at a Grade 8–10 English readability unless quoting legal text. 


