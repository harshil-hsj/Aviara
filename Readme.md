Contract Intelligence API

A FastAPI-based system for extracting structured data from contracts, answering questions, and detecting risky clauses. Supports PDF ingestion, RAG-based Q&A, clause auditing, and LLM-assisted metadata extraction with optional streaming.

##Features

1) Upload multiple PDFs and extract text + metadata.

2) Structured extraction of fields: parties, effective_date, term, governing_law, payment_terms, termination, auto_renewal,  confidentiality, indemnity, liability_cap, signatories.

3) RAG-based Q&A over uploaded contracts with citations.

4) Clause auditing for risky terms (e.g., auto-renewal < 30 days, unlimited liability, broad indemnity).

5) Streaming responses for long answers (/ask/stream).

6) Admin endpoints for health, metrics

##Setup

1) Clone the repository
2) Create and activate virtual environment
3) Install dependencies
4) Setup .env file
    MONGO_URI=your_atlas_connection_string
    DATABASE=DB_name
    TABLE=table_name
    GEMINI_API_KEY=your_api_key
    SIMILARITY_THRESHOLD=0.6
5) uvicorn app.main:app --reload


##API endpoints
1) /ingest -> Ingests pdf and extract meta data from pdf.
2) /ask -> Returns answers to asked question and citations and text proofs.
3) /extract -> Returns metadata for an ingested pdf.
4) /audit -> Return risky/important information for a document with citation.
5) /ask/stream -> Streams token-by-token response from the LLM via SSE.
6) /healthz -> Healthcheck for hosted service.
7) /metrics -> Returns Metrics for the service.
8) /docs -> opens swagger.

Example Curl for ingesting a pdf locally 

curl -X 'POST' \
  'http://127.0.0.1:8000/ingest' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@NDA_Updated.pdf;type=application/pdf'

Test Questions
  What is the termination clause in the contract?
  What is the effective date of this contract?
  Which law governs this agreement?

Security Notes - Always keep the api-keys and mongo DB connection string in .env file only.