"""
🔍 SCJN Integration Module
==========================
Multi-strategy jurisprudence data extraction:
- Puppeteer: Real-time search (on-demand)
- Selenium: Weekly bulk crawl (scheduled)
- ChromaDB: Vector storage and RAG
"""

from .puppeteer_scout import SCJNPuppeteerScout
from .crawler import SCJNCrawler
from .models import TesisResult, SearchFilters

__all__ = [
    'SCJNPuppeteerScout',
    'SCJNCrawler',
    'TesisResult',
    'SearchFilters'
]
