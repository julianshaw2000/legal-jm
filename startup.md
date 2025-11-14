# Legal JM — Startup Guide

This document walks you through setting up the development environment, creating the database, running the apps, and executing unit tests for the Legal JM system.

## 1) Prerequisites

- Node.js 20+ and npm 10+
- Python 3.12+ (for the scraper)
- Git
- A Neon PostgreSQL account (free tier is fine)

Optional but recommended:

- uv (Python package/runtime manager) — `pip install uv` or see `https://docs.astral.sh/uv/`

## 2) Clone and install

```powershell
# from your workspace
git clone <your-fork-or-repo-url> legal-jm
cd legal-jm

# install JS/TS deps
npm install
```

## 3) Environment variables

Copy the example env and fill your values (especially DATABASE_URL).

```powershell
Copy-Item infra\env.example .env
# Edit .env and set:
# - DATABASE_URL (Neon connection string, include ?sslmode=require)
# - JWT_* secrets
# - OPENAI_API_KEY (optional; set AI_DRY_RUN=true for local dev without keys)
```

Security note:

- Do not commit `.env`. It is ignored by git. If you ever accidentally commit secrets, rotate them immediately and rewrite history (already performed once in this repo).

## 4) Create the Neon database and enable pgvector

In Neon:

1. Create a new project and database.
2. In the SQL console run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Create a role with permissions or use the default. Make sure your `DATABASE_URL` looks like:

```
postgres://user:pass@host/db?sslmode=require
```

More detail: see `infra/neon.md`.

## 5) Prisma — generate client and run migrations

From repo root:

```powershell
npm run prisma:generate
npm run prisma:migrate
```

This applies the schema in `prisma/schema.prisma` and prepares the DB (including the `vector(1536)` column via `Unsupported("vector(1536)")`).

Optional: browse the DB

```powershell
npx prisma studio
```

## 6) Run the backend (NestJS)

```powershell
npx nx serve @legal-jm/api
```

- API base: `http://localhost:3000/api`
- Swagger: `http://localhost:3000/api/docs`
- Health: `http://localhost:3000/api/health`

## 7) Run the frontend (Angular)

```powershell
npx nx serve web
```

- Web app: `http://localhost:4200`
- Routes scaffolded: `/`, `/browse`, `/document/:id`, `/ask`, `/ingest`, `/admin/users`

Notes:

- Angular Material/CDK/Animations are installed and animations are enabled via `provideAnimations()`.

## 8) Python scraper (tools/scraper skeleton)

We provide a Typer-based CLI in `apps/python/main.py`.

Verify DB connectivity:

```powershell
# using uv (recommended)
uv run python apps/python/main.py verify-db

# or with your Python directly (ensure dependencies from apps/python/pyproject.toml)
python apps/python/main.py verify-db
```

Skeleton commands (not fully implemented yet):

- `scrape acts|cases|regulations|all`
- `rebuild-index`

## 9) Lint, type-check, and unit tests

Run linters:

```powershell
npx nx lint web
npx nx lint @legal-jm/api
```

Unit tests (Jest):

```powershell
# Frontend
npx nx test web

# Backend
npx nx test @legal-jm/api
```

E2E tests:

- API E2E scaffold exists in `apps/api-e2e`. To run, configure your preferred e2e runner or extend the Nx target.

## 10) Common troubleshooting

- TypeScript: “customConditions can only be used when moduleResolution is …”

  - We set `moduleResolution` to `bundler` in `tsconfig.base.json`.

- Missing Node types:

  - We installed `@types/node` and `types: ["node"]` is configured for the API.

- “Cannot find module 'helmet' / '@nestjs/swagger'”

  - Both are installed and added under the API package. Run `npm install` again if necessary.

- Angular template errors with Angular Material:

  - Ensure `@angular/material`, `@angular/cdk`, and `@angular/animations` are installed and that `provideAnimations()` is in `apps/web/src/app/app.config.ts`.

- New Angular control flow:
  - We use `@if (...) { ... }` syntax. Example: `@if (answer(); as a) { ... }`.

## 11) Next steps

- Implement auth (`auth`, `users` modules) and role enforcement.
- Implement RAG services (provider abstraction + dry-run mode already supported via env).
- Add seed script and initial corpus.
- Wire Angular services to API endpoints and build UI for browse/ask.
- Add CI (lint, typecheck, test, build) and pre-commit hooks if desired.
