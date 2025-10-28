"""
🔗 SCJN API Endpoints (Hybrid Strategy)
======================================
FastAPI endpoints for unified SCJN search

NEW ENDPOINTS:
- POST /api/v1/scjn/search (hybrid: local cache + ChromaDB + live)
- GET /api/v1/scjn/tesis/{registro} (detail with freshness)
- POST /api/v1/scjn/validate (citation validation - CRITICAL FOR ITOSTURRE)
- GET /api/v1/scjn/library/stats (local library statistics)
- POST /api/v1/scjn/sync/manual (manual bulk download trigger)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scjn", tags=["SCJN"])

# Global instances (initialized in main.py)
hybrid_search = None
bulk_downloader = None


class SearchRequest(BaseModel):
    """Search request"""
    query: str
    materia: Optional[str] = None
    sala: Optional[str] = None
    use_live: bool = False
    min_score: float = 0.5


class CitationValidationRequest(BaseModel):
    """Citation validation request"""
    citation: str
    context: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response"""
    results: List[dict]
    sources: List[str]
    response_time: float
    freshness: str
    total_found: int


@router.post("/search", response_model=SearchResponse)
async def unified_search(request: SearchRequest):
    """
    Unified SCJN search
    
    Strategy (in order):
    1. Check local bulk-downloaded library
    2. Semantic search in ChromaDB
    3. Fall back to live Puppeteer if >3 days old
    
    Args:
        query: Search text
        materia: Filter by legal matter (Laboral, Penal, etc.)
        sala: Filter by court (Primera, Segunda, Pleno)
        use_live: Force live search (bypass cache)
        min_score: Minimum relevance (0-1)
    
    Returns:
        Results from best source with freshness indicator
    
    Example:
        POST /api/v1/scjn/search
        {
            "query": "amparo laboral",
            "materia": "Laboral",
            "sala": "Primera",
            "use_live": false
        }
        
        Response:
        {
            "results": [...],
            "sources": ["local"],
            "response_time": 0.032,
            "freshness": "fresh",
            "total_found": 45
        }
    """
    
    try:
        if not hybrid_search:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        result = await hybrid_search.unified_search(
            query=request.query,
            materia=request.materia,
            sala=request.sala,
            use_live=request.use_live,
            min_score=request.min_score
        )
        
        return SearchResponse(**result)
    
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tesis/{registro}")
async def get_tesis_detail(
    registro: str,
    prefer_live: bool = False
):
    """
    Get detailed tesis information
    
    Args:
        registro: Tesis registro (e.g., "1a./J. 45/2023")
        prefer_live: Force live lookup instead of cache
    
    Returns:
        Full tesis data with validity status
    
    Example:
        GET /api/v1/scjn/tesis/1a./J.%2045/2023
    """
    
    try:
        if not hybrid_search:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        tesis = await hybrid_search.get_tesis_detail(
            registro=registro,
            prefer_live=prefer_live
        )
        
        if not tesis:
            raise HTTPException(status_code=404, detail=f"Tesis not found: {registro}")
        
        return tesis
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get tesis detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_citation(request: CitationValidationRequest):
    """
    Validate legal citation against SCJN database
    
    🚨 CRITICAL FOR ITOSTURRE 🚨
    
    This endpoint:
    1. Extracts tesis registro from citation text
    2. Looks up in SCJN database
    3. Checks validity status
    4. Detects LLM hallucinations
    5. Returns semáforo status 🟢🟡🔴
    
    Args:
        citation: Citation text (e.g., "Tesis aislada 1a./J. 45/2023")
        context: Legal context/ruling text (for semantic validation)
    
    Returns:
        Validation result with semáforo status
    
    Response statuses:
    - 'vigente': 🟢 Citation is valid and current
    - 'contradicción': 🟡 Citation contradicted by newer jurisprudence
    - 'superada': 🟡 Citation superseded/outdated
    - 'alucinación': 🔴 Citation not found (LLM hallucination)
    
    Example:
        POST /api/v1/scjn/validate
        {
            "citation": "Tesis aislada 1a./J. 45/2023",
            "context": "En materia de amparo laboral..."
        }
        
        Response:
        {
            "valid": true,
            "registro": "1a./J. 45/2023",
            "status": "vigente",
            "confidence": 0.95,
            "message": "Citation is vigente",
            "semaforo": "🟢"
        }
    """
    
    try:
        if not hybrid_search:
            raise HTTPException(status_code=503, detail="Search service not initialized")
        
        validation = await hybrid_search.validate_citation(
            citation=request.citation,
            context=request.context
        )
        
        # Add semáforo indicator
        status_to_semaforo = {
            'vigente': '🟢',
            'contradicción': '🟡',
            'superada': '🟡',
            'alucinación': '🔴',
            'desconocida': '⚪',
            'error': '❌'
        }
        
        validation['semaforo'] = status_to_semaforo.get(validation.get('status'), '❓')
        
        return validation
    
    except Exception as e:
        logger.error(f"❌ Citation validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/library/stats")
