You are my senior full-stack engineer. Build a production-ready Jamaican Law Legal Advisor system (web app + API + data/AI pipeline). Follow everything below exactly. When something is ambiguous, choose the simplest, most robust option and keep moving. Always write code, migrations, tests, and docs together.

the .env file at the project root has database key and openai key

there is a scaffolded project in the following folders:

    - for angular in app/web

    - for nestjs in apps/api

    - for the python injestion program in apps/python

\# TECH \& GLOBAL CONVENTIONS

\- Frontend: Angular (latest) with \*\*standalone components\*\* (no NgModules), \*\*SCSS\*\*, \*\*signals\*\*, \*\*Reactive Forms\*\*, \*\*Angular Material\*\* styling.

\- Create a single shared Angular Material module that re-exports the Material components we use so all components can import it easily (even though the app is standalone).

\- Use feature-first structure. Global responsive CSS in `src/styles.scss`. Each feature has its own service. Add a `shared/` folder for shared UI, pipes, models, guards, interceptors.

\- Backend: \*\*NestJS\*\* (latest) + \*\*Prisma\*\* + \*\*PostgreSQL (Neon)\*\*. Use `pgvector` for embeddings. Add OpenAPI (Swagger), Zod DTO validation (via `zod-to-openapi` or `nestjs-zod`), class-validator not required.

\- Auth: JWT access + refresh tokens, password (Argon2) + optional magic link; roles: `admin`, `editor`, `reviewer`, `operator`, `viewer`.

\- AI/RAG: Use embeddings + retrieval with source citations. Keep LLM calls behind a service with provider abstraction. Add a “dry run” mode that returns mock answers for local dev without keys.

\- Secrets via environment: never hardcode. Use `.env.example` and safe fallbacks. Support Docker builds.

\- Testing: End-to-end and unit tests everywhere (Angular + Nest). Use \*\*mocks\*\* for network/LLM/DB. Enforce best practices.

\- Tooling: ESLint, Prettier, Husky + lint-staged, commitlint. GitHub Actions CI for lint, typecheck, test, build.

\# DATABASE (Prisma schema + migrations)

Use PostgreSQL (Neon). Include \*\*pgvector\*\*. Create tables for:

`user`, `session`, `api\_key`, `org`, `user\_org`, `source`, `document`, `section`, `amendment`, `case\_law`, `cross\_reference`, `embedding`, `chunk`, `qa\_log`, `feedback`, `event\_log`, and `ingestion\_job`.

\# ENV \& NEON SETUP

Produce `.env.example` and `infra/neon.md` documenting how to set up Neon, enable `pgvector`, and run migrations. Cursor only needs a valid `DATABASE\_URL` with a role having `CREATE`/`ALTER` permissions.

\# BACKEND (NestJS)

Modules: `auth`, `users`, `corpus`, `search`, `qa`, `admin`, `health`

Controllers: for auth, ingestion, search, QA, feedback, and health.

Include PrismaService, EmbeddingService (OpenAI adapter), RagService, IngestionService (PDF/HTML to chunks), SearchService.

Include seed script to insert sample Acts/Regulations/Case data.

\# FRONTEND (Angular)

Feature routes: `/`, `/browse`, `/document/:id`, `/ask`, `/ingest`, `/admin/users`

Shared services: AuthService, SearchService, QaService, CorpusService, IngestService

Use Angular Material and signals for state. Responsive layout via SCSS flex.

\# SECURITY

Rate limiting, CORS, Helmet, and role-based access. Disclaimer and privacy docs.

\# TESTING

Unit tests for backend and frontend. Mock network/DB/LLM. E2E for login → search → view doc → ask.

---

\# NEW ADDITION — PYTHON TERMINAL SCRAPER PROGRAM

Also create a \*\*Python 3.11+ terminal application\*\* (in `tools/scraper/`) that scrapes official Jamaican legal sources and \*\*populates the database\*\* automatically.

\### PURPOSE

To fetch, parse, and populate the PostgreSQL/Neon tables defined above (e.g., `source`, `document`, `section`, `case\_law`, etc.) from public legal sources such as:

\- Jamaica Gazette

\- Ministry of Justice (moj.gov.jm)

\- Court of Appeal (courtofappeal.gov.jm)

\- Parliament of Jamaica

\- Supreme Court Judgments

\### ARCHITECTURE

\- Use \*\*Fast, standalone CLI\*\* with `Typer` (or `argparse`) for commands:

- `scrape acts`

- `scrape cases`

- `scrape regulations`

- `scrape all`

- `verify-db`

- `rebuild-index`

\- Use `requests`, `httpx`, and `BeautifulSoup4` for scraping and HTML parsing.

\- Use `pdfplumber` or `PyMuPDF` for extracting text from PDFs.

\- Use `tiktoken` or `nltk` for chunking long text.

\- Store raw text and parsed metadata in the DB (`source`, `document`, `section`, `case\_law` tables).

\- Use \*\*SQLAlchemy + psycopg2\*\* for DB access (direct to the Neon `DATABASE\_URL`).

\- Provide an `.env`-based configuration (via `python-dotenv`).

\- Log to console using `rich` for colorized output.

\### EXAMPLE COMMANDS

I'll create a comprehensive Cursor prompt for building this Jamaican Law Legal Advisor system. Here's the optimized prompt following best practices:

markdown

You are my senior full-stack engineer. Build a production-ready Jamaican Law Legal Advisor system (web app + API + data/AI pipeline + Python scraper). Follow everything below exactly. When something is ambiguous, choose the simplest, most robust option and keep moving. Always write code, migrations, tests, and docs together.

