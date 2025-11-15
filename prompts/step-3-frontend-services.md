# Step 3: Implement Frontend Services & API Integration

## Context
You are implementing the frontend services layer that connects Angular components to the NestJS API. This includes HTTP services, interceptors, and shared utilities.

**Project Structure:**
- Frontend: Angular standalone components in `apps/web/src/app/`
- Backend API: NestJS running on `http://localhost:3000/api`
- Auth: JWT tokens stored in localStorage (from Step 1)

**Existing Setup:**
- `AuthService` should be implemented (Step 1)
- `MaterialModule` is configured
- Routes are set up
- HTTP client should be available via `provideHttpClient()` (check `app.config.ts`)

## Implementation Requirements

### 1. HTTP Client Configuration

#### Update App Config
Ensure `apps/web/src/app/app.config.ts` includes:
```typescript
import { provideHttpClient, withInterceptors } from '@angular/common/http';
```
Add `provideHttpClient()` to providers array.

### 2. Create Base API Service

#### Create API Service Base
Create `apps/web/src/app/shared/services/api.service.ts`:
- `protected baseUrl = 'http://localhost:3000/api'` (or from environment)
- `protected http = inject(HttpClient)`
- Helper methods for common HTTP operations
- Error handling utilities

**Environment Configuration:**
Create `apps/web/src/environments/environment.ts`:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
};
```

Create `apps/web/src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.yourdomain.com/api',
};
```

### 3. Auth Interceptor (If Not Already Created)

#### Update Auth Interceptor
Ensure `apps/web/src/app/shared/interceptors/auth.interceptor.ts`:
- Adds `Authorization: Bearer <token>` header
- Handles 401 errors
- Attempts token refresh on 401
- Redirects to login if refresh fails

**Register Interceptor:**
In `app.config.ts`, use `withInterceptors([authInterceptor])` with `provideHttpClient()`.

### 4. Error Interceptor

#### Create Error Interceptor
Create `apps/web/src/app/shared/interceptors/error.interceptor.ts`:
- Catches HTTP errors
- Transforms error responses to user-friendly messages
- Logs errors (console in dev, service in prod)
- Handles network errors
- Returns consistent error format

**Error Response Interface:**
```typescript
interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}
```

### 5. Documents Service

#### Create Documents Service
Create `apps/web/src/app/shared/services/documents.service.ts`:

**Methods:**
- `getDocuments(filters?: DocumentFilters, pagination?: Pagination): Observable<PaginatedResponse<Document>>`
  - Calls `GET /api/documents`
  - Maps query parameters
  - Returns typed response

- `getDocument(id: string): Observable<DocumentWithSections>`
  - Calls `GET /api/documents/:id`
  - Returns document with sections

- `searchDocuments(query: string, filters?: DocumentFilters): Observable<Document[]>`
  - Calls `GET /api/documents/search?q=...`
  - Returns search results

- `createDocument(dto: CreateDocumentDto): Observable<Document>`
  - Calls `POST /api/documents`
  - Requires authentication
  - Returns created document

- `updateDocument(id: string, dto: UpdateDocumentDto): Observable<Document>`
  - Calls `PATCH /api/documents/:id`
  - Requires authentication
  - Returns updated document

- `deleteDocument(id: string): Observable<void>`
  - Calls `DELETE /api/documents/:id`
  - Requires authentication

**Interfaces/Types:**
Create `apps/web/src/app/shared/models/document.models.ts`:
```typescript
export interface Document {
  id: string;
  title: string;
  type: 'ACT' | 'REGULATION' | 'CASE' | 'OTHER';
  sourceId?: string;
  publishedAt?: string;
  createdAt: string;
  updatedAt: string;
  source?: { id: string; name: string };
  sectionCount?: number;
}

export interface DocumentWithSections extends Document {
  sections: Section[];
  amendments?: Amendment[];
}

export interface Section {
  id: string;
  documentId: string;
  index: number;
  heading?: string;
  text: string;
  createdAt: string;
}

export interface Amendment {
  id: string;
  documentId: string;
  description: string;
  effectiveAt?: string;
  createdAt: string;
}

