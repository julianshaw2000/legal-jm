# Legal Document Ingestion & AI Worker

Python CLI application for scraping, ingesting, and processing Jamaican legal documents.

## Overview

This application:

- Scrapes legal documents from authoritative sources (Acts, Regulations, Case Law)
- Normalizes and structures documents
- Detects changes and manages versions
- Writes directly to Neon Postgres (shared with NestJS backend)
- Generates embeddings for semantic search
- Provides CLI commands for ingestion and processing

## Setup

### Prerequisites

- Python 3.12+
- `uv` package manager
- Neon Postgres database with pgvector extension
- OpenAI API key (for embeddings)

### Installation

```bash
cd apps/python
uv sync
```

### Environment Variables

Create a `.env` file in the project root (or set these environment variables):

```bash
# Required
DATABASE_URL=postgresql://user:password@host/database

# Optional - OpenAI for embeddings
OPENAI_API_KEY=sk-...

# Optional - Source URLs
SCRAPE_BASE_URL_ACTS=https://www.moj.gov.jm
SCRAPE_BASE_URL_REGULATIONS=https://www.moj.gov.jm
SCRAPE_BASE_URL_CASES=https://www.court.gov.jm

# Optional - Configuration
LOG_LEVEL=INFO
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=2.0
```

## Usage

### Health Check

Verify database connectivity and configuration:

```bash
uv run main.py healthcheck
```

### Ingest Documents

Scrape and ingest legal documents:

```bash
# Ingest Acts only
uv run main.py ingest-acts

# Ingest Regulations only
uv run main.py ingest-regulations

# Ingest Case Law only
uv run main.py ingest-cases

# Ingest all sources
uv run main.py ingest-all
```

### Update Embeddings

Generate or update embeddings for document chunks:

```bash
# Update all chunks without embeddings
uv run main.py update-embeddings

# Update embeddings for a specific document
uv run main.py update-embeddings --document-id <document-id>

# Process in batches
uv run main.py update-embeddings --batch-size 50
```

### Verify Database

Alias for healthcheck:

```bash
uv run main.py verify-db
```

## Architecture

### Project Structure

```
apps/python/
├── main.py                 # CLI entrypoint
├── config.py              # Configuration management
├── models.py              # Pydantic/dataclass models
├── logging_conf.py        # Logging setup
├── db/
│   ├── connection.py      # Database connection management
│   └── repositories.py    # Data access layer
├── ingest/
│   ├── normalizer.py      # Text normalization
│   ├── parser.py          # Document parsing
│   ├── service.py         # Ingestion orchestration
│   └── sources/
│       ├── base.py        # Base scraper class
│       ├── acts.py        # Acts scraper
│       ├── regulations.py # Regulations scraper
│       └── cases.py       # Cases scraper
└── embeddings/
    ├── generator.py       # Embedding generation (OpenAI)
    ├── chunker.py         # Text chunking
    └── service.py         # Embedding management
```

### Key Components

1. **Scrapers** (`ingest/sources/`): Fetch documents from legal sources
2. **Parser** (`ingest/parser.py`): Extract structured data from HTML/text
3. **Normalizer** (`ingest/normalizer.py`): Clean and normalize content
4. **Repositories** (`db/repositories.py`): Database access layer
5. **Ingestion Service** (`ingest/service.py`): Orchestrates the ingestion workflow
6. **Embedding Service** (`embeddings/service.py`): Generates and stores embeddings

### Database Schema

The application works with the Prisma schema defined in `prisma/schema.prisma`. Key models:

- `Source`: Legal document sources
- `Document`: Acts, Regulations, Cases
- `Section`: Sections within documents
- `Chunk`: Text chunks for embeddings
- `Embedding`: Vector embeddings (pgvector)
- `IngestionJob`: Job tracking and status

## Development

### Adding a New Scraper

1. Create a new scraper class in `ingest/sources/` extending `BaseScraper`
2. Implement the `scrape()` method
3. Return a `ScrapeResult` with document counts
4. Integrate with `IngestionService` in the CLI command

### Testing

```bash
# Run health check
uv run main.py healthcheck

# Test database connection
uv run main.py verify-db
```

## Notes

- The application writes directly to Postgres using SQLAlchemy
- Schema changes should be made via Prisma migrations in the NestJS app
- The Python app assumes the schema exists and adapts queries accordingly
- Embeddings require pgvector extension in Postgres
- Scrapers are skeleton implementations - actual scraping logic needs to be implemented based on source structure

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly
- Check network connectivity to Neon
- Ensure database has pgvector extension enabled

### Embedding Generation Fails

- Verify `OPENAI_API_KEY` is set
- Check API quota and rate limits
- Review logs for specific error messages

### Import Errors

- Ensure you're running from the `apps/python` directory
- Verify all dependencies are installed: `uv sync`
- Check that Python 3.12+ is being used
