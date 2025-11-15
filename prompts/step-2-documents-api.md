# Step 2: Implement Documents API (Core Functionality)

## Context
You are implementing the core Documents API for Legal JM. This includes endpoints for managing documents, sections, and browsing/searching the legal corpus.

**Project Structure:**
- Backend: NestJS API in `apps/api/src/app/`
- Database: PostgreSQL with Prisma ORM
- Schema: `Document`, `Section`, `Source`, `DocumentType` enum (ACT, REGULATION, CASE, OTHER)

**Existing Setup:**
- `PrismaService` is configured
- Auth system should be implemented (Step 1)
- Use `@UseGuards(JwtAuthGuard)` for protected endpoints
- Use `@Roles()` decorator for role-based access

## Implementation Requirements

### 1. Documents Module

#### Install Dependencies
Add to `apps/api/package.json`:
- `class-validator` - DTO validation (if not already installed)
- `class-transformer` - DTO transformation (if not already installed)

#### Create Documents Module Structure
Create `apps/api/src/app/documents/` directory:

**documents.module.ts**
- Register `DocumentsController`, `DocumentsService`
- Import `AuthModule` to use guards
- Export `DocumentsService` for use in other modules

**documents.service.ts**
Implement the following methods:

- `findAll(filters: DocumentFiltersDto, pagination: PaginationDto): Promise<PaginatedResponse<Document>>`
  - Query documents with filters (type, date range, search)
  - Include related `Source` and count of `Section`s
  - Support pagination (offset/limit or cursor-based)
  - Support sorting (by `publishedAt`, `createdAt`, `title`)
  - Return paginated response with metadata

- `findOne(id: string): Promise<DocumentWithSections>`
  - Get document by ID
  - Include all `Section`s ordered by `index`
  - Include `Source` if exists
  - Include `Amendment`s if any
  - Throw `NotFoundException` if not found

- `create(dto: CreateDocumentDto, userId: string): Promise<Document>`
  - Create new document
  - Require EDITOR role (checked by controller)
  - Set `createdAt` and `updatedAt`
  - Link to `Source` if `sourceId` provided
  - Return created document

- `update(id: string, dto: UpdateDocumentDto, userId: string): Promise<Document>`
  - Update existing document
  - Require EDITOR role
  - Update `updatedAt` timestamp
  - Validate document exists
  - Return updated document

- `delete(id: string): Promise<void>`
  - Delete document (cascade deletes sections, chunks)
  - Require ADMIN role
  - Throw `NotFoundException` if not found

- `search(query: string, filters: DocumentFiltersDto): Promise<Document[]>`
  - Full-text search across document titles and section text
  - Use PostgreSQL `tsvector` or `ILIKE` for search
  - Apply filters (type, date range)
  - Limit results (e.g., top 50)
  - Return documents with relevance score (if possible)

**documents.controller.ts**
Implement endpoints:

- `GET /api/documents`
  - Query params: `type?`, `sourceId?`, `publishedAfter?`, `publishedBefore?`, `search?`, `page?`, `limit?`, `sortBy?`, `sortOrder?`
  - Public endpoint (or VIEWER role minimum)
  - Returns paginated list

- `GET /api/documents/:id`
  - Public endpoint (or VIEWER role minimum)
  - Returns document with sections

- `POST /api/documents`
  - Body: `CreateDocumentDto`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.EDITOR)`
  - Returns created document

- `PATCH /api/documents/:id`
  - Body: `UpdateDocumentDto`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.EDITOR)`
  - Returns updated document

