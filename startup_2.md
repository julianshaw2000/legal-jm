# Legal JM — Next Steps & Detailed TODO

## Current Project Status

### ✅ Completed

- **Database Schema**: Complete Prisma schema with all models (User, Org, Document, Section, Chunk, Embedding, QALog, etc.)
- **Database Setup**: Neon PostgreSQL with pgvector extension configured
- **Database Connectivity**: Verified working via Python CLI (`verify-db` command)
- **Backend Scaffold**: NestJS API with:
  - Basic app structure
  - PrismaService configured
  - Health endpoint (`/api/health`)
  - Swagger documentation setup
  - CORS and security (helmet) configured
- **Frontend Scaffold**: Angular app with:
  - Standalone components structure
  - Material UI configured
  - Routes scaffolded: `/`, `/browse`, `/document/:id`, `/ask`, `/ingest`, `/admin/users`
  - Basic component skeletons (all placeholder templates)
- **Python CLI**: Typer-based CLI with skeleton commands (`scrape`, `rebuild-index`)
- **Project Structure**: Nx monorepo with proper workspace configuration

### ❌ Not Yet Implemented

- Authentication & Authorization system
- API endpoints (except health)
- Frontend services to communicate with API
- RAG (Retrieval-Augmented Generation) services
- Document scraping functionality
- Embedding generation and indexing
- Frontend-backend integration
- User management features
- Document ingestion workflows

---

## Detailed TODO List

### Phase 1: Authentication & Authorization (Foundation)

#### 1.1 Backend Auth Module

- [ ] **Create Auth Module** (`apps/api/src/app/auth/`)
  - [ ] `auth.module.ts` - Register auth module
  - [ ] `auth.service.ts` - Implement:
    - [ ] `register(email, password)` - Hash password, create user
    - [ ] `login(email, password)` - Verify credentials, generate tokens
    - [ ] `refreshToken(token)` - Validate and issue new access token
    - [ ] `validateUser(email, password)` - Credential validation
  - [ ] `auth.controller.ts` - Endpoints:
    - [ ] `POST /api/auth/register` - User registration
    - [ ] `POST /api/auth/login` - Login (returns access + refresh tokens)
    - [ ] `POST /api/auth/refresh` - Refresh access token
    - [ ] `POST /api/auth/logout` - Invalidate session
  - [ ] `jwt.strategy.ts` - JWT validation strategy (if using Passport)
  - [ ] `jwt-auth.guard.ts` - Guard for protected routes
  - [ ] `roles.guard.ts` - Role-based access control guard
  - [ ] `decorators/roles.decorator.ts` - `@Roles()` decorator
  - [ ] `decorators/current-user.decorator.ts` - `@CurrentUser()` decorator
  - [ ] DTOs:
    - [ ] `register.dto.ts` - Validation for registration
    - [ ] `login.dto.ts` - Validation for login
    - [ ] `token-response.dto.ts` - Response shape

#### 1.2 Session Management

- [ ] **Implement Session Service** (`apps/api/src/app/auth/session.service.ts`)
  - [ ] Create session records in `Session` table
  - [ ] Hash tokens before storing
  - [ ] Validate session expiry
  - [ ] Cleanup expired sessions (cron job or on-demand)

#### 1.3 API Key Support

- [ ] **Implement API Key Service** (`apps/api/src/app/auth/api-key.service.ts`)
  - [ ] `generateApiKey(userId)` - Create API key, hash and store
  - [ ] `validateApiKey(key)` - Verify API key from header
  - [ ] `revokeApiKey(keyId)` - Invalidate API key
  - [ ] `listApiKeys(userId)` - List user's API keys
  - [ ] Add `X-API-Key` header authentication option

#### 1.4 Frontend Auth Service

- [ ] **Create Auth Service** (`apps/web/src/app/shared/services/auth.service.ts`)
  - [ ] `login(email, password)` - Call API, store tokens
  - [ ] `register(email, password)` - User registration
  - [ ] `logout()` - Clear tokens and session
  - [ ] `refreshToken()` - Refresh access token
  - [ ] `isAuthenticated()` - Check auth status
  - [ ] `getCurrentUser()` - Get current user info
  - [ ] Token storage (localStorage or httpOnly cookies)
  - [ ] HTTP interceptor for adding `Authorization` header
  - [ ] Auth guard for protected routes

#### 1.5 Frontend Auth Components

- [ ] **Login Component** (`apps/web/src/app/features/auth/login/`)
  - [ ] Reactive form with email/password
  - [ ] Error handling and display
  - [ ] Redirect after successful login
