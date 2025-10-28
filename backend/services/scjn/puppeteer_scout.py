"""
🎯 SCJN Puppeteer Scout
=======================
Real-time jurisprudence search using Puppeteer
- Fast on-demand searches
- Dynamic scraping
- Bypass rate limits with smart delays
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional
import json

logger = logging.getLogger(__name__)


class SCJNPuppeteerScout:
    """
    Real-time SCJN searcher using Puppeteer via pyppeteer
    Performs searches on-demand and extracts results
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Args:
            headless: Run browser without GUI
            timeout: Timeout per operation in seconds
        """
        self.base_url = "https://bj.scjn.gob.mx"
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.page = None
    
    async def connect(self):
        """Initialize browser connection"""
        try:
            from pyppeteer import launch
            self.browser = await launch(
                headless=self.headless,
                executablePath=None,  # Use system chrome
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',  # Avoid memory issues
                ]
            )
            self.page = await self.browser.newPage()
            self.page.setDefaultTimeout(self.timeout * 1000)
            logger.info("✅ Puppeteer browser connected")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect browser: {e}")
            return False
    
    async def disconnect(self):
        """Close browser connection"""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("✅ Browser disconnected")
        except Exception as e:
            logger.error(f"❌ Error disconnecting: {e}")
    
    async def search_tesis(
        self,
        query: str,
        materia: Optional[str] = None,
        sala: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 20
    ) -> List[dict]:
        """
        Search tesis with filters
        
        Args:
            query: Search query (supports SCJN syntax)
            materia: Matter (Civil, Penal, Laboral, etc)
            sala: Court (Primera, Segunda, Pleno)
            year: Publication year
            limit: Max results to return
        
        Returns:
            List of tesis results
        
        Example:
            results = await scout.search_tesis(
                query="amparo laboral derecho a la huelga",
                materia="Laboral",
                sala="Primera",
                year=2023
            )
        """
        
        try:
            if not self.browser:
                await self.connect()
            
            # 1. Navigate to SCJN
            await self.page.goto(self.base_url)
            await asyncio.sleep(2)
            
            # 2. Click on "Tesis" section
            logger.info(f"🔍 Searching: {query}")
            await self.page.waitForSelector('[data-source="tesis"]')
            await self.page.click('[data-source="tesis"]')
            await asyncio.sleep(1)
            
            # 3. Clear and type query
            search_input = await self.page.querySelector('.search-input')
            await search_input.focus()
            await self.page.keyboard.press('Control', 'KeyA')
            await self.page.type('.search-input', query, {'delay': 50})
            
            # 4. Apply filters if provided
            if materia:
                await self._select_filter('materia', materia)
            if sala:
                await self._select_filter('sala', sala)
            if year:
                await self._select_filter('year', str(year))
            
            # 5. Execute search
            await self.page.click('.btn-search, [type="submit"]')
            await asyncio.sleep(3)
            
            # 6. Extract results
            results = await self._extract_results(limit)
            
            logger.info(f"✅ Found {len(results)} tesis")
            return results
        
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []
    
    async def _select_filter(self, filter_name: str, value: str):
        """Select a dropdown filter"""
        try:
            selector = f'select[name="{filter_name}"]'
            await self.page.waitForSelector(selector)
            await self.page.select(selector, value)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"⚠️ Could not select {filter_name}={value}: {e}")
    
    async def _extract_results(self, limit: int) -> List[dict]:
        """Extract search results from current page"""
        
        extraction_script = f"""
        () => {{
            const results = [];
            const items = document.querySelectorAll('.result-item, [class*="resultado"]');
            
            for (let i = 0; i < Math.min(items.length, {limit}); i++) {{
                const item = items[i];
                results.push({{
                    id: item.getAttribute('data-id') || item.id,
                    registro: item.querySelector('.registro, [class*="registro"]')?.textContent?.trim() || '',
                    titulo: item.querySelector('h3, h2, [class*="titulo"]')?.textContent?.trim() || '',
                    materia: item.querySelector('.materia, [class*="materia"]')?.textContent?.trim() || '',
                    sala: item.querySelector('.sala, [class*="sala"]')?.textContent?.trim() || '',
                    vigencia: item.querySelector('.vigencia, [class*="vigencia"]')?.textContent?.trim() || 'vigente',
                    url: item.querySelector('a')?.href || '',
                    preview: item.querySelector('.preview, [class*="preview"]')?.textContent?.trim() || ''
                }});
            }}
            return results;
        }}
        """
        
        try:
            results = await self.page.evaluate(extraction_script)
            
            # Enrich with timestamps and source
            for result in results:
                result['extracted_at'] = datetime.now().isoformat()
                result['source'] = 'scjn_puppeteer'
            
            return results
        except Exception as e:
            logger.error(f"❌ Extraction error: {e}")
            return []
    
    async def get_tesis_detail(self, tesis_url: str) -> Optional[dict]:
        """
        Get full content of a specific tesis
        
        Args:
            tesis_url: Direct URL to tesis
        
        Returns:
            Full tesis details with content and metadata
        """
        
        try:
            await self.page.goto(tesis_url)
            await asyncio.sleep(2)
            
            detail_script = """
            () => {
                return {
                    titulo: document.querySelector('h1, [class*="titulo"]')?.textContent?.trim(),
                    contenido: document.querySelector('.content, [class*="contenido"]')?.textContent?.trim(),
                    ficha_tecnica: {
                        registro: document.querySelector('[data-field="registro"]')?.textContent?.trim(),
                        ponente: document.querySelector('[data-field="ponente"]')?.textContent?.trim(),
                        fecha: document.querySelector('[data-field="fecha"]')?.textContent?.trim(),
                        instancia: document.querySelector('[data-field="instancia"]')?.textContent?.trim(),
                    },
                    download_word: document.querySelector('a[href*=".docx"], a[class*="download"]')?.href,
                    documentos_sugeridos: Array.from(
                        document.querySelectorAll('[class*="sugerido"] a')
                    ).map(a => ({
                        titulo: a.textContent.trim(),
                        url: a.href
                    }))
                };
            }
            """
            
            details = await self.page.evaluate(detail_script)
            details['url'] = tesis_url
            details['extracted_at'] = datetime.now().isoformat()
            
            return details
        
        except Exception as e:
            logger.error(f"❌ Detail extraction error: {e}")
            return None
    
    async def paginate_results(
        self,
        query: str,
        max_pages: int = 5,
        **filters
    ) -> List[dict]:
        """
        Paginate through search results
        
        Args:
            query: Search query
            max_pages: Maximum pages to crawl
            **filters: Additional filters
        
        Returns:
            All results from all pages
        """
        
        all_results = []
        
        for page_num in range(1, max_pages + 1):
            try:
                logger.info(f"📄 Fetching page {page_num}...")
                
                # Search or navigate to next page
                if page_num == 1:
                    results = await self.search_tesis(query, **filters)
                else:
                    # Click next button
                    next_btn = await self.page.querySelector(
                        '.next-page, [class*="siguiente"], a[rel="next"]'
                    )
                    if not next_btn:
                        break
                    
                    await next_btn.click()
                    await asyncio.sleep(2)
                    results = await self._extract_results(limit=20)
                
                all_results.extend(results)
                
                # Smart delay to avoid rate limiting
                await asyncio.sleep(1 + page_num * 0.5)
            
            except Exception as e:
                logger.warning(f"⚠️ Error on page {page_num}: {e}")
                break
        
        logger.info(f"✅ Pagination complete: {len(all_results)} total results")
        return all_results
    
    async def search_by_registro(self, registro: str) -> Optional[dict]:
        """
        Search specific tesis by registro ID
        
        Example: "1a./J. 45/2023"
        """
        
        try:
            results = await self.search_tesis(f'"{registro}"', limit=1)
            if results and results[0]['url']:
                return await self.get_tesis_detail(results[0]['url'])
            return None
        except Exception as e:
            logger.error(f"❌ Error searching registro {registro}: {e}")
            return None


# Context manager for convenience
class SCJNPuppeteerContext:
    """Context manager for browser lifecycle"""
    
    def __init__(self, **kwargs):
        self.scout = SCJNPuppeteerScout(**kwargs)
    
    async def __aenter__(self):
        await self.scout.connect()
        return self.scout
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.scout.disconnect()


# Usage example
"""
async def main():
    async with SCJNPuppeteerContext() as scout:
        results = await scout.search_tesis(
            query="amparo laboral",
            materia="Laboral",
            sala="Primera",
            limit=20
        )
        
        for result in results:
            print(f"📄 {result['registro']}: {result['titulo']}")
            detail = await scout.get_tesis_detail(result['url'])
            print(f"   Ponente: {detail['ficha_tecnica']['ponente']}")

if __name__ == "__main__":
    asyncio.run(main())
"""
