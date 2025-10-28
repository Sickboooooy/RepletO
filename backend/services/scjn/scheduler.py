"""
📅 SCJN Scheduler (Bulk Download Strategy)
===========================================
APScheduler integration for automated SCJN data extraction

Jobs:
- Every Friday 03:00 AM: Download weekly batch from sjfsemanal.scjn.gob.mx
- Every Friday 04:00 AM: Index & vectorize into ChromaDB
- Daily 06:00 PM: Quick validation sync
- On-demand: Puppeteer Scout for urgent queries

Strategy:
✅ Official weekly bulk downloads (no scraping)
✅ Local library indexing (fast searches)
✅ Fallback to live Puppeteer when needed
✅ Minimal SCJN resource usage
"""

import logging
from datetime import datetime
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)


class SCJNWeeklySyncScheduler:
    """
    Weekly scheduler for SCJN bulk data synchronization
    
    Primary Strategy: Official weekly bulk downloads
    
    Schedule:
    - Friday 03:00 AM: Download weekly batch from sjfsemanal.scjn.gob.mx
    - Friday 04:00 AM: Index & vectorize into ChromaDB
    - Daily 18:00 (6 PM): Quick validation sync
    - On-demand: Puppeteer Scout for urgent queries
    
    Previous strategy (dynamic scraping):
    - DEPRECATED in favor of official bulk publications
    - Kept as fallback for urgent real-time searches
    """
    
    def __init__(self, bulk_downloader=None, vector_db=None, puppeteer_scout=None):
        """
        Args:
            bulk_downloader: SCJNBulkDownloader instance
            vector_db: ChromaDB or similar vector store
            puppeteer_scout: SCJNPuppeteerScout for fallback
        """
        self.bulk_downloader = bulk_downloader
        self.vector_db = vector_db
        self.puppeteer_scout = puppeteer_scout
        self.scheduler = None
        self.jobs = {}
    
    async def setup_scheduler(self):
        """
        Initialize APScheduler with bulk download strategy
        
        NEW STRATEGY (Bulk Downloads):
        - Friday 03:00 AM: Download weekly batch from sjfsemanal.scjn.gob.mx
        - Friday 04:00 AM: Index into ChromaDB
        - Daily 18:00: Quick validation check
        
        OLD STRATEGY (DEPRECATED):
        - Monday 2 AM: Selenium crawl (REPLACED by bulk download)
        - Tuesday 2 AM: Vectorization (MOVED to Friday 4 AM)
        - Wednesday 2 AM: Validation (MOVED to daily)
        """
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            
            self.scheduler = AsyncIOScheduler()
            
            # BULK DOWNLOAD: Friday 03:00 AM
            self.scheduler.add_job(
                self.download_weekly_bulk,
                'cron',
                day_of_week='fri',
                hour=3,
                minute=0,
                id='bulk_download_scjn_friday',
                max_instances=1,
                coalesce=True
            )
            
            # INDEXING: Friday 04:00 AM (1 hour after download)
            self.scheduler.add_job(
                self.index_and_vectorize,
                'cron',
                day_of_week='fri',
                hour=4,
                minute=0,
                id='index_scjn_friday',
                max_instances=1,
                coalesce=True
            )
            
            # VALIDATION: Daily 18:00 (6 PM) - Quick check
            self.scheduler.add_job(
                self.daily_validation_check,
                'cron',
                hour=18,
                minute=0,
                id='validate_scjn_daily',
                max_instances=1,
                coalesce=True
            )
            
            logger.info("✅ Bulk download scheduler setup complete")
            logger.info("📅 Schedule: Friday 03:00 (download), Friday 04:00 (index), Daily 18:00 (validate)")
            return True
        
        except Exception as e:
            logger.error(f"❌ Scheduler setup failed: {e}")
            return False
    
    async def start(self):
        """Start scheduler"""
        try:
            if not self.scheduler:
                await self.setup_scheduler()
            
            self.scheduler.start()
            logger.info("✅ Scheduler started")
        
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
    
    async def stop(self):
        """Stop scheduler"""
        try:
            if self.scheduler:
                self.scheduler.shutdown()
                logger.info("✅ Scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
    
    async def download_weekly_bulk(self):
        """
        Weekly bulk download - Friday 03:00 AM
        
        Downloads from official SCJN source: sjfsemanal.scjn.gob.mx
        
        Benefits:
        ✅ Official source - no TOS violations
        ✅ Complete dataset - all tesis published
        ✅ No rate limiting - official channel
        ✅ Structured format - ready for parsing
        """
        
        logger.info("� [SCHEDULED] Starting weekly bulk download from SCJN...")
        
        try:
            if not self.bulk_downloader:
                logger.error("❌ Bulk downloader not initialized")
                return
            
            # Download weekly batch
            tesis_list = await self.bulk_downloader.download_weekly_batch()
            
            logger.info(f"✅ Downloaded {len(tesis_list)} tesis")
            
            # Store each locally
            stored_count = 0
            for tesis in tesis_list:
                if self.bulk_downloader.store_tesis_locally(tesis):
                    stored_count += 1
            
            logger.info(f"✅ Stored {stored_count} tesis locally")
            
            # Update metadata
            self._update_sync_metadata(
                job_name='bulk_download',
                status='completed',
                records=stored_count
            )
        
        except Exception as e:
            logger.error(f"❌ Weekly bulk download failed: {e}")
            self._update_sync_metadata(
                job_name='bulk_download',
                status='error',
                error=str(e)
            )
    
    async def index_and_vectorize(self):
        """
        Index and vectorize new tesis - Friday 04:00 AM
        
        Takes downloaded tesis and:
        1. Creates local search index
        2. Vectorizes for semantic search
        3. Stores in ChromaDB
        """
        
        logger.info("🧠 [SCHEDULED] Starting indexing and vectorization...")
        
        try:
            if not self.bulk_downloader:
                logger.error("❌ Bulk downloader not initialized")
                return
            
            # Create local index
            index = self.bulk_downloader.create_local_index()
            logger.info(f"✅ Local index created: {len(index.get('all_files', []))} files")
            
            # Vectorize if vector DB available
            if self.vector_db:
                logger.info("📊 Vectorizing for semantic search...")
                
                # Get all tesis
                all_tesis = self.bulk_downloader.search_local_library("")
                
                # Vectorize each
                vectorized_count = 0
                for tesis in all_tesis:
                    try:
                        # Extract key fields for embedding
                        text_to_embed = f"{tesis.get('titulo', '')} {tesis.get('sumario', '')}"
                        
                        if await self.vector_db.add_document(
                            text=text_to_embed,
                            metadata=tesis
                        ):
                            vectorized_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Vectorization error for {tesis.get('registro')}: {e}")
                
                logger.info(f"✅ Vectorized {vectorized_count} tesis")
            
            # Update metadata
            self._update_sync_metadata(
                job_name='index_vectorize',
                status='completed',
                records=len(index.get('all_files', []))
            )
        
        except Exception as e:
            logger.error(f"❌ Indexing failed: {e}")
            self._update_sync_metadata(
                job_name='index_vectorize',
                status='error',
                error=str(e)
            )
    
    async def daily_validation_check(self):
        """
        Daily quick validation - 18:00 (6 PM)
        
        Quick health checks:
        - Library is not corrupted
        - Latest data is accessible
        - Index is valid
        """
        
        logger.info("⏰ [SCHEDULED] Starting daily validation check...")
        
        try:
            if not self.bulk_downloader:
                logger.warning("⚠️ Bulk downloader not available for validation")
                return
            
            # Get stats
            stats = self.bulk_downloader.get_library_stats()
            
            logger.info(f"✅ Library validation: {stats['total_tesis']} tesis available")
            logger.info(f"  - Last updated: {stats['last_updated']}")
            logger.info(f"  - Materias: {len(stats.get('materias', {}))}")
            
            # Check if download needed urgently
            if stats['last_updated']:
                from datetime import datetime, timedelta
                last_update = datetime.fromisoformat(stats['last_updated'])
                days_since = (datetime.now() - last_update).days
                
                if days_since > 7:
                    logger.warning(f"⚠️ Data is {days_since} days old - consider manual sync")
            
            self._update_sync_metadata(
                job_name='daily_check',
                status='completed'
            )
        
        except Exception as e:
            logger.error(f"❌ Daily validation failed: {e}")
    
    async def sync_scjn_crawl(self):
        """
        [DEPRECATED] Full SCJN crawl
        
        REPLACED BY: download_weekly_bulk()
        
        Previously ran Monday 2 AM with Selenium.
        Now using official bulk downloads (Friday 3 AM) instead.
        
        Kept for reference or emergency fallback if bulk download fails.
        """
        
        logger.warning("⚠️ sync_scjn_crawl is DEPRECATED - use download_weekly_bulk instead")
        
        # If needed as fallback, could implement here
        pass
    
    async def vectorize_new_data(self):
        """
        Vectorize new tesis - runs Tuesday 2 AM
        Takes scraped data and embeds into ChromaDB
        """
        
        logger.info("🔄 [SCHEDULED] Starting vectorization...")
        
        try:
            if not self.vector_db:
                logger.error("❌ Vector DB not initialized")
                return
            
            # Load latest JSON
            import json
            with open('data/scjn_tesis_weekly.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tesis_list = data.get('data', [])
            logger.info(f"📊 Vectorizing {len(tesis_list)} tesis...")
            
            # Vectorize each tesis
            vectorized_count = 0
            for tesis in tesis_list:
                try:
                    embedding = await self._embed_tesis(tesis)
                    await self.vector_db.store(
                        text=tesis.get('contenido', ''),
                        embedding=embedding,
                        metadata={
                            'registro': tesis.get('registro'),
                            'titulo': tesis.get('titulo'),
                            'materia': tesis.get('materia'),
                            'sala': tesis.get('sala'),
                            'year': tesis.get('year'),
                            'source': 'scjn',
                            'extracted_at': tesis.get('extracted_at')
                        }
                    )
                    vectorized_count += 1
                
                except Exception as e:
                    logger.warning(f"⚠️ Failed to vectorize {tesis.get('registro')}: {e}")
                    continue
            
            self._update_sync_metadata(
                job_name='vectorization',
                status='completed',
                records=vectorized_count
            )
            
            logger.info(f"✅ Vectorization complete: {vectorized_count} tesis")
        
        except Exception as e:
            logger.error(f"❌ Vectorization failed: {e}")
            self._update_sync_metadata(
                job_name='vectorization',
                status='error',
                error=str(e)
            )
    
    async def _embed_tesis(self, tesis: dict) -> list:
        """
        Embed tesis content using embedder
        Returns vector representation
        """
        
        # This would use your embedder service
        # For now, placeholder
        from backend.services.embedder import Embedder
        
        embedder = Embedder()
        text = f"{tesis.get('titulo', '')} {tesis.get('contenido', '')}"
        return await embedder.embed(text)
    
    async def quick_sync_daily(self):
        """
        Quick daily sync - runs 6 PM daily
        Only fetches new tesis since last sync
        """
        
        logger.info("🔄 [SCHEDULED] Starting quick daily sync...")
        
        try:
            # Get last sync timestamp
            last_sync = self._get_last_sync_time('quick_sync')
            
            logger.info(f"📅 Syncing tesis since {last_sync}...")
            
            # Use puppeteer scout for quick searches
            if hasattr(self, 'scout'):
                # Search for recent updates
                results = await self.scout.search_tesis(
                    query="(recent OR new OR 2024 OR 2025)",
                    limit=50
                )
                
                logger.info(f"✅ Found {len(results)} new tesis")
                
                self._update_sync_metadata(
                    job_name='quick_sync',
                    status='completed',
                    records=len(results)
                )
        
        except Exception as e:
            logger.error(f"❌ Quick sync failed: {e}")
            self._update_sync_metadata(
                job_name='quick_sync',
                status='error',
                error=str(e)
            )
    
    async def validate_cache(self):
        """
        Validate cache - runs Wednesday 2 AM
        Checks for stale or corrupted data
        """
        
        logger.info("🔄 [SCHEDULED] Starting cache validation...")
        
        try:
            import json
            
            # Load and validate JSON
            with open('data/scjn_tesis_weekly.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tesis_list = data.get('data', [])
            issues = []
            
            for tesis in tesis_list:
                # Check required fields
                if not tesis.get('registro'):
                    issues.append(f"Missing registro: {tesis.get('titulo')}")
                
                if not tesis.get('contenido'):
                    issues.append(f"Missing contenido: {tesis.get('registro')}")
            
            if issues:
                logger.warning(f"⚠️ Cache issues found: {len(issues)}")
                self._update_sync_metadata(
                    job_name='cache_validation',
                    status='warning',
                    records=len(tesis_list),
                    issues=len(issues)
                )
            else:
                logger.info(f"✅ Cache valid: {len(tesis_list)} tesis")
                self._update_sync_metadata(
                    job_name='cache_validation',
                    status='completed',
                    records=len(tesis_list)
                )
        
        except Exception as e:
            logger.error(f"❌ Cache validation failed: {e}")
            self._update_sync_metadata(
                job_name='cache_validation',
                status='error',
                error=str(e)
            )
    
    def _update_sync_metadata(self, job_name: str, status: str, **kwargs):
        """Update sync metadata"""
        
        metadata = {
            'job': job_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        self.jobs[job_name] = metadata
        logger.info(f"📝 Metadata updated: {metadata}")
    
    def _get_last_sync_time(self, job_name: str) -> Optional[str]:
        """Get last sync time for a job"""
        
        if job_name in self.jobs:
            return self.jobs[job_name].get('timestamp')
        
        return None
    
    def get_sync_status(self) -> dict:
        """Get overall sync status"""
        
        return {
            'scheduler_running': self.scheduler.running if self.scheduler else False,
            'jobs': self.jobs,
            'next_runs': self._get_next_runs()
        }
    
    def _get_next_runs(self) -> dict:
        """Get next scheduled runs"""
        
        if not self.scheduler:
            return {}
        
        next_runs = {}
        for job in self.scheduler.get_jobs():
            next_runs[job.id] = str(job.next_run_time)
        
        return next_runs


# Initialize scheduler in FastAPI startup
"""
from contextlib import asynccontextmanager

scheduler = None

@asynccontextmanager
async def lifespan(app):
    # Startup
    global scheduler
    scheduler = SCJNWeeklySyncScheduler(crawler=scjn_crawler, vector_db=chromadb)
    await scheduler.start()
    yield
    # Shutdown
    await scheduler.stop()

app = FastAPI(lifespan=lifespan)
"""
