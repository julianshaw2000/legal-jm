# Step 6: Implement Embeddings & Indexing

## Context
You are implementing the embeddings generation and indexing system that enables semantic search and RAG functionality for Legal JM.

**Project Structure:**
- Python CLI: `apps/python/main.py`
- Embeddings: `apps/python/embeddings/`
- Chunking: `apps/python/chunking/`
- Indexing: `apps/python/indexing/`
- Database: PostgreSQL with pgvector extension

**Existing Setup:**
- Database has `Chunk` and `Embedding` tables
- `Embedding.vector` column uses `vector(1536)` (OpenAI embedding dimension)
- `rebuild-index` command skeleton exists

## Implementation Requirements

### 1. Embedding Service

#### Create Embedding Service
Create `apps/python/embeddings/embedding_service.py`:

**Methods:**
- `generate_embedding(text: str) -> List[float]`
  - Call OpenAI embeddings API (`text-embedding-ada-002` or `text-embedding-3-small`)
  - Handle API errors and retries
  - Return 1536-dimensional vector

- `generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]`
  - Batch processing for efficiency
  - Handle rate limits
  - Return list of vectors

**Configuration:**
- Use `OPENAI_API_KEY` from environment
- Support `AI_DRY_RUN` mode (return mock vectors)
- Configurable model name

### 2. Chunking Service

#### Create Chunking Service
Create `apps/python/chunking/chunking_service.py`:

**Methods:**
- `chunk_document(document_id: str, sections: List[Section]) -> List[Chunk]`
  - Split document into chunks
  - Strategy: by section, sliding window, or semantic boundaries
  - Preserve context (section ID, document ID)
  - Handle chunk size limits (token count ~800 tokens or ~3200 chars)
  - Return list of chunk objects

**Chunking Strategies:**
- **By Section**: Each section becomes a chunk (if under size limit)
- **Sliding Window**: Overlap chunks for better context
- **Semantic Boundaries**: Split at paragraph/sentence boundaries

### 3. Indexing Service

#### Create Indexing Service
Create `apps/python/indexing/indexing_service.py`:

**Methods:**
- `index_document(document_id: str) -> int`
  - Fetch document and sections from database
  - Generate chunks using ChunkingService
  - Generate embeddings for each chunk
  - Store chunks and embeddings in database
  - Return number of chunks indexed

- `rebuild_index(skip_existing: bool = False) -> dict`
  - Process all documents
  - Show progress bar
  - Handle errors gracefully
  - Return statistics (total documents, chunks, errors)

- `update_index(document_id: str) -> int`
  - Re-index a single document
  - Delete existing chunks/embeddings first
  - Return number of chunks indexed

### 4. Database Helpers

#### Create Database Helpers
Create `apps/python/db/embedding_helpers.py`:

**Functions:**
- `create_chunk(engine, document_id, section_id, index, text) -> str`
- `create_embedding(engine, chunk_id, vector) -> str`
- `get_document_sections(engine, document_id) -> List[Section]`
- `delete_chunks_for_document(engine, document_id) -> int`
- `vector_to_pgvector(vector: List[float]) -> str` - Convert to pgvector format

### 5. Update CLI Command

#### Enhance Rebuild Index Command
Update `apps/python/main.py`:

```python
from indexing.indexing_service import IndexingService
from rich.console import Console
from rich.progress import Progress

@app.command("rebuild-index")
def rebuild_index(
    skip_existing: bool = typer.Option(False, "--skip-existing", help="Skip documents that already have embeddings"),
    document_id: Optional[str] = typer.Option(None, "--document-id", help="Index specific document only")
) -> None:
    """Rebuild embeddings index."""
    load_dotenv()
    engine = get_engine()

    indexing_service = IndexingService(engine)

    if document_id:
        console.print(f"[cyan]Indexing document {document_id}...[/cyan]")
        count = indexing_service.update_index(document_id)
        console.print(f"[green]Indexed {count} chunks[/green]")
    else:
        console.print("[cyan]Rebuilding index for all documents...[/cyan]")
        stats = indexing_service.rebuild_index(skip_existing=skip_existing)
        console.print(f"[green]Completed: {stats['chunks_indexed']} chunks from {stats['documents_processed']} documents[/green]")
```

## Unit Tests

### Embedding Service Tests
**test_embedding_service.py**
- Test `generate_embedding()` - success case
- Test API error handling
- Test retry logic
- Test batch processing
- Test dry-run mode
- Mock OpenAI API

### Chunking Service Tests
**test_chunking_service.py**
- Test chunking by section
- Test chunking with size limits
- Test sliding window strategy
- Test chunk ordering
- Test context preservation

### Indexing Service Tests
**test_indexing_service.py**
- Test `index_document()` - success case
- Test `rebuild_index()` - processes all documents
- Test `update_index()` - updates existing
- Test error handling
- Mock database and embedding service

### Database Helper Tests
**test_embedding_helpers.py**
- Test chunk creation
- Test embedding creation
- Test vector conversion
- Test chunk deletion
- Mock database

## Code Style & Conventions

### Python
- Use type hints
- Use dataclasses for chunk objects
- Handle API rate limits gracefully
- Add progress indicators
- Use environment variables for configuration
- Follow PEP 8

### Testing
- Use pytest
- Mock external APIs
- Test error cases
- Test edge cases (empty text, very long text)

## Success Criteria
- [ ] Embeddings are generated correctly
- [ ] Chunking preserves context
- [ ] Indexing creates chunks and embeddings
- [ ] Rebuild index processes all documents
- [ ] Dry-run mode works
- [ ] Error handling works
- [ ] All unit tests pass
- [ ] Progress indicators work

## Notes
- Consider using `tiktoken` for accurate token counting
- Consider adding chunk overlap for better context
- Consider caching embeddings to avoid re-generating
- Add logging for debugging
- Consider adding embedding similarity search helper functions

