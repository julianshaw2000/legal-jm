# Step 7: Implement RAG API (Ask Functionality)

## Context
You are implementing the RAG (Retrieval-Augmented Generation) API that enables users to ask questions and get answers based on the legal document corpus.

**Project Structure:**
- Backend: NestJS API in `apps/api/src/app/rag/`
- Database: PostgreSQL with pgvector for vector similarity search
- AI Provider: OpenAI (with abstraction for other providers)

**Existing Setup:**
- Embeddings should be generated (Step 6)
- `Chunk` and `Embedding` tables exist
- Auth system is implemented (Step 1)

## Implementation Requirements

### 1. AI Provider Abstraction

#### Create Provider Interface
Create `apps/api/src/app/rag/providers/ai-provider.interface.ts`:

```typescript
export interface EmbeddingResponse {
  embedding: number[];
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  content: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
  };
}

export interface AIProvider {
  generateEmbedding(text: string): Promise<number[]>;
  chat(messages: ChatMessage[]): Promise<ChatResponse>;
}
```

#### Create OpenAI Provider
Create `apps/api/src/app/rag/providers/openai-provider.ts`:

**Methods:**
- `generateEmbedding(text: string): Promise<number[]>`
  - Call OpenAI embeddings API
  - Handle errors and retries
  - Return vector

- `chat(messages: ChatMessage[]): Promise<ChatResponse>`
  - Call OpenAI chat API (gpt-4 or gpt-3.5-turbo)
  - Handle streaming (optional)
  - Return response

#### Create Dry-Run Provider
Create `apps/api/src/app/rag/providers/dry-run-provider.ts`:

**Methods:**
- Return mock embeddings (random or zero vector)
- Return mock chat responses
- Log requests for debugging

#### Create Provider Factory
Create `apps/api/src/app/rag/providers/provider.factory.ts`:

**Methods:**
- `createProvider(): AIProvider`
  - Check `AI_PROVIDER` env var
  - Check `AI_DRY_RUN` env var
  - Return appropriate provider

### 2. RAG Service

#### Create RAG Service
Create `apps/api/src/app/rag/rag.service.ts`:

**Methods:**
- `ask(question: string, options?: AskOptions): Promise<AskResponse>`
  - Generate embedding for question
  - Vector similarity search (top-k chunks)
  - Build context from chunks
  - Call LLM with question + context
  - Log Q&A to `QALog` table
  - Return answer with sources

- `similaritySearch(embedding: number[], limit: number = 5): Promise<ChunkWithSimilarity[]>`
  - Use pgvector cosine similarity
  - Query: `SELECT ... ORDER BY embedding <=> $1 LIMIT $2`
  - Return chunks with similarity scores

- `buildContext(chunks: ChunkWithSimilarity[]): string`
  - Format chunks into context string
  - Include document titles, section headings
  - Limit total context length

**Ask Options:**
```typescript
interface AskOptions {
  maxChunks?: number;
  minSimilarity?: number;
  model?: string;
}
```

### 3. RAG Controller

#### Create RAG Controller
Create `apps/api/src/app/rag/rag.controller.ts`:

**Endpoints:**
- `POST /api/ask`
  - Body: `{ question: string, options?: AskOptions }`
  - Protected: `@UseGuards(JwtAuthGuard)`
  - Returns: `AskResponse`

- `GET /api/ask/history`
  - Query params: `page?`, `limit?`
  - Protected: `@UseGuards(JwtAuthGuard)`
  - Returns: Paginated Q&A history

- `POST /api/ask/:id/feedback`
  - Body: `{ rating: number, comment?: string }`
  - Protected: `@UseGuards(JwtAuthGuard)`
  - Returns: Success message

### 4. RAG Module

#### Create RAG Module
Create `apps/api/src/app/rag/rag.module.ts`:
- Register `RAGController`, `RAGService`
- Import `AuthModule`
- Provide `AIProvider` via factory

### 5. DTOs

#### Create DTOs
Create `apps/api/src/app/rag/dto/`:

**ask-question.dto.ts:**
```typescript
- question: string (required, min 10, max 1000)
- maxChunks?: number (optional, default 5, min 1, max 20)
- minSimilarity?: number (optional, default 0.7)
```

**ask-response.dto.ts:**
```typescript
- answer: string
- sources: SourceChunk[]
- qaLogId: string
- dryRun: boolean
```

**feedback.dto.ts:**
```typescript
- rating: number (required, min 1, max 5)
- comment?: string (optional, max 500)
```

### 6. Database Queries

#### Vector Similarity Search
Use Prisma raw query or SQL:

```typescript
// Using Prisma raw query
const chunks = await prisma.$queryRaw<ChunkWithSimilarity[]>`
  SELECT
    c.*,
    e.vector,
    1 - (e.vector <=> ${embedding}::vector) as similarity
  FROM "Chunk" c
  JOIN "Embedding" e ON e."chunkId" = c.id
  WHERE e.vector IS NOT NULL
  ORDER BY e.vector <=> ${embedding}::vector
  LIMIT ${limit}
`;
```

## Unit Tests

### AI Provider Tests
**openai-provider.spec.ts**
- Test `generateEmbedding()` - success and error
- Test `chat()` - success and error
- Test retry logic
- Mock OpenAI SDK

**dry-run-provider.spec.ts**
- Test returns mock data
- Test logging

**provider.factory.spec.ts**
- Test creates correct provider based on env

### RAG Service Tests
**rag.service.spec.ts**
- Test `ask()` - full flow
- Test `similaritySearch()` - returns correct chunks
- Test `buildContext()` - formats correctly
- Test error handling
- Mock AI provider and Prisma

### RAG Controller Tests
**rag.controller.spec.ts**
- Test all endpoints
- Test authentication
- Test validation
- Mock RAG service

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
- Mock external APIs
- Test success and error cases
- Test edge cases

## Success Criteria
- [ ] Questions generate embeddings
- [ ] Vector similarity search works
- [ ] LLM generates answers with context
- [ ] Q&A history is logged
- [ ] Feedback can be submitted
- [ ] Dry-run mode works
- [ ] All unit tests pass
- [ ] Swagger docs are complete

## Notes
- Consider adding streaming responses for better UX
- Consider caching common questions
- Consider adding answer quality scoring
- Monitor token usage and costs
- Consider adding answer sources highlighting

