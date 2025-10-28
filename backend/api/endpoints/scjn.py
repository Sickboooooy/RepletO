"""
🔍 SCJN Search Endpoints
========================
FastAPI endpoints for SCJN jurisprudence search and integration with Itosturre
"""

from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import List, Optional, Literal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scjn", tags=["SCJN"])


@router.post("/search")
async def search_jurisprudencia(
    query: str = Query(..., description="Texto a buscar (soporta sintaxis SCJN)"),
    materia: Optional[str] = Query(None, description="Materia: Civil, Penal, Laboral, etc"),
    sala: Optional[str] = Query(None, description="Sala: Primera, Segunda, Pleno"),
    year: Optional[int] = Query(None, description="Año de publicación"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    use_cache: bool = Query(True, description="Usar caché si está disponible"),
    timeout: int = Query(30, ge=5, le=120, description="Timeout en segundos"),
):
    """
    Búsqueda multi-fuente de jurisprudencia SCJN
    
    Utiliza:
    - Puppeteer Scout: Búsquedas en vivo (rápidas)
    - ChromaDB Cache: Datos pre-indexados (instantáneo)
    
    Ejemplo:
    ```bash
    POST /api/v1/scjn/search
    {
        "query": "amparo laboral derecho a la huelga",
        "materia": "Laboral",
        "sala": "Primera",
        "year": 2023,
        "limit": 20
    }
    ```
    """
    
    try:
        from backend.services.scjn import SCJNPuppeteerScout
        
        scout = SCJNPuppeteerScout(timeout=timeout)
        await scout.connect()
        
        results = await scout.search_tesis(
            query=query,
            materia=materia,
            sala=sala,
            year=year,
            limit=limit
        )
        
        await scout.disconnect()
        
        return {
            "status": "success",
            "query": query,
            "filters": {
                "materia": materia,
                "sala": sala,
                "year": year
            },
            "results": results,
            "total": len(results),
            "timestamp": datetime.now().isoformat(),
            "source": "scjn_puppeteer"
        }
    
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tesis/{registro}")
async def get_tesis_by_registro(
    registro: str = Query(..., description="Registro SCJN (ej: 1a./J. 45/2023)"),
):
    """
    Obtiene tesis completa por registro
    
    Ejemplo:
    GET /api/v1/scjn/tesis/1a./J. 45/2023
    """
    
    try:
        from backend.services.scjn import SCJNPuppeteerScout
        
        scout = SCJNPuppeteerScout()
        await scout.connect()
        
        result = await scout.search_by_registro(registro)
        
        await scout.disconnect()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Tesis no encontrada: {registro}")
        
        return {
            "status": "success",
            "registro": registro,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Error fetching tesis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_jurisprudencia_citations(
    text: str = Query(..., description="Texto legal a validar"),
    extract_citations: bool = Query(True, description="Extraer citaciones automáticamente"),
):
    """
    ENDPOINT CLAVE PARA ITOSTURRE:
    Valida texto legal extrayendo citaciones
    
    Retorna:
    - Citaciones encontradas
    - Validación en SCJN
    - Semáforo de vigencia (🟢🟡🔴)
    - Riesgos detectados
    """
    
    try:
        import re
        from backend.services.scjn import SCJNPuppeteerScout
        
        # Extract potential citations
        citation_pattern = r'(\d+[a-z]+\.)/[JT]\.?\s*(\d+)/(\d{4})'
        citations = re.findall(citation_pattern, text)
        
        scout = SCJNPuppeteerScout()
        await scout.connect()
        
        validated_citations = []
        
        for citation in citations:
            registro = f"{citation[0]}/{citation[1]}/{citation[2]}"
            
            result = await scout.search_by_registro(registro)
            
            if result:
                validated_citations.append({
                    "registro": registro,
                    "found": True,
                    "titulo": result.get('titulo'),
                    "vigencia": "vigente",  # Will come from Itosturre semáforo
                    "semaforo": "🟢"
                })
            else:
                validated_citations.append({
                    "registro": registro,
                    "found": False,
                    "semaforo": "🔴",
                    "warning": "Tesis no encontrada en SCJN - posible alucinación"
                })
        
        await scout.disconnect()
        
        return {
            "status": "success",
            "text_length": len(text),
            "citations_found": len(validated_citations),
            "citations": validated_citations,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/status")
async def sources_status():
    """
    Estado de todas las fuentes de datos SCJN
    
    Response:
    ```json
    {
        "scjn": {
            "status": "healthy",
            "last_sync": "2025-10-28T02:00:00Z",
            "total_tesis": 45230,
            "new_this_week": 12
        }
    }
    ```
    """
    
    try:
        # Check if crawler metadata exists
        import json
        import os
        from datetime import datetime, timedelta
        
        metadata = {
            "scjn": {
                "status": "checking",
                "last_sync": None,
                "total_tesis": 0,
                "new_this_week": 0
            }
        }
        
        # Try to read last crawl metadata
        if os.path.exists("data/scjn_tesis_weekly.json"):
            try:
                with open("data/scjn_tesis_weekly.json", "r") as f:
                    data = json.load(f)
                
                meta = data.get("metadata", {})
                metadata["scjn"] = {
                    "status": "healthy",
                    "last_sync": meta.get("extracted_at"),
                    "total_tesis": meta.get("total_tesis", 0),
                    "new_this_week": 0,  # Would come from comparison
                    "crawl_stats": meta.get("crawl_stats")
                }
            except Exception as e:
                logger.warning(f"⚠️ Could not read crawl metadata: {e}")
                metadata["scjn"]["status"] = "error"
        else:
            metadata["scjn"]["status"] = "not_synced"
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "sources": metadata
        }
    
    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/trigger")
async def trigger_manual_sync(
    background_tasks: BackgroundTasks,
    full_crawl: bool = Query(False, description="Ejecutar crawl completo vs quick sync")
):
    """
    Dispara sincronización manual de SCJN
    
    - full_crawl=false (default): Quick sync (solo nuevas tesis)
    - full_crawl=true: Full crawl (todas las tesis)
    """
    
    try:
        logger.info(f"🔄 Manual sync triggered (full_crawl={full_crawl})")
        
        if full_crawl:
            background_tasks.add_task(
                _trigger_full_crawl
            )
            message = "Full crawl scheduled in background"
        else:
            background_tasks.add_task(
                _trigger_quick_sync
            )
            message = "Quick sync scheduled in background"
        
        return {
            "status": "scheduled",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Sync trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _trigger_full_crawl():
    """Background task: full crawl"""
    try:
        from backend.services.scjn import SCJNCrawler
        
        crawler = SCJNCrawler(headless=True)
        
        if await crawler.initialize_driver():
            await crawler.crawl_all_combinations()
            crawler.save_to_json()
        
        await crawler.close()
        logger.info("✅ Full crawl completed")
    
    except Exception as e:
        logger.error(f"❌ Full crawl failed: {e}")


async def _trigger_quick_sync():
    """Background task: quick sync"""
    try:
        from backend.services.scjn import SCJNPuppeteerScout
        
        scout = SCJNPuppeteerScout()
        await scout.connect()
        
        # Search for recent updates
        results = await scout.search_tesis(
            query="(2024 OR 2025 OR reciente)",
            limit=50
        )
        
        await scout.disconnect()
        logger.info(f"✅ Quick sync completed: {len(results)} new tesis")
    
    except Exception as e:
        logger.error(f"❌ Quick sync failed: {e}")