async def get_library_stats():
    """
    Get local SCJN library statistics
    
    Returns:
        Library metadata and statistics
    
    Example Response:
        {
            "total_tesis": 45230,
            "materias": {
                "Laboral": 10234,
                "Penal": 8932,
                "Civil": 12123,
                ...
            },
            "salas": {
                "Primera": 15000,
                "Segunda": 15000,
                "Pleno": 15230
            },
            "last_updated": "2024-01-12T04:00:00",
            "storage_path": "/data/scjn_library",
            "download_stats": {
                "total_downloaded": 45230,
                "total_stored": 45230,
                "last_sync": "2024-01-12T03:45:00"
            }
        }
    """
    
    try:
        if not bulk_downloader:
            raise HTTPException(status_code=503, detail="Library service not initialized")
        
        stats = bulk_downloader.get_library_stats()
        return stats
    
    except Exception as e:
        logger.error(f"❌ Failed to get library stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/status")
async def get_sources_status():
    """
    Get status of all SCJN data sources
    
    Returns:
        Status of: local cache, ChromaDB, Puppeteer Scout, last sync
    """
    
    try:
        status = {
            'local_cache': 'unknown',
            'chroma_db': 'unknown',
            'puppeteer_scout': 'unknown',
            'last_sync': None,
            'next_sync': 'Friday 03:00 AM'
        }
        
        if bulk_downloader:
            stats = bulk_downloader.get_library_stats()
            status['local_cache'] = 'ready' if stats['total_tesis'] > 0 else 'empty'
            status['last_sync'] = stats['last_updated']
        
        if hybrid_search and hybrid_search.chroma_db:
            status['chroma_db'] = 'ready'
        
        if hybrid_search and hybrid_search.puppeteer_scout:
            status['puppeteer_scout'] = 'ready'
        
        return status
    
    except Exception as e:
        logger.error(f"❌ Failed to get sources status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/manual")
async def trigger_manual_sync(background_tasks: BackgroundTasks):
    """
    Manually trigger SCJN bulk download and sync
    
    Runs asynchronously in background
    
    Normal schedule:
    - Friday 03:00 AM: Automatic bulk download
    - Friday 04:00 AM: Automatic indexing
    
    This endpoint allows manual triggering outside schedule
    
    Returns:
        Job ID for status tracking
    
    Example Response:
        {
            "job_id": "manual_sync_2024_01_15_143022",
            "status": "queued",
            "message": "Bulk download queued in background"
        }
    """
    
    try:
        if not bulk_downloader:
            raise HTTPException(status_code=503, detail="Download service not initialized")
        
        job_id = f"manual_sync_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"
        
        # Queue async task
        async def run_sync():
            logger.info(f"🔄 Manual sync started: {job_id}")
            try:
                tesis_list = await bulk_downloader.download_weekly_batch()
                for tesis in tesis_list:
                    bulk_downloader.store_tesis_locally(tesis)
                
                bulk_downloader.create_local_index()
                logger.info(f"✅ Manual sync completed: {job_id}")
            except Exception as e:
                logger.error(f"❌ Manual sync failed: {e}")
        
        background_tasks.add_task(run_sync)
        
        return {
            'job_id': job_id,
            'status': 'queued',
            'message': 'Bulk download queued in background',
            'next_check_endpoint': f'/api/v1/scjn/sources/status'
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to trigger manual sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check for SCJN service
    
    Returns:
        Service status
    """
    
    status = {
        'service': 'scjn_hybrid_search',
        'status': 'healthy' if hybrid_search else 'degraded',
        'components': {
            'hybrid_search': 'ok' if hybrid_search else 'missing',
            'bulk_downloader': 'ok' if bulk_downloader else 'missing',
        }
    }
    
    return status


# Initialization function (call from main.py)
def initialize_scjn_service(
    hybrid_search_instance,
    bulk_downloader_instance
):
    """
    Initialize SCJN service
    
    Call from main.py:
        from backend.services.scjn.hybrid_search import HybridSearchAdapter
        from backend.services.scjn.bulk_downloader import SCJNBulkDownloader
        
        bulk_dl = SCJNBulkDownloader()
        hybrid = HybridSearchAdapter(bulk_downloader=bulk_dl)
        
        initialize_scjn_service(hybrid, bulk_dl)
    """
    
    global hybrid_search, bulk_downloader
    
    hybrid_search = hybrid_search_instance
    bulk_downloader = bulk_downloader_instance
    
    logger.info("✅ SCJN service initialized")
    logger.info(f"  - Hybrid search: {type(hybrid_search).__name__}")
    logger.info(f"  - Bulk downloader: {type(bulk_downloader).__name__}")