- [ ] **Register Component** (`apps/web/src/app/features/auth/register/`)
  - [ ] Registration form
  - [ ] Password strength validation
- [ ] **Auth Guard** (`apps/web/src/app/shared/guards/auth.guard.ts`)
  - [ ] Protect routes requiring authentication
- [ ] **Update Routes** - Add auth routes and protect admin routes

---

### Phase 2: Core API Endpoints

#### 2.1 Documents Module

- [ ] **Create Documents Module** (`apps/api/src/app/documents/`)
  - [ ] `documents.module.ts`
  - [ ] `documents.service.ts` - Business logic:
    - [ ] `findAll(filters, pagination)` - List documents with filters
    - [ ] `findOne(id)` - Get document with sections
    - [ ] `create(dto)` - Create new document
    - [ ] `update(id, dto)` - Update document
    - [ ] `delete(id)` - Soft delete or hard delete
    - [ ] `search(query, filters)` - Text search across documents
  - [ ] `documents.controller.ts` - Endpoints:
    - [ ] `GET /api/documents` - List (with pagination, filters)
    - [ ] `GET /api/documents/:id` - Get single document
    - [ ] `POST /api/documents` - Create (requires EDITOR role)
    - [ ] `PATCH /api/documents/:id` - Update (requires EDITOR role)
    - [ ] `DELETE /api/documents/:id` - Delete (requires ADMIN role)
    - [ ] `GET /api/documents/search?q=...` - Search documents
  - [ ] DTOs:
    - [ ] `create-document.dto.ts`
    - [ ] `update-document.dto.ts`
    - [ ] `document-response.dto.ts`
    - [ ] `document-list-response.dto.ts`

#### 2.2 Sections Module

- [ ] **Create Sections Module** (`apps/api/src/app/sections/`)
  - [ ] `sections.service.ts`:
    - [ ] `findByDocument(documentId)` - Get all sections for a document
    - [ ] `create(documentId, dto)` - Add section to document
    - [ ] `update(id, dto)` - Update section
    - [ ] `reorder(documentId, sectionIds)` - Reorder sections
  - [ ] `sections.controller.ts`:
    - [ ] `GET /api/documents/:documentId/sections` - List sections
    - [ ] `POST /api/documents/:documentId/sections` - Create section
    - [ ] `PATCH /api/sections/:id` - Update section
    - [ ] `DELETE /api/sections/:id` - Delete section

#### 2.3 Browse/Search API

- [ ] **Enhance Documents Service** for browse functionality
  - [ ] Filter by `DocumentType` (ACT, REGULATION, CASE, OTHER)
  - [ ] Filter by date range (`publishedAt`)
  - [ ] Sort options (date, title, relevance)
  - [ ] Pagination (cursor-based or offset-based)

#### 2.4 Ask/RAG Module

- [ ] **Create RAG Module** (`apps/api/src/app/rag/`)
  - [ ] `rag.service.ts`:
    - [ ] `ask(question, options)` - Main RAG query:
      - [ ] Generate embedding for question
      - [ ] Vector similarity search (pgvector)
      - [ ] Retrieve top-k chunks
      - [ ] Build context from chunks
      - [ ] Call LLM with question + context
      - [ ] Log Q&A to `QALog` table
      - [ ] Return answer with sources
    - [ ] `generateEmbedding(text)` - Generate embedding via OpenAI/other
    - [ ] `similaritySearch(embedding, limit)` - Vector search
  - [ ] `rag.controller.ts`:
    - [ ] `POST /api/ask` - Submit question, get answer
    - [ ] `GET /api/ask/history` - Get Q&A history (paginated)
    - [ ] `POST /api/ask/:id/feedback` - Submit feedback on answer
  - [ ] **AI Provider Abstraction** (`apps/api/src/app/rag/providers/`)
    - [ ] `ai-provider.interface.ts` - Common interface
    - [ ] `openai-provider.ts` - OpenAI implementation
    - [ ] `dry-run-provider.ts` - Mock provider for testing
    - [ ] Factory pattern to select provider based on `AI_PROVIDER` env
  - [ ] DTOs:
    - [ ] `ask-question.dto.ts`
    - [ ] `ask-response.dto.ts` - Answer + source chunks
    - [ ] `feedback.dto.ts`

#### 2.5 Ingest Module