\## ARCHITECTURE OVERVIEW

\- \*\*Frontend\*\*: Angular (latest) with standalone components, SCSS, signals, Reactive Forms, Angular Material

\- \*\*Backend\*\*: NestJS + Prisma + PostgreSQL (Neon) with pgvector

\- \*\*AI/RAG\*\*: Embeddings + retrieval with source citations, provider abstraction

\- \*\*Scraper\*\*: Python 3.11+ CLI tool for legal data ingestion

\- \*\*Auth\*\*: JWT access + refresh tokens, Argon2, role-based (admin, editor, reviewer, operator, viewer)

\- \*\*Testing\*\*: Comprehensive unit + E2E tests with mocks

\## PROJECT STRUCTURE

jamaican-law-advisor/

├── frontend/ # Angular application

├── backend/ # NestJS API

├── tools/scraper/ # Python CLI scraper

├── infra/ # Deployment \& database docs

└── shared/ # Shared types/configs

text

\## TECH SPECIFICATIONS

\### FRONTEND (Angular)

\- \*\*Standalone components only\*\* - no NgModules

\- \*\*Signals\*\* for state management

\- \*\*Angular Material\*\* with shared module re-export

\- \*\*Feature-first structure\*\*: `features/`, `shared/`, `core/`

\- \*\*Routes\*\*: `/`, `/browse`, `/document/:id`, `/ask`, `/ingest`, `/admin/users`

\- \*\*Services\*\*: AuthService, SearchService, QaService, CorpusService, IngestService

\### BACKEND (NestJS)

\- \*\*Modules\*\*: `auth`, `users`, `corpus`, `search`, `qa`, `admin`, `health`

\- \*\*Validation\*\*: Zod DTOs with `nestjs-zod`

\- \*\*Database\*\*: Prisma + PostgreSQL (Neon) + pgvector

\- \*\*AI Service\*\*: Provider abstraction with dry-run mode

\- \*\*OpenAPI\*\* documentation with Swagger

\### PYTHON SCRAPER (tools/scraper/)

\- \*\*Framework\*\*: Typer CLI with Rich console

\- \*\*Libraries\*\*: httpx, BeautifulSoup4, pdfplumber, SQLAlchemy, python-dotenv

\- \*\*Commands\*\*:

- `scrape acts` - Fetch legislation from Parliament

- `scrape cases` - Get case law from courts

- `scrape regulations` - Extract from Jamaica Gazette

- `scrape all` - Run all scrapers

- `verify-db` - Validate database state

- `rebuild-index` - Refresh vector embeddings

\### DATABASE SCHEMA (Prisma)

```prisma

// Core entities

model User { id String @id @default(cuid()) ... }

model Org { id String @id @default(cuid()) ... }

model Document { id String @id @default(cuid()) ... }

model Section { id String @id @default(cuid()) ... }

model CaseLaw { id String @id @default(cuid()) ... }



// AI/RAG entities

model Chunk { id String @id @default(cuid()) ... }

model Embedding {

 id String @id @default(cuid())

 chunkId String @unique

 vector Unsupported("vector(1536)")? // pgvector

 ...

}



// Support entities

model Source { id String @id @default(cuid()) ... }

model Amendment { id String @id @default(cuid()) ... }

model CrossReference { id String @id @default(cuid()) ... }

model QALog { id String @id @default(cuid()) ... }

model Feedback { id String @id @default(cuid()) ... }

IMPLEMENTATION PRIORITIES

PHASE 1: Foundation

Database setup with Neon + pgvector + Prisma migrations



Backend auth with JWT + role management



Basic Angular app with routing and Material



Python scraper skeleton with DB connection



PHASE 2: Core Features

Document ingestion pipeline (PDF/HTML → chunks → embeddings)



Search service with vector similarity



QA service with source citations



Scraper implementations for key sources



PHASE 3: Polish \& Scale

Admin dashboard and user management



Feedback and analytics systems



Comprehensive testing suite



Production deployment setup



ENVIRONMENT \& CONFIGURATION

Environment variables via .env.example patterns



Docker support for all components



Secrets management with safe fallbacks



Development dry-run mode for AI features



SECURITY REQUIREMENTS

Rate limiting on all endpoints



CORS configured for frontend domains



Helmet security headers



Role-based access control



Input validation with Zod schemas



TESTING STRATEGY

Unit tests: All services, components, utilities



E2E tests: Critical user journeys (login → search → ask → view)



Mocks: LLM, database, external APIs



CI/CD: GitHub Actions for lint, test, build



DELIVERABLES FOR EACH COMPONENT

When implementing any feature, always provide:

Code - Production-ready implementation



Migrations - Database schema changes



Tests - Unit + integration tests



Documentation - Usage examples and API docs



Environment updates - Required config changes



For Angular components:

Standalone component with signals



SCSS styling with responsive design



Angular Material components



Reactive forms with validation



Unit tests with TestBed



For NestJS modules:

Zod DTO validation



Prisma service integration



OpenAPI decorators



Comprehensive test coverage



Error handling



For Python scraper:

Typer command implementation



Rich progress reporting



Error handling with retries



Database operations with SQLAlchemy



PDF/text parsing logic



MOCK DATA \& SEEDING

Provide seed scripts for sample legal documents



Mock LLM responses for development



Test users with different roles



Sample Q\&A pairs for demonstration



START IMPLEMENTATION

Begin with the database schema and initial setup. Create the Prisma schema, Neon documentation, and basic project structure. Then proceed with authentication and the core Angular/NestJS application.



Remember: When faced with ambiguity, choose the simplest robust solution and maintain momentum. Write tests and documentation alongside code.

```
