# Step 9: Testing & Production Polish

## Context
You are implementing comprehensive testing, error handling, performance optimization, and production readiness features for Legal JM.

**Project Structure:**
- Backend: NestJS API
- Frontend: Angular app
- Python: Scraper CLI
- Testing: Jest for TS/JS, pytest for Python

**Existing Setup:**
- Basic test structure exists
- Some unit tests may be implemented
- Need comprehensive test coverage
- Need production optimizations

## Implementation Requirements

### 1. Backend Testing

#### Integration Tests
Enhance `apps/api-e2e/`:

**auth.e2e-spec.ts**
- Test full auth flow:
  - Register user
  - Login with credentials
  - Access protected route
  - Refresh token
  - Logout
- Test error cases (invalid credentials, expired tokens)

**documents.e2e-spec.ts**
- Test document CRUD:
  - Create document (authenticated)
  - List documents (public)
  - Get document by ID
  - Update document (authorized)
  - Delete document (admin only)
- Test filtering and pagination
- Test search functionality

**rag.e2e-spec.ts**
- Test ask endpoint:
  - Submit question
  - Get answer with sources
  - Submit feedback
  - Get history
- Test with dry-run mode

**ingest.e2e-spec.ts**
- Test ingestion:
  - Create job (authorized)
  - Get job status
  - List jobs
- Test authorization

**users.e2e-spec.ts**
- Test user management:
  - List users (admin only)
  - Update role (admin only)
  - Assign to org (admin only)

#### Unit Test Coverage
Ensure all services and controllers have tests:
- [ ] AuthService - 100% coverage
- [ ] DocumentsService - 100% coverage
- [ ] SectionsService - 100% coverage
- [ ] RAGService - 100% coverage
- [ ] IngestService - 100% coverage
- [ ] UsersService - 100% coverage
- [ ] All controllers - main paths covered
- [ ] All guards - covered
- [ ] All interceptors - covered

### 2. Frontend Testing

#### Component Tests
Ensure all components have tests:
- [ ] BrowseComponent - filters, pagination, navigation
- [ ] DocumentComponent - document display, error handling
- [ ] AskComponent - form submission, answer display
- [ ] IngestComponent - form submission, job list
- [ ] AdminUsersComponent - user list, role updates
- [ ] LoginComponent - form validation, submission
- [ ] RegisterComponent - form validation, submission

#### Service Tests
Ensure all services have tests:
- [ ] AuthService - all methods
- [ ] DocumentsService - all methods
- [ ] SectionsService - all methods
- [ ] AskService - all methods
- [ ] IngestService - all methods
- [ ] UsersService - all methods

#### E2E Tests (Optional but Recommended)
Set up Cypress or Playwright:
- [ ] User registration and login flow
- [ ] Browse documents flow
- [ ] Ask question flow
- [ ] Admin user management flow

### 3. Python Testing

#### Scraper Tests
Ensure scrapers have tests:
- [ ] BaseScraper - abstract class
- [ ] ActsScraper - scraping logic
- [ ] RegulationsScraper - scraping logic
- [ ] CasesScraper - scraping logic
- [ ] PDFParser - parsing logic
- [ ] HTMLParser - parsing logic

#### Embedding Tests
Ensure embedding services have tests:
- [ ] EmbeddingService - API calls, error handling
- [ ] ChunkingService - chunking strategies
- [ ] IndexingService - indexing logic

### 4. Error Handling

#### Backend Global Exception Filter
Create `apps/api/src/app/common/filters/http-exception.filter.ts`:
- Catch all exceptions
- Transform to consistent format:
  ```typescript
  {
    error: {
      message: string;
      statusCode: number;
      errors?: Record<string, string[]>;
    },
    traceId: string;
  }
  ```
- Log errors appropriately
- Don't expose sensitive info in production

#### Frontend Global Error Handler
Create `apps/web/src/app/shared/services/error-handler.service.ts`:
- Catch unhandled errors
- Display user-friendly messages
- Log errors (console in dev, service in prod)
- Show error notifications (Material snackbar)

#### Error Interceptor Enhancement
Update `error.interceptor.ts`:
- Handle different HTTP status codes
- Transform error responses
- Show user-friendly messages
- Handle network errors

### 5. Logging

#### Backend Logging
Install and configure Winston or NestJS Logger:
- [ ] Structured logging
- [ ] Log levels (error, warn, info, debug)
- [ ] Request logging middleware
- [ ] Error logging with stack traces
- [ ] Log rotation (production)

#### Frontend Logging
Create logging service:
- [ ] Console logging in development
- [ ] Error reporting service integration (optional: Sentry)
- [ ] User action logging (optional)