- [ ] **Create Ingest Module** (`apps/api/src/app/ingest/`)
  - [ ] `ingest.service.ts`:
    - [ ] `createJob(source, type)` - Create ingestion job
    - [ ] `processJob(jobId)` - Process ingestion (async)
    - [ ] `getJobStatus(jobId)` - Check job status
    - [ ] `listJobs(filters)` - List ingestion jobs
  - [ ] `ingest.controller.ts`:
    - [ ] `POST /api/ingest` - Trigger ingestion (requires OPERATOR role)
    - [ ] `GET /api/ingest/jobs` - List jobs
    - [ ] `GET /api/ingest/jobs/:id` - Get job status
  - [ ] **Background Processing**:
    - [ ] Use Bull/BullMQ or similar for job queue
    - [ ] Worker to process ingestion jobs
    - [ ] Handle errors and retries

#### 2.6 Admin/Users Module

- [ ] **Create Users Module** (`apps/api/src/app/users/`)
  - [ ] `users.service.ts`:
    - [ ] `findAll(filters)` - List users (paginated)
    - [ ] `findOne(id)` - Get user details
    - [ ] `updateRole(id, role)` - Update user role (ADMIN only)
    - [ ] `assignToOrg(userId, orgId, role)` - Assign user to org
    - [ ] `removeFromOrg(userId, orgId)` - Remove from org
  - [ ] `users.controller.ts`:
    - [ ] `GET /api/users` - List users (ADMIN only)
    - [ ] `GET /api/users/:id` - Get user (self or ADMIN)
    - [ ] `PATCH /api/users/:id/role` - Update role (ADMIN only)
    - [ ] `POST /api/users/:id/orgs` - Assign to org
    - [ ] `DELETE /api/users/:id/orgs/:orgId` - Remove from org

---

### Phase 3: Frontend Services & Integration

#### 3.1 HTTP Client Setup

- [ ] **Create API Service Base** (`apps/web/src/app/shared/services/api.service.ts`)
  - [ ] Configure base URL from environment
  - [ ] HTTP interceptor for auth tokens
  - [ ] Error handling interceptor
  - [ ] Request/response logging (dev mode)

#### 3.2 Feature Services

- [ ] **Documents Service** (`apps/web/src/app/shared/services/documents.service.ts`)
  - [ ] `getDocuments(filters)` - Fetch document list
  - [ ] `getDocument(id)` - Fetch single document
  - [ ] `searchDocuments(query)` - Search
  - [ ] `createDocument(dto)` - Create document
  - [ ] `updateDocument(id, dto)` - Update document
- [ ] **Ask Service** (`apps/web/src/app/shared/services/ask.service.ts`)
  - [ ] `askQuestion(question)` - Submit question
  - [ ] `getHistory()` - Get Q&A history
  - [ ] `submitFeedback(qaLogId, rating, comment)` - Submit feedback
- [ ] **Ingest Service** (`apps/web/src/app/shared/services/ingest.service.ts`)
  - [ ] `triggerIngestion(source, type)` - Start ingestion
  - [ ] `getJobs()` - List ingestion jobs
  - [ ] `getJobStatus(id)` - Check job status
- [ ] **Users Service** (`apps/web/src/app/shared/services/users.service.ts`)
  - [ ] `getUsers()` - List users
  - [ ] `updateUserRole(id, role)` - Update role

#### 3.3 Frontend Components Implementation

##### Browse Component

- [ ] **Enhance Browse Component** (`apps/web/src/app/features/browse/`)
  - [ ] Document list with Material table/cards
  - [ ] Filters (type, date range)
  - [ ] Search input
  - [ ] Pagination
  - [ ] Loading states
  - [ ] Error handling
  - [ ] Click to navigate to document detail

##### Document Component

- [ ] **Enhance Document Component** (`apps/web/src/app/features/document/`)
  - [ ] Fetch document by ID from route
  - [ ] Display document metadata (title, type, published date)
  - [ ] Render sections with headings
  - [ ] Show amendments if any
  - [ ] Loading and error states
  - [ ] Edit button (if user has EDITOR role)

##### Ask Component

- [ ] **Enhance Ask Component** (`apps/web/src/app/features/ask/`)
  - [ ] Connect form to Ask Service
  - [ ] Display answer with loading state
  - [ ] Show source chunks/references
  - [ ] Feedback form (thumbs up/down + comment)
  - [ ] Display Q&A history below
  - [ ] Handle dry-run mode gracefully

##### Ingest Component

