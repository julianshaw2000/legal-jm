"""Ingestion modules for scraping and parsing legal documents."""

from .normalizer import DocumentNormalizer
from .parser import DocumentParser

__all__ = ["DocumentNormalizer", "DocumentParser"]

