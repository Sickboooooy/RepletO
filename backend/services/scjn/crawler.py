"""
🔄 SCJN Selenium Crawler
========================
Weekly bulk crawl of SCJN jurisprudence
- Comprehensive data extraction
- All materias, salas, years
- Scheduled synchronization
- Stores in ChromaDB
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json
import time

logger = logging.getLogger(__name__)


class SCJNCrawler:
    """
    Weekly SCJN crawler using Selenium + BeautifulSoup
    Designed for comprehensive data extraction
    """
    
    # SCJN filter options
    MATERIAS = [
        'Civil',
        'Penal',
        'Laboral',
        'Fiscal',
        'Constitucional',
        'Administrativa',
        'Mercantil'
    ]
    
    SALAS = [
        'Primera',
        'Segunda',
        'Pleno'
    ]
    
    YEARS = list(range(2020, 2026))  # Last 5 years
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Args:
            headless: Run browser without GUI
            timeout: Timeout per operation
        """
        self.base_url = "https://bj.scjn.gob.mx"
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.all_tesis = []
        self.crawl_stats = {
            'total_tesis': 0,
            'total_pages': 0,
            'errors': [],
            'start_time': None,
            'end_time': None
        }
    
    async def initialize_driver(self):
        """Initialize Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.timeout)
            
            logger.info("✅ Selenium WebDriver initialized")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize driver: {e}")
            return False
    
    async def crawl_all_combinations(self) -> List[dict]:
        """
        Crawl all combinations of materia, sala, year
        
        Returns:
            All tesis found
        """
        
        self.crawl_stats['start_time'] = datetime.now().isoformat()
        
        total_combinations = len(self.MATERIAS) * len(self.SALAS) * len(self.YEARS)
        current = 0
        
        for materia in self.MATERIAS:
            for sala in self.SALAS:
                for year in self.YEARS:
                    current += 1
                    progress = f"{current}/{total_combinations}"
                    
                    try:
                        logger.info(
                            f"🔍 [{progress}] Crawling: {materia} / {sala} / {year}"
                        )
                        
                        await self.search_and_extract(
                            materia=materia,
                            sala=sala,
                            year=year
                        )
                        
                        # Smart delay
                        await asyncio.sleep(1)
                    
                    except Exception as e:
                        error_msg = f"Error in {materia}/{sala}/{year}: {str(e)}"
                        logger.error(f"❌ {error_msg}")
                        self.crawl_stats['errors'].append(error_msg)
        
        self.crawl_stats['end_time'] = datetime.now().isoformat()
        self.crawl_stats['total_tesis'] = len(self.all_tesis)
        
        logger.info(f"✅ Crawl complete: {len(self.all_tesis)} tesis extracted")
        return self.all_tesis
    
    async def search_and_extract(
        self,
        materia: str,
        sala: str,
        year: int
    ) -> int:
        """
        Search and extract tesis for specific combination
        
        Returns:
            Number of tesis extracted
        """
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import Select
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from bs4 import BeautifulSoup
            
            # Navigate
            self.driver.get(self.base_url)
            time.sleep(2)
            
            # Click Tesis
            tesis_link = self.driver.find_element(By.LINK_TEXT, "Tesis")
            tesis_link.click()
            time.sleep(2)
            
            # Apply filters
            try:
                Select(self.driver.find_element(By.NAME, "materia")).select_by_value(materia)
            except:
                pass
            
            try:
                Select(self.driver.find_element(By.NAME, "sala")).select_by_value(sala)
            except:
                pass
            
            try:
                Select(self.driver.find_element(By.NAME, "year")).select_by_value(str(year))
            except:
                pass
            
            # Execute search
            search_btn = self.driver.find_element(By.CLASS_NAME, "btn-search")
            search_btn.click()
            
            wait = WebDriverWait(self.driver, self.timeout)
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "result-item")))
            
            # Paginate and extract
            page_count = 0
            extracted_in_combo = 0
            
            while True:
                page_count += 1
                
                # Extract HTML
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                results = soup.find_all('div', class_='result-item')
                
                for result in results:
                    try:
                        tesis_data = self._parse_result(result, materia, sala, year)
                        
                        # Get full detail
                        result_url = result.find('a')
                        if result_url:
                            tesis_data['url'] = result_url['href']
                            detail = await self._get_detail_async(tesis_data['url'])
                            tesis_data.update(detail)
                        
                        self.all_tesis.append(tesis_data)
                        extracted_in_combo += 1
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to parse result: {e}")
                        continue
                
                # Check for next page
                try:
                    next_btn = self.driver.find_element(By.CLASS_NAME, "next-page")
                    next_btn.click()
                    time.sleep(2)
                except:
                    break  # No more pages
            
            logger.info(
                f"   ✅ Extracted {extracted_in_combo} tesis from {page_count} pages"
            )
            self.crawl_stats['total_pages'] += page_count
            
            return extracted_in_combo
        
        except Exception as e:
            logger.error(f"❌ Search and extract error: {e}")
            return 0
    
    def _parse_result(self, result_element, materia: str, sala: str, year: int) -> dict:
        """Parse a single result element"""
        
        from bs4 import BeautifulSoup
        
        return {
            'id': result_element.get('data-id', ''),
            'registro': result_element.find('span', class_='registro').text.strip() if result_element.find('span', class_='registro') else '',
            'titulo': result_element.find('h3').text.strip() if result_element.find('h3') else '',
            'materia': materia,
            'sala': sala,
            'year': year,
            'vigencia': result_element.find('span', class_='vigencia').text.strip() if result_element.find('span', class_='vigencia') else 'vigente',
            'extracted_at': datetime.now().isoformat(),
            'source': 'scjn_selenium'
        }
    
    async def _get_detail_async(self, url: str) -> dict:
        """Get detail page (runs in thread pool to avoid blocking)"""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_detail_sync, url)
    
    def _get_detail_sync(self, url: str) -> dict:
        """Synchronous detail extraction"""
        
        try:
            from bs4 import BeautifulSoup
            
            self.driver.get(url)
            time.sleep(1)
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            contenido_div = soup.find('div', class_='tesis-content')
            contenido = contenido_div.text.strip() if contenido_div else ''
            
            return {
                'contenido': contenido,
                'ficha_tecnica': {
                    'ponente': soup.find('span', class_='ponente').text.strip() if soup.find('span', class_='ponente') else '',
                    'fecha': soup.find('span', class_='fecha').text.strip() if soup.find('span', class_='fecha') else '',
                    'instancia': soup.find('span', class_='instancia').text.strip() if soup.find('span', class_='instancia') else '',
                },
                'download_word': soup.find('a', {'class': 'download-word'})['href'] if soup.find('a', {'class': 'download-word'}) else None
            }
        
        except Exception as e:
            logger.warning(f"⚠️ Failed to get detail: {e}")
            return {}
    
    def save_to_json(self, filename: str = 'scjn_tesis_dump.json') -> str:
        """Save all extracted data to JSON"""
        
        try:
            filepath = f"data/{filename}"
            
            output = {
                'metadata': {
                    'extracted_at': datetime.now().isoformat(),
                    'total_tesis': len(self.all_tesis),
                    'crawl_stats': self.crawl_stats
                },
                'data': self.all_tesis
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Data saved to {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"❌ Failed to save: {e}")
            return ""
    
    async def close(self):
        """Close browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser closed")
        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")


# Scheduler integration
class SCJNCrawlScheduler:
    """Manages scheduled crawl jobs"""
    
    def __init__(self):
        self.crawler = None
        self.is_running = False
    
    async def start_crawl(self) -> bool:
        """Start a crawl job"""
        
        if self.is_running:
            logger.warning("⚠️ Crawl already running")
            return False
        
        try:
            self.is_running = True
            self.crawler = SCJNCrawler(headless=True)
            
            if not await self.crawler.initialize_driver():
                return False
            
            await self.crawler.crawl_all_combinations()
            self.crawler.save_to_json()
            
            logger.info("✅ Crawl completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"❌ Crawl failed: {e}")
            return False
        
        finally:
            self.is_running = False
            if self.crawler:
                await self.crawler.close()


# Usage example
"""
async def main():
    crawler = SCJNCrawler(headless=False)  # For testing
    
    if await crawler.initialize_driver():
        tesis = await crawler.crawl_all_combinations()
        crawler.save_to_json()
        print(f"✅ Extracted {len(tesis)} tesis")
    
    await crawler.close()

if __name__ == "__main__":
    asyncio.run(main())
"""