- [ ] **Enhance Ingest Component** (`apps/web/src/app/features/ingest/`)
  - [ ] Form to trigger ingestion (source URL, type)
  - [ ] File upload option (if supporting PDF uploads)
  - [ ] Job status list/table
  - [ ] Real-time updates (polling or WebSocket)
  - [ ] Error display for failed jobs

##### Admin Users Component

- [ ] **Enhance Admin Users Component** (`apps/web/src/app/features/admin-users/`)
  - [ ] User table with Material table
  - [ ] Role dropdown/selector
  - [ ] Assign to org functionality
  - [ ] Search/filter users
  - [ ] Pagination

---

### Phase 4: Python Scraper Implementation

#### 4.1 Scraper Infrastructure

- [ ] **Create Scraper Base Classes** (`apps/python/scrapers/`)
  - [ ] `base_scraper.py` - Abstract base class
  - [ ] `scraper_registry.py` - Registry for scrapers
  - [ ] Common utilities (HTTP client, parsing helpers)

#### 4.2 Legal Source Scrapers

- [ ] **Acts Scraper** (`apps/python/scrapers/acts_scraper.py`)
  - [ ] Identify source URLs for Jamaican Acts
  - [ ] Fetch and parse HTML/PDF
  - [ ] Extract title, sections, dates
  - [ ] Create `Document` and `Section` records
  - [ ] Handle pagination if needed
- [ ] **Regulations Scraper** (`apps/python/scrapers/regulations_scraper.py`)
  - [ ] Similar to Acts scraper
  - [ ] Handle regulation-specific structure
- [ ] **Case Law Scraper** (`apps/python/scrapers/cases_scraper.py`)
  - [ ] Scrape case law sources
  - [ ] Extract court, citation, decision date
  - [ ] Create `CaseLaw` records
- [ ] **Update CLI** (`apps/python/main.py`)
  - [ ] Wire scrapers to `scrape` command
  - [ ] Add progress indicators
  - [ ] Add error handling and retries
  - [ ] Add dry-run mode

#### 4.3 Document Processing

- [ ] **PDF Parser** (`apps/python/parsers/pdf_parser.py`)
  - [ ] Extract text from PDFs
  - [ ] Identify sections/headings
  - [ ] Handle tables and formatting
- [ ] **HTML Parser** (`apps/python/parsers/html_parser.py`)
  - [ ] Parse HTML legal documents
  - [ ] Extract structure (headings, sections)
  - [ ] Clean and normalize text

---

### Phase 5: Embeddings & Indexing

#### 5.1 Embedding Generation

- [ ] **Create Embedding Service** (`apps/python/embeddings/embedding_service.py`)
  - [ ] `generate_embedding(text)` - Call OpenAI embeddings API
  - [ ] Batch processing for efficiency
  - [ ] Error handling and retries
  - [ ] Rate limiting

#### 5.2 Chunking Strategy

- [ ] **Create Chunking Service** (`apps/python/chunking/chunking_service.py`)
  - [ ] `chunk_document(document)` - Split document into chunks
  - [ ] Strategy: by section, sliding window, or semantic boundaries
  - [ ] Preserve context (section ID, document ID)
  - [ ] Handle chunk size limits (token count)

#### 5.3 Indexing Pipeline

- [ ] **Create Indexing Service** (`apps/python/indexing/indexing_service.py`)
  - [ ] `index_document(document_id)` - Full indexing:
    - [ ] Fetch document and sections
    - [ ] Generate chunks
    - [ ] Generate embeddings for chunks
    - [ ] Store in `Chunk` and `Embedding` tables
  - [ ] `rebuild_index()` - Re-index all documents
  - [ ] `update_index(document_id)` - Update existing index
  - [ ] Progress tracking and logging

#### 5.4 Update CLI

- [ ] **Enhance `rebuild-index` command**
  - [ ] Process all documents
  - [ ] Show progress bar
  - [ ] Handle errors gracefully
  - [ ] Option to skip existing embeddings

---

### Phase 6: Testing

#### 6.1 Backend Tests

- [ ] **Unit Tests** (`apps/api/src/**/*.spec.ts`)
  - [ ] Auth service tests
  - [ ] Documents service tests
  - [ ] RAG service tests (mock LLM)
  - [ ] Guards and decorators tests
- [ ] **Integration Tests** (`apps/api-e2e/`)
  - [ ] Auth flow (register, login, refresh)
  - [ ] Document CRUD operations
  - [ ] RAG query flow
  - [ ] Role-based access control

#### 6.2 Frontend Tests