### 6. Performance Optimization

#### Backend Optimizations
- [ ] Database query optimization:
  - Add indexes on frequently queried fields
  - Use `select` to limit fields
  - Use pagination everywhere
  - Optimize N+1 queries
- [ ] Caching:
  - Redis for session storage (optional)
  - Cache frequently accessed documents (optional)
- [ ] Response compression (gzip)
- [ ] Connection pooling (already configured)

#### Frontend Optimizations
- [ ] Lazy loading routes (already done)
- [ ] Virtual scrolling for long lists
- [ ] Image optimization
- [ ] Bundle size optimization:
  - Tree shaking
  - Code splitting
  - Remove unused dependencies
- [ ] OnPush change detection (already done)
- [ ] Memoization for expensive computations

### 7. Security Enhancements

#### Backend Security
- [ ] Rate limiting:
  - Install `@nestjs/throttler`
  - Configure rate limits per endpoint
  - Different limits for auth endpoints
- [ ] Input validation:
  - Ensure all DTOs use `class-validator`
  - Sanitize user input
- [ ] SQL injection prevention:
  - Prisma handles this, but verify raw queries
- [ ] XSS prevention:
  - Helmet already configured
  - Verify CORS settings
- [ ] Security headers:
  - Verify Helmet configuration
  - Add CSP headers if needed

#### Frontend Security
- [ ] XSS prevention:
  - Angular sanitization (automatic)
  - Verify no `innerHTML` with user content
- [ ] CSRF protection:
  - If using cookies, implement CSRF tokens
- [ ] Secure token storage:
  - Consider httpOnly cookies for production
  - Or ensure localStorage is secure

### 8. Documentation

#### API Documentation
- [ ] Complete Swagger annotations:
  - All endpoints documented
  - All DTOs documented
  - Examples provided
  - Authentication documented
- [ ] API versioning (optional):
  - Consider `/api/v1/` prefix

#### Code Documentation
- [ ] JSDoc comments for public APIs
- [ ] README updates:
  - Setup instructions
  - API documentation link
  - Environment variables
  - Deployment guide

#### Architecture Documentation
- [ ] Create `docs/architecture.md`:
  - System overview
  - Component diagrams
  - Data flow
  - Technology choices

### 9. CI/CD

#### GitHub Actions Workflow
Create `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint:
    - Run linting (ESLint, Prettier)

  typecheck:
    - Run TypeScript type checking

  test-backend:
    - Run backend unit tests
    - Run backend e2e tests

  test-frontend:
    - Run frontend unit tests

  test-python:
    - Run Python tests

  build:
    - Build backend
    - Build frontend
```

#### Pre-commit Hooks
Set up Husky or similar:
- [ ] Lint-staged:
  - Run linter on staged files
  - Run formatter on staged files
- [ ] Type checking:
  - Run TypeScript compiler
- [ ] Tests:
  - Run affected tests (optional)

### 10. Environment Configuration

#### Environment Files
- [ ] `.env.example` - Complete with all variables
- [ ] `.env.development` - Development defaults
- [ ] `.env.production` - Production template
- [ ] Document all environment variables

#### Configuration Validation
- [ ] Validate required env vars on startup
- [ ] Provide helpful error messages
- [ ] Use default values where appropriate

## Unit Tests Checklist

### Backend
- [ ] All services have >80% coverage
- [ ] All controllers have tests
- [ ] All guards have tests
- [ ] All interceptors have tests
- [ ] All DTOs are validated
- [ ] Error cases are tested
- [ ] Edge cases are tested

### Frontend
- [ ] All components have tests
- [ ] All services have tests
- [ ] All guards have tests
- [ ] All interceptors have tests
- [ ] User interactions are tested
- [ ] Error scenarios are tested

### Python
- [ ] All scrapers have tests
- [ ] All parsers have tests
- [ ] All services have tests
- [ ] Error handling is tested

## Success Criteria
- [ ] Test coverage >80% for all modules
- [ ] All E2E tests pass
- [ ] Error handling is consistent
- [ ] Logging is comprehensive
- [ ] Performance is optimized
- [ ] Security measures are in place
- [ ] Documentation is complete
- [ ] CI/CD pipeline works
- [ ] Application is production-ready

## Notes
- Consider using code coverage tools (Jest coverage, pytest-cov)
- Consider using static analysis tools (ESLint, Pylint)
- Consider using dependency scanning tools
- Consider setting up monitoring (APM, error tracking)
- Consider setting up health checks for production
- Consider adding metrics collection (Prometheus, etc.)

