# Step 4: Implement Frontend Components (UI Implementation)

## Context
You are implementing the frontend Angular components that provide the user interface for Legal JM. These components will use the services created in Step 3 to interact with the API.

**Project Structure:**
- Frontend: Angular standalone components in `apps/web/src/app/features/`
- Services: Available in `apps/web/src/app/shared/services/`
- Material UI: Configured via `MaterialModule`

**Existing Setup:**
- Routes are configured in `app.routes.ts`
- Component skeletons exist but are mostly placeholders
- Material UI is available
- Services should be implemented (Step 3)

## Implementation Requirements

### 1. Browse Component

#### Enhance Browse Component
Update `apps/web/src/app/features/browse/browse.component.ts`:

**Features:**
- Display paginated list of documents
- Filter by document type (ACT, REGULATION, CASE, OTHER)
- Filter by date range (published date)
- Search by title/keywords
- Sort by title, date, creation date
- Click document to navigate to detail page
- Loading state during data fetch
- Error handling and display
- Empty state when no documents

**UI Elements:**
- Material table or cards for document list
- Material select for type filter
- Material date pickers for date range
- Material input for search
- Material paginator
- Material progress spinner for loading
- Material snackbar for errors

**Implementation:**
- Use `DocumentsService` to fetch documents
- Use signals for reactive state
- Use reactive forms for filters
- Implement pagination
- Handle loading and error states
- Use `ChangeDetectionStrategy.OnPush`

**Template Structure:**
```html
<div class="browse-container">
  <h2>Browse Documents</h2>

  <!-- Filters -->
  <mat-card class="filters">
    <mat-form-field>
      <mat-label>Type</mat-label>
      <mat-select [formControl]="typeFilter">
        <mat-option value="">All</mat-option>
        <mat-option value="ACT">Acts</mat-option>
        <!-- ... -->
      </mat-select>
    </mat-form-field>

    <!-- Search, date filters, etc. -->
  </mat-card>

  <!-- Document List -->
  @if (loading()) {
    <mat-spinner></mat-spinner>
  } @else if (error()) {
    <mat-error>{{ error() }}</mat-error>
  } @else if (documents().length === 0) {
    <p>No documents found</p>
  } @else {
    <mat-table [dataSource]="documents()">
      <!-- Columns -->
    </mat-table>

    <mat-paginator
      [length]="total()"
      [pageSize]="pageSize()"
      (page)="onPageChange($event)">
    </mat-paginator>
  }
</div>
```

### 2. Document Component

#### Enhance Document Component
Update `apps/web/src/app/features/document/document.component.ts`:

**Features:**
- Display document details (title, type, published date, source)
- Display all sections with headings
- Display amendments if any
- Loading state
- Error handling (404, network errors)
- Edit button (if user has EDITOR role)
- Back to browse button

**Implementation:**
- Get document ID from route params
- Use `DocumentsService.getDocument(id)`
- Use signals for document state
- Handle route param changes (if navigating between documents)
- Check user role for edit button visibility

**Template Structure:**
```html
<div class="document-container">
  @if (loading()) {
    <mat-spinner></mat-spinner>
  } @else if (error()) {
    <mat-error>{{ error() }}</mat-error>
  } @else if (document(); as doc) {
    <mat-card>
      <mat-card-header>
        <mat-card-title>{{ doc.title }}</mat-card-title>
        <mat-card-subtitle>
          {{ doc.type }} • Published: {{ doc.publishedAt | date }}
        </mat-card-subtitle>
      </mat-card-header>

      <mat-card-content>
        @for (section of doc.sections; track section.id) {
          <section>
            @if (section.heading) {
              <h3>{{ section.heading }}</h3>
            }
            <p>{{ section.text }}</p>
          </section>
        }
      </mat-card-content>

      @if (canEdit()) {
        <mat-card-actions>
          <button mat-button (click)="edit()">Edit</button>
        </mat-card-actions>
      }
    </mat-card>
  }
</div>
```

### 3. Ask Component

#### Enhance Ask Component
Update `apps/web/src/app/features/ask/ask.component.ts`:

**Features:**
- Question input form
- Submit button (disabled when invalid)
- Display answer with loading state
- Display source chunks/references
- Feedback form (thumbs up/down + comment)
- Q&A history below
- Handle dry-run mode (show indicator)

**Implementation:**
- Use reactive form for question input
- Use `AskService.askQuestion()`
- Use signals for answer and history
- Display sources with links to documents
- Submit feedback after answer
- Load history on component init