export interface DocumentFilters {
  type?: DocumentType;
  sourceId?: string;
  publishedAfter?: string;
  publishedBefore?: string;
  search?: string;
}

export interface Pagination {
  page?: number;
  limit?: number;
  sortBy?: 'title' | 'publishedAt' | 'createdAt';
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface CreateDocumentDto {
  title: string;
  type: DocumentType;
  sourceId?: string;
  publishedAt?: string;
}

export interface UpdateDocumentDto {
  title?: string;
  type?: DocumentType;
  sourceId?: string | null;
  publishedAt?: string | null;
}

export type DocumentType = 'ACT' | 'REGULATION' | 'CASE' | 'OTHER';
```

### 6. Sections Service

#### Create Sections Service
Create `apps/web/src/app/shared/services/sections.service.ts`:

**Methods:**
- `getSections(documentId: string): Observable<Section[]>`
  - Calls `GET /api/documents/:documentId/sections`

- `createSection(documentId: string, dto: CreateSectionDto): Observable<Section>`
  - Calls `POST /api/documents/:documentId/sections`

- `updateSection(id: string, dto: UpdateSectionDto): Observable<Section>`
  - Calls `PATCH /api/sections/:id`

- `deleteSection(id: string): Observable<void>`
  - Calls `DELETE /api/sections/:id`

- `reorderSections(documentId: string, sectionIds: string[]): Observable<Section[]>`
  - Calls `POST /api/documents/:documentId/sections/reorder`

**DTOs:**
Add to `document.models.ts`:
```typescript
export interface CreateSectionDto {
  heading?: string;
  text: string;
  index?: number;
}

export interface UpdateSectionDto {
  heading?: string | null;
  text?: string;
  index?: number;
}
```

### 7. Ask Service

#### Create Ask Service
Create `apps/web/src/app/shared/services/ask.service.ts`:

**Methods:**
- `askQuestion(question: string): Observable<AskResponse>`
  - Calls `POST /api/ask`
  - Body: `{ question: string }`
  - Returns answer with sources

- `getHistory(pagination?: Pagination): Observable<PaginatedResponse<QALog>>`
  - Calls `GET /api/ask/history`
  - Returns Q&A history

- `submitFeedback(qaLogId: string, rating: number, comment?: string): Observable<void>`
  - Calls `POST /api/ask/:id/feedback`
  - Body: `{ rating: number, comment?: string }`

**Interfaces:**
Create `apps/web/src/app/shared/models/ask.models.ts`:
```typescript
export interface AskResponse {
  answer: string;
  sources: SourceChunk[];
  qaLogId: string;
}

export interface SourceChunk {
  chunkId: string;
  documentId: string;
  documentTitle: string;
  sectionId?: string;
  sectionHeading?: string;
  text: string;
  similarity?: number;
}

export interface QALog {
  id: string;
  question: string;
  answer?: string;
  dryRun: boolean;
  createdAt: string;
  feedbacks?: Feedback[];
}

export interface Feedback {
  id: string;
  rating: number;
  comment?: string;
  createdAt: string;
}
```

### 8. Ingest Service

#### Create Ingest Service
Create `apps/web/src/app/shared/services/ingest.service.ts`:

**Methods:**
- `triggerIngestion(source: string, type: DocumentType): Observable<IngestionJob>`
  - Calls `POST /api/ingest`
  - Body: `{ source: string, type: DocumentType }`

- `getJobs(filters?: IngestFilters): Observable<IngestionJob[]>`
  - Calls `GET /api/ingest/jobs`

- `getJobStatus(id: string): Observable<IngestionJob>`
  - Calls `GET /api/ingest/jobs/:id`

**Interfaces:**
Create `apps/web/src/app/shared/models/ingest.models.ts`:
```typescript
export interface IngestionJob {
  id: string;
  source: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  startedAt: string;
  finishedAt?: string;
  error?: string;
}

export interface IngestFilters {
  status?: IngestionJob['status'];
  source?: string;
}
```

### 9. Users Service

#### Create Users Service
Create `apps/web/src/app/shared/services/users.service.ts`:

**Methods:**
- `getUsers(filters?: UserFilters, pagination?: Pagination): Observable<PaginatedResponse<User>>`
  - Calls `GET /api/users`

- `getUser(id: string): Observable<User>`
  - Calls `GET /api/users/:id`

- `updateUserRole(id: string, role: Role): Observable<User>`
  - Calls `PATCH /api/users/:id/role`
  - Body: `{ role: Role }`

- `assignToOrg(userId: string, orgId: string, role: Role): Observable<void>`
  - Calls `POST /api/users/:userId/orgs`
  - Body: `{ orgId: string, role: Role }`

- `removeFromOrg(userId: string, orgId: string): Observable<void>`
  - Calls `DELETE /api/users/:userId/orgs/:orgId`

**Interfaces:**
Create `apps/web/src/app/shared/models/user.models.ts`:
```typescript
export interface User {
  id: string;
  email: string;
  role: Role;
  createdAt: string;
  updatedAt: string;
  orgs?: UserOrg[];
}

export interface UserOrg {
  userId: string;
  orgId: string;
  role: Role;
  org: { id: string; name: string };
}

export type Role = 'ADMIN' | 'EDITOR' | 'REVIEWER' | 'OPERATOR' | 'VIEWER';

export interface UserFilters {
  role?: Role;
  email?: string;
}
```

### 10. Loading State Service (Optional but Recommended)

#### Create Loading Service
Create `apps/web/src/app/shared/services/loading.service.ts`:
- Signal-based loading state
- `isLoading(): Signal<boolean>`
- `setLoading(loading: boolean): void`
- Can be used with HTTP interceptor to automatically set loading state

## Unit Tests

### API Service Tests
**api.service.spec.ts**
- Test base URL configuration
- Test error handling utilities
- Mock HttpClient

### Documents Service Tests
**documents.service.spec.ts**
- Test all methods with success responses
- Test error handling
- Test query parameter mapping
- Mock HttpClient and AuthService

### Sections Service Tests
**sections.service.spec.ts**
- Test all CRUD operations
- Test reorder functionality
- Mock HttpClient

### Ask Service Tests
**ask.service.spec.ts**
- Test `askQuestion()` - success and error
- Test `getHistory()` - pagination
- Test `submitFeedback()`
- Mock HttpClient

### Ingest Service Tests
**ingest.service.spec.ts**
- Test `triggerIngestion()`
- Test `getJobs()` with filters
- Test `getJobStatus()`
- Mock HttpClient

### Users Service Tests
**users.service.spec.ts**
- Test all user management methods
- Test role updates
- Test org assignments
- Mock HttpClient

### Error Interceptor Tests
**error.interceptor.spec.ts**
- Test error transformation
- Test network error handling
- Test different HTTP status codes
- Mock HTTP requests

## Code Style & Conventions

### Frontend
- Use standalone services (no NgModules)
- Use `inject()` function for dependency injection
- Use RxJS `Observable` for async operations
- Use `pipe()` with operators (`map`, `catchError`, `retry`)
- Use typed interfaces for all API responses
- Handle errors with `catchError` operator
- Use `finalize` for cleanup (loading states)
- Follow existing Angular patterns

### Testing
- Use Jest (configured in project)
- Mock `HttpClient` using `HttpTestingController`
- Test success and error cases
- Test query parameter building
- Use `describe()`, `it()`, `expect()` structure
- Use `beforeEach()` for setup

## Success Criteria
- [ ] All services are created and typed
- [ ] HTTP interceptors work correctly
- [ ] Error handling is consistent
- [ ] All services have unit tests
- [ ] Services use proper TypeScript types
- [ ] Environment configuration works
- [ ] Auth tokens are added to requests
- [ ] Error messages are user-friendly

## Notes
- Consider using RxJS operators like `retry()` for network resilience
- Consider implementing request caching for GET requests
- Consider using `shareReplay()` for frequently accessed data
- Consider implementing a loading state management system
- All API calls should handle loading and error states appropriately

