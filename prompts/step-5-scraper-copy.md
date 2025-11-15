# Step 5: Implement Python Scraper

## Context
You are implementing the Python scraper system that will populate the Legal JM database with legal documents from various sources. This is a critical component for building the corpus.

**Project Structure:**
- Python CLI: `apps/python/main.py` (Typer-based)
- Scrapers: `apps/python/scrapers/`
- Parsers: `apps/python/parsers/`
- Database: PostgreSQL via SQLAlchemy (already configured)

**Existing Setup:**
- `verify-db` command works
- `scrape` command skeleton exists
- Database connection via `get_engine()` function
- Dependencies: `httpx`, `beautifulsoup4`, `pdfplumber`, `SQLAlchemy`, `psycopg2-binary`

## Implementation Requirements

### 1. Scraper Infrastructure

#### Create Base Scraper Class
Create `apps/python/scrapers/base_scraper.py`:

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.engine import Engine

class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(self, engine: Engine):
        self.engine = engine

    @abstractmethod
    def scrape(self, **kwargs) -> int:
        """
        Main scraping method. Returns number of documents scraped.
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of the source being scraped."""
        pass
```

#### Create Scraper Registry
Create `apps/python/scrapers/scraper_registry.py`:

```python
from typing import Dict, Type
from scrapers.base_scraper import BaseScraper

