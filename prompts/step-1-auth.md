# Step 1: Implement Authentication & Authorization System

## Context

You are implementing the authentication and authorization system for Legal JM, a legal document management and RAG (Retrieval-Augmented Generation) system. This is the foundation that all other features will build upon.

**Project Structure:**

- Backend: NestJS API in `apps/api/src/app/`
- Frontend: Angular standalone components in `apps/web/src/app/`
- Database: PostgreSQL with Prisma ORM
- Auth: JWT-based authentication with access and refresh tokens

**Existing Setup:**

- Prisma schema includes `User`, `Session`, `ApiKey`, `Role` enum (ADMIN, EDITOR, REVIEWER, OPERATOR, VIEWER)
- Environment variables: `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, `JWT_EXPIRES_IN`, `JWT_REFRESH_EXPIRES_IN`
- `PrismaService` is already configured and available

## Implementation Requirements

### Backend (NestJS)

#### 1. Install Required Dependencies

Add to `apps/api/package.json`:

- `@nestjs/jwt` - JWT token handling
- `@nestjs/passport` - Passport integration
- `passport` - Authentication middleware
- `passport-jwt` - JWT strategy for Passport
- `bcrypt` - Password hashing
- `class-validator` - DTO validation
- `class-transformer` - DTO transformation
- `@types/passport-jwt` - TypeScript types
- `@types/bcrypt` - TypeScript types

#### 2. Create Auth Module Structure

Create `apps/api/src/app/auth/` directory with:

**auth.module.ts**

- Import `JwtModule` with configuration from environment variables
- Register `AuthService`, `AuthController`, `JwtStrategy`, `JwtAuthGuard`, `RolesGuard`
- Export `JwtAuthGuard` and `RolesGuard` for use in other modules

**auth.service.ts**

- `register(email: string, password: string): Promise<{ accessToken: string; refreshToken: string; user: User }>`
  - Hash password using bcrypt (10 rounds)
  - Create user with default role VIEWER
  - Generate access and refresh tokens
  - Create session record (hash token before storing)
  - Return tokens and user (without password)
- `login(email: string, password: string): Promise<{ accessToken: string; refreshToken: string; user: User }>`
  - Find user by email
  - Verify password using bcrypt
  - Generate tokens
  - Create session record
  - Return tokens and user
- `refreshToken(refreshToken: string): Promise<{ accessToken: string }>`
  - Validate refresh token
  - Find session by hashed token
  - Check if session is expired
  - Generate new access token
  - Return new access token
- `logout(token: string): Promise<void>`
  - Find and delete session record
- `validateUser(email: string, password: string): Promise<User | null>`
  - Internal validation helper
- `hashToken(token: string): string`
  - Hash token using bcrypt before storing

**auth.controller.ts**

- `POST /api/auth/register` - Public endpoint
  - Body: `{ email: string, password: string }`
  - Returns: `{ accessToken: string, refreshToken: string, user: { id, email, role } }`
- `POST /api/auth/login` - Public endpoint
  - Body: `{ email: string, password: string }`
  - Returns: `{ accessToken: string, refreshToken: string, user: { id, email, role } }`
- `POST /api/auth/refresh` - Public endpoint (but requires valid refresh token)
  - Body: `{ refreshToken: string }`
  - Returns: `{ accessToken: string }`
- `POST /api/auth/logout` - Protected endpoint
  - Uses `@UseGuards(JwtAuthGuard)`
  - Extracts token from request
  - Returns: `{ message: 'Logged out successfully' }`

**jwt.strategy.ts**

- Extends `PassportStrategy(Strategy)` from `passport-jwt`
- Extract token from `Authorization: Bearer <token>` header
- Validate token and return user payload
- Handle token expiration errors

**guards/jwt-auth.guard.ts**

- Extends `AuthGuard('jwt')`
- Can be used with `@UseGuards(JwtAuthGuard)` decorator

**guards/roles.guard.ts**

- Extends `CanActivate`
- Checks if user has required role(s)
- Works with `@Roles()` decorator

**decorators/roles.decorator.ts**

- `@Roles(...roles: Role[])` decorator
- Stores roles in metadata for `RolesGuard`

**decorators/current-user.decorator.ts**

- `@CurrentUser()` decorator
- Extracts user from request (set by JWT strategy)

**dto/register.dto.ts**

- `email: string` - Must be valid email format
- `password: string` - Min length 8 characters
- Use `class-validator` decorators

**dto/login.dto.ts**

- `email: string` - Must be valid email format
- `password: string` - Required

**dto/refresh-token.dto.ts**

- `refreshToken: string` - Required

**dto/token-response.dto.ts**

- `accessToken: string`
- `refreshToken?: string`
- `user: { id: string; email: string; role: Role }`

#### 3. Session Service

Create `apps/api/src/app/auth/session.service.ts`:

- `createSession(userId: string, tokenHash: string, expiresAt: Date): Promise<Session>`
- `findSessionByTokenHash(tokenHash: string): Promise<Session | null>`
- `deleteSession(tokenHash: string): Promise<void>`
- `deleteExpiredSessions(): Promise<number>` - Cleanup method

#### 4. API Key Service (Optional but Recommended)

Create `apps/api/src/app/auth/api-key.service.ts`:

- `generateApiKey(userId: string): Promise<{ key: string; apiKey: ApiKey }>`
  - Generate random API key (32+ characters)
  - Hash and store in database
  - Return plain key once (for user to save)
- `validateApiKey(key: string): Promise<{ userId: string; apiKey: ApiKey } | null>`
- `revokeApiKey(keyId: string): Promise<void>`
- `listApiKeys(userId: string): Promise<ApiKey[]>`

#### 5. Update AppModule

- Import `AuthModule` into `AppModule`

### Frontend (Angular)

#### 6. Create Auth Service

Create `apps/web/src/app/shared/services/auth.service.ts`:

- `login(email: string, password: string): Observable<{ accessToken: string; refreshToken: string; user: User }>`
- `register(email: string, password: string): Observable<{ accessToken: string; refreshToken: string; user: User }>`
- `logout(): void` - Clear tokens and call logout endpoint
- `refreshToken(): Observable<{ accessToken: string }>`
- `isAuthenticated(): boolean` - Check if tokens exist and are valid
- `getCurrentUser(): User | null` - Get current user from stored data
- `getAccessToken(): string | null` - Get stored access token
- Store tokens in `localStorage` (or consider httpOnly cookies for production)
- Store user info in a signal or service state

#### 7. Create HTTP Interceptor

Create `apps/web/src/app/shared/interceptors/auth.interceptor.ts`:

- Intercept HTTP requests
- Add `Authorization: Bearer <token>` header if token exists
- Handle 401 errors and attempt token refresh
- Redirect to login if refresh fails

#### 8. Create Auth Guard

Create `apps/web/src/app/shared/guards/auth.guard.ts`:

- Implement `CanActivate`
- Check authentication status
- Redirect to `/login` if not authenticated

#### 9. Create Login Component

Create `apps/web/src/app/features/auth/login/login.component.ts`:

- Standalone component
- Reactive form with email and password fields
- Use Material form fields (`mat-form-field`, `matInput`)
- Call `AuthService.login()`
- Handle errors and display messages
- Redirect to home on success
- Loading state during submission

#### 10. Create Register Component

Create `apps/web/src/app/features/auth/register/register.component.ts`:

- Similar to login component
- Include password confirmation field
- Password strength validation (optional but recommended)

#### 11. Update Routes

Add auth routes to `apps/web/src/app/app.routes.ts`:

- `/login` - LoginComponent
- `/register` - RegisterComponent
- Protect admin routes with `canActivate: [AuthGuard]`

### Unit Tests

#### Backend Tests

Create test files with `.spec.ts` extension:

**auth.service.spec.ts**

- Test `register()` - success case, duplicate email error
- Test `login()` - success case, invalid credentials
- Test `refreshToken()` - success case, invalid token, expired token
- Test `logout()` - success case
- Mock PrismaService and bcrypt

**auth.controller.spec.ts**

- Test all endpoints with valid/invalid inputs
- Test authentication guards
- Mock AuthService

**jwt.strategy.spec.ts**

- Test token validation
- Test token extraction from header
- Test expired token handling

**guards/jwt-auth.guard.spec.ts**

- Test guard allows authenticated requests
- Test guard blocks unauthenticated requests

**guards/roles.guard.spec.ts**

- Test guard allows users with correct role
- Test guard blocks users without required role
- Test multiple roles requirement

**session.service.spec.ts**

- Test session creation
- Test session lookup
- Test session deletion
- Test expired session cleanup

#### Frontend Tests

Create test files with `.spec.ts` extension:

**auth.service.spec.ts**

- Test `login()` - success and error cases
- Test `register()` - success and error cases
- Test `logout()` - clears tokens
- Test `isAuthenticated()` - returns correct status
- Mock HttpClient

**auth.interceptor.spec.ts**

- Test adds Authorization header when token exists
- Test doesn't add header when no token
- Test handles 401 and refreshes token
- Mock HTTP requests

**auth.guard.spec.ts**

- Test allows navigation when authenticated
- Test redirects when not authenticated
- Mock AuthService and Router

**login.component.spec.ts**

- Test form validation
- Test submission calls AuthService
- Test error handling
- Test redirect on success
- Use TestBed with MaterialModule

**register.component.spec.ts**

- Similar to login component tests
- Test password confirmation matching

## Code Style & Conventions

### Backend

- Use NestJS dependency injection
- Use `@Injectable()` decorator for services
- Use `@Controller()` and `@Get()`, `@Post()` decorators
- Use `class-validator` for DTO validation
- Use `@ApiTags()`, `@ApiOperation()`, `@ApiResponse()` for Swagger docs
- Follow existing error handling patterns
- Use async/await, not Promises directly
- Return consistent response format: `{ data?, error?, traceId? }`

### Frontend

- Use standalone components only (no NgModules)
- Use Angular Signals for reactive state
- Use Reactive Forms (FormControl, FormGroup)
- Use Material UI components from `MaterialModule`
- Use `ChangeDetectionStrategy.OnPush`
- Use `inject()` function for dependency injection
- Follow existing component patterns

### Testing

- Use Jest for backend tests
- Use Jest for frontend tests (configured in project)
- Use `describe()`, `it()`, `expect()` structure
- Mock external dependencies
- Test both success and error cases
- Use `beforeEach()` for setup
- Follow AAA pattern (Arrange-Act-Assert)

## Environment Variables

Ensure these are in `.env`:

```
JWT_ACCESS_SECRET=your-secret-key-here
JWT_REFRESH_SECRET=your-refresh-secret-key-here
JWT_EXPIRES_IN=15m
JWT_REFRESH_EXPIRES_IN=7d
```

## Success Criteria

- [ ] Users can register with email and password
- [ ] Users can login and receive access/refresh tokens
- [ ] Protected routes require valid JWT token
- [ ] Role-based access control works
- [ ] Token refresh works
- [ ] Logout invalidates session
- [ ] All unit tests pass
- [ ] Swagger docs show auth endpoints
- [ ] Frontend login/register forms work
- [ ] Auth guard protects routes

## Notes

- Store refresh tokens securely (hashed in database)
- Consider token rotation for refresh tokens
- Add rate limiting to login/register endpoints (future enhancement)
- Consider adding email verification (future enhancement)
- API key authentication is optional but useful for programmatic access