- [ ] **Unit Tests** (`apps/web/src/**/*.spec.ts`)
  - [ ] Component tests (with TestBed)
  - [ ] Service tests (mock HTTP)
  - [ ] Guard tests
- [ ] **E2E Tests** (Cypress or Playwright)
  - [ ] User registration and login
  - [ ] Browse documents
  - [ ] Ask question flow
  - [ ] Admin user management

#### 6.3 Python Tests

- [ ] **Unit Tests** (`apps/python/tests/`)
  - [ ] Scraper tests (mock HTTP responses)
  - [ ] Parser tests
  - [ ] Embedding service tests (mock API)
  - [ ] Chunking tests

---

### Phase 7: Polish & Production Readiness

#### 7.1 Error Handling

- [ ] **Backend Error Handling**
  - [ ] Global exception filter
  - [ ] Consistent error response format
  - [ ] Logging (Winston or similar)
  - [ ] Error tracking (Sentry optional)
- [ ] **Frontend Error Handling**
  - [ ] Global error handler
  - [ ] User-friendly error messages
  - [ ] Retry logic for failed requests

#### 7.2 Performance Optimization

- [ ] **Backend**
  - [ ] Database query optimization (indexes)
  - [ ] Caching (Redis for sessions, document cache)
  - [ ] Pagination for all list endpoints
  - [ ] Connection pooling (already configured in Prisma)
- [ ] **Frontend**
  - [ ] Lazy loading for routes (already done)
  - [ ] Virtual scrolling for long lists
  - [ ] Image optimization
  - [ ] Bundle size optimization

#### 7.3 Security

- [ ] **Backend**
  - [ ] Rate limiting (express-rate-limit)
  - [ ] Input validation (class-validator)
  - [ ] SQL injection prevention (Prisma handles this)
  - [ ] XSS prevention (helmet already configured)
  - [ ] CORS configuration review
- [ ] **Frontend**
  - [ ] XSS prevention (Angular sanitization)
  - [ ] CSRF protection (if using cookies)
  - [ ] Secure token storage

#### 7.4 Documentation

- [ ] **API Documentation**
  - [ ] Complete Swagger/OpenAPI annotations
  - [ ] Example requests/responses
  - [ ] Authentication guide
- [ ] **Code Documentation**
  - [ ] JSDoc for public APIs
  - [ ] README updates
  - [ ] Architecture decision records (ADRs)

#### 7.5 CI/CD

- [ ] **GitHub Actions** (or similar)
  - [ ] Lint and type-check on PR
  - [ ] Run tests on PR
  - [ ] Build on main branch
  - [ ] Deploy to staging/production (optional)
- [ ] **Pre-commit Hooks**
  - [ ] Lint-staged
  - [ ] Format check

---

### Phase 8: Advanced Features (Future)

#### 8.1 Cross-References

- [ ] **Cross-Reference Detection**
  - [ ] Parse document text for references (e.g., "Section 5 of Act X")
  - [ ] Create `CrossReference` records
  - [ ] Display cross-references in UI

#### 8.2 Amendments Tracking

- [ ] **Amendments UI**
  - [ ] Display amendments on document page
  - [ ] Show effective dates
  - [ ] Highlight amended sections

#### 8.3 Advanced Search

- [ ] **Semantic Search**
  - [ ] Search by meaning, not just keywords
  - [ ] Use embeddings for search queries
- [ ] **Faceted Search**
  - [ ] Filter by multiple criteria
  - [ ] Date range, document type, source

#### 8.4 Analytics

- [ ] **Usage Analytics**
  - [ ] Track popular documents
  - [ ] Track common questions
  - [ ] User activity logs

---

## Recommended Implementation Order

1. **Start with Phase 1 (Auth)** - Foundation for everything else
2. **Phase 2.1-2.3 (Documents API)** - Core functionality
3. **Phase 3.1-3.2 (Frontend Services)** - Connect frontend to API
4. **Phase 3.3 (Frontend Components)** - Make UI functional
5. **Phase 4 (Scraper)** - Populate database with real data
6. **Phase 5 (Embeddings)** - Enable RAG functionality
7. **Phase 2.4 (RAG API)** - Implement ask functionality
8. **Phase 2.5-2.6 (Ingest & Admin)** - Complete remaining features
9. **Phase 6-7 (Testing & Polish)** - Quality and production readiness

---

## Notes

- Use environment variables for all configuration (API keys, URLs, etc.)
- Follow the existing code style and patterns
- Write tests as you implement features (TDD recommended)
- Keep commits small and focused (Conventional Commits format)
- Update this document as you complete items