**Template Structure:**
```html
<div class="ask-container">
  <h2>Ask a Question</h2>

  <form [formGroup]="questionForm" (ngSubmit)="submit()">
    <mat-form-field appearance="outline" class="full-width">
      <mat-label>Your question</mat-label>
      <textarea matInput formControlName="question" rows="4"></textarea>
      <mat-error>Question is required</mat-error>
    </mat-form-field>

    <button
      mat-raised-button
      color="primary"
      type="submit"
      [disabled]="questionForm.invalid || loading()">
      Ask
    </button>
  </form>

  @if (loading()) {
    <mat-spinner></mat-spinner>
  }

  @if (answer(); as ans) {
    <mat-card class="answer-card">
      <mat-card-header>
        <mat-card-title>Answer</mat-card-title>
        @if (ans.dryRun) {
          <mat-chip>Dry Run Mode</mat-chip>
        }
      </mat-card-header>
      <mat-card-content>
        <p>{{ ans.answer }}</p>

        @if (ans.sources.length > 0) {
          <h4>Sources</h4>
          @for (source of ans.sources; track source.chunkId) {
            <mat-card class="source-card">
              <mat-card-title>
                <a [routerLink]="['/document', source.documentId]">
                  {{ source.documentTitle }}
                </a>
              </mat-card-title>
              @if (source.sectionHeading) {
                <mat-card-subtitle>{{ source.sectionHeading }}</mat-card-subtitle>
              }
              <mat-card-content>
                <p>{{ source.text }}</p>
              </mat-card-content>
            </mat-card>
          }
        }
      </mat-card-content>

      <mat-card-actions>
        <button mat-icon-button (click)="submitFeedback(ans.qaLogId, 1)">
          <mat-icon>thumb_up</mat-icon>
        </button>
        <button mat-icon-button (click)="submitFeedback(ans.qaLogId, -1)">
          <mat-icon>thumb_down</mat-icon>
        </button>
      </mat-card-actions>
    </mat-card>
  }

  <!-- Q&A History -->
  <mat-card class="history-card">
    <mat-card-header>
      <mat-card-title>Recent Questions</mat-card-title>
    </mat-card-header>
    <mat-card-content>
      @for (item of history(); track item.id) {
        <div class="history-item">
          <strong>Q:</strong> {{ item.question }}<br>
          @if (item.answer) {
            <strong>A:</strong> {{ item.answer }}
          }
        </div>
      }
    </mat-card-content>
  </mat-card>
</div>
```

### 4. Ingest Component

#### Enhance Ingest Component
Update `apps/web/src/app/features/ingest/ingest.component.ts`:

**Features:**
- Form to trigger ingestion (source URL, document type)
- File upload option (if supporting PDF uploads)
- List of ingestion jobs with status
- Real-time status updates (polling)
- Error display for failed jobs
- Cancel job option (if supported by API)

**Implementation:**
- Use reactive form for ingestion form
- Use `IngestService` for all operations
- Poll job status every few seconds
- Display jobs in Material table
- Show status with color coding (pending, processing, completed, failed)

**Template Structure:**
```html
<div class="ingest-container">
  <h2>Ingest Documents</h2>

  <mat-card>
    <mat-card-header>
      <mat-card-title>Trigger Ingestion</mat-card-title>
    </mat-card-header>
    <mat-card-content>
      <form [formGroup]="ingestForm" (ngSubmit)="submit()">
        <mat-form-field>
          <mat-label>Source URL</mat-label>
          <input matInput formControlName="source" />
        </mat-form-field>

        <mat-form-field>
          <mat-label>Document Type</mat-label>
          <mat-select formControlName="type">
            <mat-option value="ACT">Act</mat-option>
            <!-- ... -->
          </mat-select>
        </mat-form-field>

        <button mat-raised-button type="submit" [disabled]="ingestForm.invalid">
          Start Ingestion
        </button>
      </form>
    </mat-card-content>
  </mat-card>

  <mat-card>
    <mat-card-header>
      <mat-card-title>Ingestion Jobs</mat-card-title>
    </mat-card-header>
    <mat-card-content>
      <mat-table [dataSource]="jobs()">
        <ng-container matColumnDef="source">
          <mat-header-cell *matHeaderCellDef>Source</mat-header-cell>
          <mat-cell *matCellDef="let job">{{ job.source }}</mat-cell>
        </ng-container>

        <ng-container matColumnDef="status">
          <mat-header-cell *matHeaderCellDef>Status</mat-header-cell>
          <mat-cell *matCellDef="let job">
            <mat-chip [color]="getStatusColor(job.status)">
              {{ job.status }}
            </mat-chip>
          </mat-cell>
        </ng-container>

        <!-- More columns -->

        <mat-header-row *matHeaderRowDef="displayedColumns"></mat-header-row>
        <mat-row *matRowDef="let row; columns: displayedColumns"></mat-row>
      </mat-table>
    </mat-card-content>
  </mat-card>
</div>
```