class ScraperRegistry:
    """Registry for all available scrapers."""

    _scrapers: Dict[str, Type[BaseScraper]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a scraper."""
        def decorator(scraper_class: Type[BaseScraper]):
            cls._scrapers[name] = scraper_class
            return scraper_class
        return decorator

    @classmethod
    def get_scraper(cls, name: str) -> Type[BaseScraper]:
        """Get a scraper class by name."""
        if name not in cls._scrapers:
            raise ValueError(f"Scraper '{name}' not found")
        return cls._scrapers[name]

    @classmethod
    def list_scrapers(cls) -> List[str]:
        """List all registered scraper names."""
        return list(cls._scrapers.keys())
```

#### Create Common Utilities
Create `apps/python/scrapers/utils.py`:

```python
import httpx
from typing import Optional
from rich.console import Console

console = Console()

def fetch_url(url: str, timeout: int = 30) -> Optional[bytes]:
    """Fetch URL content with error handling."""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.content
    except httpx.HTTPError as e:
        console.print(f"[red]Error fetching {url}:[/red] {e}")
        return None

def normalize_text(text: str) -> str:
    """Normalize text (remove extra whitespace, etc.)."""
    import re
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

### 2. Document Processing

#### Create PDF Parser
Create `apps/python/parsers/pdf_parser.py`:

```python
import pdfplumber
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ParsedSection:
    heading: Optional[str]
    text: str
    index: int

class PDFParser:
    """Parser for PDF legal documents."""

    def parse(self, pdf_content: bytes) -> Dict[str, any]:
        """
        Parse PDF content.
        Returns: {
            'title': str,
            'sections': List[ParsedSection],
            'metadata': Dict
        }
        """
        # Implementation:
        # 1. Open PDF with pdfplumber
        # 2. Extract text page by page
        # 3. Identify sections/headings (heuristics or patterns)
        # 4. Extract metadata if available
        # 5. Return structured data
        pass

    def _identify_headings(self, text: str) -> List[tuple]:
        """Identify section headings in text."""
        # Use patterns like:
        # - "Section 1", "Section 2", etc.
        # - Numbered lists
        # - Bold/large text (if PDF structure available)
        pass
```

#### Create HTML Parser
Create `apps/python/parsers/html_parser.py`:

```python
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from parsers.pdf_parser import ParsedSection

class HTMLParser:
    """Parser for HTML legal documents."""

    def parse(self, html_content: bytes, url: Optional[str] = None) -> Dict[str, any]:
        """
        Parse HTML content.
        Returns: {
            'title': str,
            'sections': List[ParsedSection],
            'metadata': Dict
        }
        """
        # Implementation:
        # 1. Parse HTML with BeautifulSoup
        # 2. Extract title from <title> or <h1>
        # 3. Identify sections (look for <section>, <div> with classes, headings)
        # 4. Extract text from sections
        # 5. Clean HTML tags
        # 6. Return structured data
        pass

    def _extract_sections(self, soup: BeautifulSoup) -> List[ParsedSection]:
        """Extract sections from parsed HTML."""
        # Look for:
        # - <section> tags
        # - <h2>, <h3> headings followed by content
        # - Specific CSS classes/IDs
        pass

    def _clean_text(self, element) -> str:
        """Extract and clean text from HTML element."""
        # Remove script, style tags
        # Get text content
        # Normalize whitespace
        pass
```

### 3. Database Models & Helpers

#### Create Database Models
Create `apps/python/db/models.py`:

```python
from sqlalchemy import (
    Column, String, DateTime, Integer, Text, ForeignKey,
    create_engine, MetaData, Table
)
from sqlalchemy.engine import Engine
from datetime import datetime
from typing import Optional

# Define tables matching Prisma schema
# Use SQLAlchemy Core (not ORM) for simplicity

def get_or_create_source(engine: Engine, name: str, url: Optional[str] = None) -> str:
    """Get or create a Source record. Returns source ID."""
    # Implementation:
    # 1. Check if source exists
    # 2. Create if not exists
    # 3. Return source ID
    pass

def create_document(
    engine: Engine,
    title: str,
    doc_type: str,
    source_id: Optional[str] = None,
    published_at: Optional[datetime] = None
) -> str:
    """Create a Document record. Returns document ID."""
    # Implementation:
    # 1. Insert into Document table
    # 2. Return document ID
    pass

def create_section(
    engine: Engine,
    document_id: str,
    index: int,
    text: str,
    heading: Optional[str] = None
) -> str:
    """Create a Section record. Returns section ID."""
    # Implementation:
    # 1. Insert into Section table
    # 2. Return section ID
    pass
```

### 4. Acts Scraper

#### Create Acts Scraper
Create `apps/python/scrapers/acts_scraper.py`:

```python
from scrapers.base_scraper import BaseScraper
from scrapers.scraper_registry import ScraperRegistry
from scrapers.utils import fetch_url
from parsers.html_parser import HTMLParser
from parsers.pdf_parser import PDFParser
from db.models import get_or_create_source, create_document, create_section
from rich.console import Console
from rich.progress import Progress, TaskID
from typing import List
import re

console = Console()

@ScraperRegistry.register("acts")
class ActsScraper(BaseScraper):
    """Scraper for Jamaican Acts of Parliament."""

    # Source URLs - these should be actual Jamaican legal sources
    SOURCE_URLS = [
        "https://example.com/jamaican-acts",  # Replace with actual URLs
        # Add more sources
    ]

    def get_source_name(self) -> str:
        return "Jamaican Acts of Parliament"

    def scrape(self, **kwargs) -> int:
        """
        Scrape Acts from configured sources.
        Returns number of documents scraped.
        """
        source_id = get_or_create_source(
            self.engine,
            self.get_source_name(),
            url=self.SOURCE_URLS[0] if self.SOURCE_URLS else None
        )

        html_parser = HTMLParser()
        pdf_parser = PDFParser()
        documents_scraped = 0

        with Progress() as progress:
            task = progress.add_task(
                f"Scraping {self.get_source_name()}...",
                total=len(self.SOURCE_URLS)
            )

            for url in self.SOURCE_URLS:
                try:
                    content = fetch_url(url)
                    if not content:
                        continue

                    # Determine if HTML or PDF
                    if url.endswith('.pdf') or content.startswith(b'%PDF'):
                        parsed = pdf_parser.parse(content)
                    else:
                        parsed = html_parser.parse(content, url)

                    if parsed:
                        doc_id = create_document(
                            self.engine,
                            title=parsed['title'],
                            doc_type='ACT',
                            source_id=source_id,
                            published_at=parsed.get('metadata', {}).get('published_at')
                        )

                        # Create sections
                        for idx, section in enumerate(parsed['sections']):
                            create_section(
                                self.engine,
                                document_id=doc_id,
                                index=idx,
                                text=section.text,
                                heading=section.heading
                            )

                        documents_scraped += 1
                        console.print(f"[green]Scraped:[/green] {parsed['title']}")

                except Exception as e:
                    console.print(f"[red]Error scraping {url}:[/red] {e}")

                progress.update(task, advance=1)

        return documents_scraped
```

### 5. Regulations Scraper

#### Create Regulations Scraper
Create `apps/python/scrapers/regulations_scraper.py`:

```python
from scrapers.base_scraper import BaseScraper
from scrapers.scraper_registry import ScraperRegistry
# Similar structure to ActsScraper
# Adapt for regulations-specific sources and structure

@ScraperRegistry.register("regulations")
class RegulationsScraper(BaseScraper):
    """Scraper for Jamaican Regulations."""

    def get_source_name(self) -> str:
        return "Jamaican Regulations"

    def scrape(self, **kwargs) -> int:
        # Similar implementation to ActsScraper
        # Adapt for regulations-specific parsing
        pass
```

### 6. Cases Scraper

#### Create Cases Scraper
Create `apps/python/scrapers/cases_scraper.py`:

```python
from scrapers.base_scraper import BaseScraper
from scrapers.scraper_registry import ScraperRegistry
from db.models import create_case_law  # Need to add this helper

@ScraperRegistry.register("cases")
class CasesScraper(BaseScraper):
    """Scraper for Case Law."""

    def get_source_name(self) -> str:
        return "Jamaican Case Law"

    def scrape(self, **kwargs) -> int:
        # Implementation for case law scraping
        # Create CaseLaw records instead of Document records
        # Extract: title, court, decidedAt, citation
        pass
```

### 7. Update CLI Command

#### Enhance Scrape Command
Update `apps/python/main.py`:

```python
from scrapers.scraper_registry import ScraperRegistry
from scrapers.base_scraper import BaseScraper
from rich.console import Console

console = Console()

@app.command("scrape")
def scrape(
    which: str = typer.Argument(..., help="acts|cases|regulations|all")
) -> None:
    """Scrape legal sources and populate the database."""
    load_dotenv()
    engine = get_engine()

    if which == "all":
        scrapers_to_run = ScraperRegistry.list_scrapers()
    else:
        scrapers_to_run = [which]

    total_documents = 0

    for scraper_name in scrapers_to_run:
        try:
            scraper_class = ScraperRegistry.get_scraper(scraper_name)
            scraper = scraper_class(engine)

            console.print(f"[cyan]Starting {scraper.get_source_name()}...[/cyan]")
            count = scraper.scrape()
            total_documents += count
            console.print(f"[green]Completed: {count} documents[/green]")

        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
        except Exception as e:
            console.print(f"[red]Error scraping {scraper_name}:[/red] {e}")

    console.print(f"[green]Total documents scraped: {total_documents}[/green]")
```

### 8. Error Handling & Retries

#### Add Retry Logic
Create `apps/python/scrapers/retry.py`:

```python
from functools import wraps
from typing import Callable, TypeVar, Any
import time

T = TypeVar('T')

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for retrying functions."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise last_exception
            raise last_exception
        return wrapper
    return decorator
```

## Unit Tests

### Base Scraper Tests
**test_base_scraper.py**
- Test abstract class cannot be instantiated
- Test scraper registry registration
- Test scraper lookup

### PDF Parser Tests
**test_pdf_parser.py**
- Test PDF parsing with sample PDF
- Test section identification
- Test heading extraction
- Test metadata extraction
- Mock pdfplumber

### HTML Parser Tests
**test_html_parser.py**
- Test HTML parsing with sample HTML
- Test section extraction
- Test text cleaning
- Test heading identification
- Mock BeautifulSoup

### Acts Scraper Tests
**test_acts_scraper.py**
- Test scraper initialization
- Test source creation
- Test document creation
- Test section creation
- Mock HTTP requests and database

### Utils Tests
**test_utils.py**
- Test URL fetching (success and error)
- Test text normalization
- Mock httpx

### Database Helper Tests
**test_db_models.py**
- Test source get_or_create
- Test document creation
- Test section creation
- Mock database engine

## Code Style & Conventions

### Python
- Use type hints for all functions
- Use dataclasses for data structures
- Use f-strings for string formatting
- Follow PEP 8 style guide
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Add docstrings to all public functions/classes
- Use `uv` for dependency management

### Testing
- Use `pytest` (add to `pyproject.toml`)
- Use `pytest-mock` for mocking
- Test success and error cases
- Test edge cases (empty content, malformed HTML/PDF)
- Use `describe()` equivalent: organize tests in classes or modules

## Success Criteria
- [ ] Base scraper infrastructure works
- [ ] PDF parser extracts text and sections
- [ ] HTML parser extracts text and sections
- [ ] Acts scraper creates documents and sections
- [ ] Regulations scraper works
- [ ] Cases scraper works
- [ ] CLI command works for all scraper types
- [ ] Error handling and retries work
- [ ] All unit tests pass
- [ ] Progress indicators work

## Notes
- Replace placeholder URLs with actual Jamaican legal document sources
- Consider rate limiting to avoid overwhelming sources
- Consider caching downloaded content to avoid re-downloading
- Add logging for debugging
- Consider adding dry-run mode that doesn't write to database
- Handle duplicate documents (check if document already exists)
- Consider adding metadata extraction (publication dates, etc.)
- For production, consider using a job queue (Celery) for async processing