- `DELETE /api/documents/:id`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.ADMIN)`
  - Returns success message

- `GET /api/documents/search?q=...`
  - Query params: `q` (required), `type?`, `publishedAfter?`, `publishedBefore?`
  - Public endpoint
  - Returns search results

**DTOs:**

**dto/create-document.dto.ts**
```typescript
- title: string (required, min 1, max 500)
- type: DocumentType (required, enum)
- sourceId?: string (optional)
- publishedAt?: Date (optional)
```

**dto/update-document.dto.ts**
```typescript
- title?: string (optional, min 1, max 500)
- type?: DocumentType (optional)
- sourceId?: string (optional, nullable)
- publishedAt?: Date (optional, nullable)
```

**dto/document-filters.dto.ts**
```typescript
- type?: DocumentType (optional)
- sourceId?: string (optional)
- publishedAfter?: Date (optional)
- publishedBefore?: Date (optional)
- search?: string (optional, for title search)
```

**dto/pagination.dto.ts**
```typescript
- page?: number (default: 1, min: 1)
- limit?: number (default: 20, min: 1, max: 100)
- sortBy?: 'title' | 'publishedAt' | 'createdAt' (default: 'createdAt')
- sortOrder?: 'asc' | 'desc' (default: 'desc')
```

**dto/document-response.dto.ts**
```typescript
- id: string
- title: string
- type: DocumentType
- sourceId?: string
- publishedAt?: Date
- createdAt: Date
- updatedAt: Date
- source?: { id: string; name: string }
- sectionCount?: number
```

**dto/paginated-response.dto.ts**
```typescript
- data: T[]
- meta: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
```

### 2. Sections Module

#### Create Sections Module Structure
Create `apps/api/src/app/sections/` directory:

**sections.module.ts**
- Register `SectionsController`, `SectionsService`
- Import `AuthModule`

**sections.service.ts**
- `findByDocument(documentId: string): Promise<Section[]>`
  - Get all sections for a document, ordered by `index`
  - Include related `Chunk` count if needed
  - Throw `NotFoundException` if document doesn't exist

- `create(documentId: string, dto: CreateSectionDto): Promise<Section>`
  - Create new section
  - Auto-increment `index` (get max index + 1)
  - Validate document exists
  - Require EDITOR role (checked by controller)

- `update(id: string, dto: UpdateSectionDto): Promise<Section>`
  - Update section (title, text, index)
  - If updating index, reorder other sections
  - Require EDITOR role

- `delete(id: string): Promise<void>`
  - Delete section
  - Reorder remaining sections (decrement indices)
  - Require EDITOR role

- `reorder(documentId: string, sectionIds: string[]): Promise<Section[]>`
  - Reorder sections by providing ordered array of IDs
  - Update indices accordingly
  - Require EDITOR role

**sections.controller.ts**
- `GET /api/documents/:documentId/sections`
  - Public or VIEWER role
  - Returns sections ordered by index

- `POST /api/documents/:documentId/sections`
  - Body: `CreateSectionDto`
  - Protected: `@Roles(Role.EDITOR)`
  - Returns created section

- `PATCH /api/sections/:id`
  - Body: `UpdateSectionDto`
  - Protected: `@Roles(Role.EDITOR)`
  - Returns updated section

- `DELETE /api/sections/:id`
  - Protected: `@Roles(Role.EDITOR)`
  - Returns success message

- `POST /api/documents/:documentId/sections/reorder`
  - Body: `{ sectionIds: string[] }`
  - Protected: `@Roles(Role.EDITOR)`
  - Returns reordered sections

**DTOs:**

**dto/create-section.dto.ts**
```typescript
- heading?: string (optional, max 200)
- text: string (required, min 1)
- index?: number (optional, auto-assigned if not provided)
```

**dto/update-section.dto.ts**
```typescript
- heading?: string (optional, nullable)
- text?: string (optional)
- index?: number (optional)
```

**dto/section-response.dto.ts**
```typescript
- id: string
- documentId: string
- index: number
- heading?: string
- text: string
- createdAt: Date
```

### 3. Update AppModule
- Import `DocumentsModule` and `SectionsModule` into `AppModule`

### 4. Swagger Documentation
- Add `@ApiTags('documents')` and `@ApiTags('sections')` to controllers
- Add `@ApiOperation()` for each endpoint
- Add `@ApiResponse()` for success and error cases
- Add `@ApiBearerAuth()` for protected endpoints
- Document query parameters with `@ApiQuery()`

## Unit Tests

### Documents Service Tests
**documents.service.spec.ts**
- `findAll()` - Test filtering, pagination, sorting
- `findOne()` - Test success, not found
- `create()` - Test success, validation errors
- `update()` - Test success, not found, validation
- `delete()` - Test success, not found
- `search()` - Test search query, filters
- Mock `PrismaService`

### Documents Controller Tests
**documents.controller.spec.ts**
- Test all endpoints with valid/invalid inputs
- Test authentication guards
- Test role-based access
- Test query parameter parsing
- Mock `DocumentsService`

### Sections Service Tests
**sections.service.spec.ts**
- `findByDocument()` - Test success, document not found
- `create()` - Test success, auto-index assignment
- `update()` - Test success, index reordering
- `delete()` - Test success, index reordering after delete
- `reorder()` - Test reordering logic
- Mock `PrismaService`

### Sections Controller Tests
**sections.controller.spec.ts**
- Test all endpoints
- Test authentication and authorization
- Mock `SectionsService`

## Code Style & Conventions

### Backend
- Use NestJS dependency injection
- Use `@Injectable()` for services
- Use `class-validator` decorators for DTOs
- Use `@ApiTags()`, `@ApiOperation()`, `@ApiResponse()` for Swagger
- Use `NotFoundException` from `@nestjs/common` for 404 errors
- Use `BadRequestException` for validation errors
- Use `ForbiddenException` for authorization errors
- Return consistent response format
- Use async/await
- Handle Prisma errors (unique constraint, foreign key, etc.)

### Testing
- Use Jest
- Mock PrismaService methods
- Test success and error cases
- Test edge cases (empty results, pagination boundaries)
- Use `describe()`, `it()`, `expect()` structure
- Use `beforeEach()` for setup

## Success Criteria
- [ ] Documents can be created, read, updated, deleted
- [ ] Sections can be created, read, updated, deleted
- [ ] Pagination works correctly
- [ ] Filtering by type, date, source works
- [ ] Search functionality works
- [ ] Role-based access control enforced
- [ ] All unit tests pass
- [ ] Swagger docs are complete
- [ ] Error handling is consistent
- [ ] Section reordering works

## Notes
- Consider adding database indexes on frequently queried fields (`type`, `publishedAt`, `sourceId`)
- For production, consider implementing cursor-based pagination instead of offset-based
- Full-text search can be enhanced with PostgreSQL `tsvector` and `tsquery` for better relevance
- Consider adding soft delete instead of hard delete for audit purposes