### 5. Admin Users Component

#### Enhance Admin Users Component
Update `apps/web/src/app/features/admin-users/admin-users.component.ts`:

**Features:**
- Table of all users
- Role dropdown/selector for each user
- Assign to organization functionality
- Search/filter users
- Pagination
- Loading and error states

**Implementation:**
- Use `UsersService` for all operations
- Check if current user is ADMIN (use AuthService)
- Use Material table for user list
- Implement role update with confirmation
- Handle errors gracefully

**Template Structure:**
```html
<div class="admin-users-container">
  <h2>User Management</h2>

  <mat-form-field>
    <mat-label>Search</mat-label>
    <input matInput (input)="onSearch($event)" />
  </mat-form-field>

  <mat-table [dataSource]="users()">
    <ng-container matColumnDef="email">
      <mat-header-cell *matHeaderCellDef>Email</mat-header-cell>
      <mat-cell *matCellDef="let user">{{ user.email }}</mat-cell>
    </ng-container>

    <ng-container matColumnDef="role">
      <mat-header-cell *matHeaderCellDef>Role</mat-header-cell>
      <mat-cell *matCellDef="let user">
        <mat-select [value]="user.role" (selectionChange)="updateRole(user.id, $event.value)">
          <mat-option value="VIEWER">Viewer</mat-option>
          <mat-option value="EDITOR">Editor</mat-option>
          <!-- ... -->
        </mat-select>
      </mat-cell>
    </ng-container>

    <!-- More columns -->

    <mat-header-row *matHeaderRowDef="displayedColumns"></mat-header-row>
    <mat-row *matRowDef="let row; columns: displayedColumns"></mat-row>
  </mat-table>

  <mat-paginator
    [length]="total()"
    [pageSize]="pageSize()"
    (page)="onPageChange($event)">
  </mat-paginator>
</div>
```

### 6. Shared Styles

#### Update Global Styles
Add common styles to `apps/web/src/styles.scss`:
- Container padding
- Card spacing
- Form field widths
- Responsive breakpoints
- Loading spinner centering

## Unit Tests

### Browse Component Tests
**browse.component.spec.ts**
- Test component initialization
- Test filter changes trigger API calls
- Test pagination
- Test document click navigation
- Test loading and error states
- Mock DocumentsService and Router

### Document Component Tests
**document.component.spec.ts**
- Test document loading from route param
- Test 404 handling
- Test edit button visibility based on role
- Test section rendering
- Mock DocumentsService, ActivatedRoute, AuthService

### Ask Component Tests
**ask.component.spec.ts**
- Test form validation
- Test question submission
- Test answer display
- Test feedback submission
- Test history loading
- Mock AskService

### Ingest Component Tests
**ingest.component.spec.ts**
- Test form submission
- Test job list display
- Test status polling
- Test error handling
- Mock IngestService

### Admin Users Component Tests
**admin-users.component.spec.ts**
- Test user list display
- Test role update
- Test search functionality
- Test pagination
- Test admin access check
- Mock UsersService and AuthService

## Code Style & Conventions

### Frontend
- Use standalone components only
- Use Angular Signals for reactive state
- Use Reactive Forms (FormControl, FormGroup)
- Use Material UI components
- Use `ChangeDetectionStrategy.OnPush`
- Use `inject()` for dependency injection
- Use `@if`, `@for` control flow syntax
- Handle loading and error states
- Use proper TypeScript types
- Follow existing component patterns

### Testing
- Use Jest
- Use TestBed for component testing
- Mock services
- Test user interactions
- Test error scenarios
- Use `describe()`, `it()`, `expect()` structure

## Success Criteria
- [ ] All components are fully functional
- [ ] Components use services correctly
- [ ] Loading and error states are handled
- [ ] UI is responsive and accessible
- [ ] All components have unit tests
- [ ] Material UI is used consistently
- [ ] Forms are validated properly
- [ ] Navigation works correctly
- [ ] Role-based UI elements work

## Notes
- Consider adding skeleton loaders instead of spinners for better UX
- Consider implementing virtual scrolling for long lists
- Consider adding keyboard shortcuts for common actions
- Ensure all interactive elements are accessible (ARIA labels, keyboard navigation)
- Consider adding tooltips for better UX
- Use consistent spacing and typography

