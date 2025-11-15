# Step 8: Implement Ingest & Admin APIs

## Context
You are implementing the ingestion job management API and admin user management API to complete the backend functionality.

**Project Structure:**
- Backend: NestJS API in `apps/api/src/app/`
- Database: PostgreSQL with Prisma ORM
- Job Queue: Optional (Bull/BullMQ) for background processing

**Existing Setup:**
- Auth system is implemented (Step 1)
- Documents API is implemented (Step 2)
- Users table exists in schema

## Implementation Requirements

### 1. Ingest Module

#### Create Ingest Module Structure
Create `apps/api/src/app/ingest/` directory:

**ingest.module.ts**
- Register `IngestController`, `IngestService`
- Import `AuthModule`
- Optionally import BullModule for job queue

**ingest.service.ts**
Implement methods:

- `createJob(source: string, type: DocumentType, userId: string): Promise<IngestionJob>`
  - Create `IngestionJob` record with status 'pending'
  - Optionally queue background job
  - Return job record

- `processJob(jobId: string): Promise<void>`
  - Update status to 'processing'
  - Call Python scraper or process directly
  - Update status to 'completed' or 'failed'
  - Store error message if failed
  - Set `finishedAt` timestamp

- `getJobStatus(jobId: string): Promise<IngestionJob>`
  - Get job by ID
  - Throw `NotFoundException` if not found

- `listJobs(filters: IngestFiltersDto, pagination: PaginationDto): Promise<PaginatedResponse<IngestionJob>>`
  - Query jobs with filters (status, source)
  - Support pagination
  - Return paginated list

**ingest.controller.ts**
Implement endpoints:

- `POST /api/ingest`
  - Body: `{ source: string, type: DocumentType }`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.OPERATOR, Role.ADMIN)`
  - Returns: `IngestionJob`

- `GET /api/ingest/jobs`
  - Query params: `status?`, `source?`, `page?`, `limit?`
  - Protected: `@UseGuards(JwtAuthGuard)` (OPERATOR+)
  - Returns: Paginated list

- `GET /api/ingest/jobs/:id`
  - Protected: `@UseGuards(JwtAuthGuard)` (OPERATOR+)
  - Returns: `IngestionJob`

**DTOs:**

**dto/create-ingestion-job.dto.ts**
```typescript
- source: string (required, min 1, max 2000)
- type: DocumentType (required, enum)
```

**dto/ingest-filters.dto.ts**
```typescript
- status?: 'pending' | 'processing' | 'completed' | 'failed'
- source?: string
```

**dto/ingestion-job-response.dto.ts**
```typescript
- id: string
- source: string
- status: string
- startedAt: Date
- finishedAt?: Date
- error?: string
```

### 2. Background Processing (Optional)

#### Install Bull/BullMQ
Add to `apps/api/package.json`:
- `@nestjs/bull` or `bullmq`
- `redis` (for job queue)

#### Create Job Processor
Create `apps/api/src/app/ingest/ingest.processor.ts`:
- Process ingestion jobs asynchronously
- Call Python scraper via HTTP or CLI
- Update job status
- Handle errors

### 3. Users Module

#### Create Users Module Structure
Create `apps/api/src/app/users/` directory:

**users.module.ts**
- Register `UsersController`, `UsersService`
- Import `AuthModule`

**users.service.ts**
Implement methods:

- `findAll(filters: UserFiltersDto, pagination: PaginationDto): Promise<PaginatedResponse<User>>`
  - Query users with filters (role, email search)
  - Support pagination
  - Exclude password from results
  - Return paginated list

- `findOne(id: string): Promise<User>`
  - Get user by ID
  - Include orgs if requested
  - Exclude password
  - Throw `NotFoundException` if not found

- `updateRole(id: string, role: Role, currentUserId: string): Promise<User>`
  - Update user role
  - Require ADMIN role (checked by controller)
  - Prevent self-demotion from ADMIN (optional)
  - Return updated user

- `assignToOrg(userId: string, orgId: string, role: Role): Promise<void>`
  - Create or update `UserOrg` record
  - Validate org exists
  - Return success

- `removeFromOrg(userId: string, orgId: string): Promise<void>`
  - Delete `UserOrg` record
  - Return success

**users.controller.ts**
Implement endpoints:

- `GET /api/users`
  - Query params: `role?`, `email?`, `page?`, `limit?`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.ADMIN)`
  - Returns: Paginated user list

- `GET /api/users/:id`
  - Protected: `@UseGuards(JwtAuthGuard)`
  - Users can view themselves, admins can view anyone
  - Returns: `User`

- `PATCH /api/users/:id/role`
  - Body: `{ role: Role }`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.ADMIN)`
  - Returns: Updated `User`

- `POST /api/users/:userId/orgs`
  - Body: `{ orgId: string, role: Role }`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.ADMIN)`
  - Returns: Success message

- `DELETE /api/users/:userId/orgs/:orgId`
  - Protected: `@UseGuards(JwtAuthGuard, RolesGuard)` with `@Roles(Role.ADMIN)`
  - Returns: Success message

**DTOs:**

**dto/user-filters.dto.ts**
```typescript
- role?: Role (optional)
- email?: string (optional, for search)
```

**dto/update-role.dto.ts**
```typescript
- role: Role (required, enum)
```

**dto/assign-org.dto.ts**
```typescript
- orgId: string (required)
- role: Role (required, enum)
```

**dto/user-response.dto.ts**
```typescript
- id: string
- email: string
- role: Role
- createdAt: Date
- updatedAt: Date
- orgs?: UserOrgResponse[]
```

### 4. Update AppModule
- Import `IngestModule` and `UsersModule` into `AppModule`

## Unit Tests

### Ingest Service Tests
**ingest.service.spec.ts**
- Test `createJob()` - success case
- Test `processJob()` - success and failure
- Test `getJobStatus()` - success and not found
- Test `listJobs()` - filtering and pagination
- Mock PrismaService

### Ingest Controller Tests
**ingest.controller.spec.ts**
- Test all endpoints
- Test authentication and authorization
- Test validation
- Mock IngestService

### Users Service Tests
**users.service.spec.ts**
- Test `findAll()` - filtering and pagination
- Test `findOne()` - success and not found
- Test `updateRole()` - success, prevent self-demotion
- Test `assignToOrg()` - success and error
- Test `removeFromOrg()` - success
- Mock PrismaService

### Users Controller Tests
**users.controller.spec.ts**
- Test all endpoints
- Test authentication and authorization
- Test self-access vs admin access
- Mock UsersService

## Code Style & Conventions

### Backend
- Use NestJS dependency injection
- Use `class-validator` for DTOs
- Use Swagger decorators
- Handle errors consistently
- Use async/await
- Log important operations

### Testing
- Use Jest
- Mock PrismaService
- Test success and error cases
- Test authorization logic
- Test edge cases

## Success Criteria
- [ ] Ingestion jobs can be created
- [ ] Job status can be queried
- [ ] Jobs list with filters works
- [ ] Users can be listed and filtered
- [ ] User roles can be updated (admin only)
- [ ] Users can be assigned to orgs
- [ ] Role-based access control enforced
- [ ] All unit tests pass
- [ ] Swagger docs are complete

## Notes
- Consider adding job cancellation
- Consider adding job retry logic
- Consider adding job progress tracking
- Consider adding user activity logging
- Consider adding email notifications for job completion
- For production, use proper job queue (Bull/BullMQ) for background processing

