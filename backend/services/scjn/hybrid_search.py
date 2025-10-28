"""
🔗 SCJN Hybrid Search Adapter
=============================
Unified search interface using:
1. Local bulk library (primary) - instant results
2. Puppeteer Scout (fallback) - real-time when needed
3. ChromaDB vectorized (semantic search)

Priority Order:
- Local cache check (~0ms)
- ChromaDB semantic search (~50ms) 
- Puppeteer live search (~2-5s) if ≥3 days old or not found
- Return combined results with freshness indicators
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class HybridSearchAdapter:
    """
    Unified search interface combining multiple SCJN sources
    
    Strategy:
    ✅ Fast: Check local cache first
    ✅ Accurate: ChromaDB semantic search
    ✅ Fresh: Fall back to live search if old
    ✅ Efficient: Minimize SCJN API calls
    """
    
    def __init__(
        self,
        bulk_downloader=None,
        puppeteer_scout=None,
        chroma_db=None,
        freshness_threshold_days: int = 3
    ):
        """
        Args:
            bulk_downloader: SCJNBulkDownloader instance
            puppeteer_scout: SCJNPuppeteerScout instance
            chroma_db: ChromaDB instance
            freshness_threshold_days: Days before considering cache stale
        """
        self.bulk_downloader = bulk_downloader
        self.puppeteer_scout = puppeteer_scout
        self.chroma_db = chroma_db
        self.freshness_threshold_days = freshness_threshold_days
        
        self.search_stats = {
            'local_hits': 0,
            'chroma_hits': 0,
            'live_hits': 0,
            'total_searches': 0,
            'avg_response_time': 0
        }
    
    async def unified_search(
        self,
        query: str,
        materia: Optional[str] = None,
        sala: Optional[str] = None,
        use_live: bool = False,
        min_score: float = 0.5
    ) -> Dict:
        """
        Unified search across all sources
        
        Args:
            query: Search query
            materia: Filter by materia
            sala: Filter by sala
            use_live: Force live search (bypass cache)
            min_score: Minimum relevance score (0-1)
        
        Returns:
            {
                'results': [...],
                'sources': ['local', 'chroma', 'live'],
                'response_time': 0.234,
                'freshness': 'fresh',
                'total_found': 45
            }
        """
        
        start_time = datetime.now()
        
        try:
            results = {
                'local': [],
                'chroma': [],
                'live': []
            }
            sources_used = []
            
            # Step 1: Check local cache
            if self.bulk_downloader and not use_live:
                logger.info(f"🔍 Searching local cache: {query}")
                
                local_results = self.bulk_downloader.search_local_library(
                    query=query,
                    materia=materia,
                    sala=sala
                )
                
                if local_results:
                    results['local'] = local_results
                    sources_used.append('local')
                    self.search_stats['local_hits'] += 1
                    logger.info(f"✅ Local cache: {len(local_results)} results")
            
            # Step 2: ChromaDB semantic search
            if self.chroma_db and not use_live and not results['local']:
                logger.info(f"🧠 Semantic search in ChromaDB: {query}")
                
                try:
                    chroma_results = await self.chroma_db.semantic_search(
                        query=query,
                        top_k=10,
                        where_filter={
                            'materia': materia,
                            'sala': sala
                        } if materia or sala else None,
                        min_score=min_score
                    )
                    
                    if chroma_results:
                        results['chroma'] = chroma_results
                        sources_used.append('chroma')
                        self.search_stats['chroma_hits'] += 1
                        logger.info(f"✅ ChromaDB: {len(chroma_results)} results")
                except Exception as e:
                    logger.warning(f"⚠️ ChromaDB search error: {e}")
            
            # Step 3: Check freshness - go live if cache is stale
            should_go_live = use_live
            
            if not should_go_live and (results['local'] or results['chroma']):
                freshness = self._check_freshness(results)
                if freshness == 'stale':
                    logger.info("⏰ Cache is stale, triggering live search...")
                    should_go_live = True
            
            # Step 4: Fall back to live search if needed
            if (should_go_live or not results['local'] and not results['chroma']) and self.puppeteer_scout:
                logger.info(f"🚀 Live search: {query}")
                
                try:
                    live_results = await self.puppeteer_scout.search(
                        query=query,
                        materia=materia,
                        sala=sala
                    )
                    
                    if live_results:
                        results['live'] = live_results
                        sources_used.append('live')
                        self.search_stats['live_hits'] += 1
                        logger.info(f"✅ Live search: {len(live_results)} results")
                        
                        # Store in bulk downloader for future cache hits
                        if self.bulk_downloader:
                            for tesis in live_results:
                                self.bulk_downloader.store_tesis_locally(tesis)
                
                except Exception as e:
                    logger.warning(f"⚠️ Live search error: {e}")
            
            # Combine and deduplicate results
            combined_results = self._deduplicate_results(results)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Update stats
            self.search_stats['total_searches'] += 1
            self.search_stats['avg_response_time'] = (
                (self.search_stats['avg_response_time'] * (self.search_stats['total_searches'] - 1) + response_time)
                / self.search_stats['total_searches']
            )
            
            return {
                'results': combined_results,
                'sources': sources_used,
                'response_time': response_time,
                'freshness': self._check_freshness(results),
                'total_found': len(combined_results),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Unified search failed: {e}")
            return {
                'results': [],
                'sources': [],
                'response_time': (datetime.now() - start_time).total_seconds(),
                'error': str(e)
            }
    
    def _check_freshness(self, results: Dict) -> str:
        """
        Check data freshness
        
        Returns:
            'fresh', 'acceptable', or 'stale'
        """
        
        if not results['local'] and not results['chroma']:
            return 'unknown'
        
        # Check timestamps
        for result_group in [results['local'], results['chroma']]:
            if result_group:
                first_result = result_group[0]
                
                if 'downloaded_at' in first_result:
                    downloaded_at = datetime.fromisoformat(first_result['downloaded_at'])
                    age_days = (datetime.now() - downloaded_at).days
                    
                    if age_days <= 1:
                        return 'fresh'
                    elif age_days <= self.freshness_threshold_days:
                        return 'acceptable'
                    else:
                        return 'stale'
        
        return 'unknown'
    
    def _deduplicate_results(self, results: Dict) -> List[dict]:
        """
        Deduplicate results from different sources
        
        Priority: local > chroma > live
        """
        
        seen_registros = set()
        combined = []
        
        # Add local results first (most trusted)
        for tesis in results['local']:
            registro = tesis.get('registro')
            if registro and registro not in seen_registros:
                tesis['source'] = 'local'
                combined.append(tesis)
                seen_registros.add(registro)
        
        # Add ChromaDB results
        for tesis in results['chroma']:
            registro = tesis.get('registro')
            if registro and registro not in seen_registros:
                tesis['source'] = 'chroma'
                combined.append(tesis)
                seen_registros.add(registro)
        
        # Add live results (merge with existing if found)
        for tesis in results['live']:
            registro = tesis.get('registro')
            if registro and registro not in seen_registros:
                tesis['source'] = 'live'
                combined.append(tesis)
                seen_registros.add(registro)
        
        return combined
    
    async def get_tesis_detail(
        self,
        registro: str,
        prefer_live: bool = False
    ) -> Optional[dict]:
        """
        Get detailed tesis information
        
        Args:
            registro: Tesis registro (e.g., "1a./J. 45/2023")
            prefer_live: Force live lookup
        
        Returns:
            Full tesis data with validity status
        """
        
        try:
            # Try local first
            if self.bulk_downloader and not prefer_live:
                local_results = self.bulk_downloader.search_local_library(query=registro)
                if local_results:
                    logger.info(f"✅ Found locally: {registro}")
                    return local_results[0]
            
            # Fall back to live
            if self.puppeteer_scout:
                logger.info(f"🚀 Live lookup: {registro}")
                result = await self.puppeteer_scout.get_tesis_detail(registro)
                
                if result and self.bulk_downloader:
                    self.bulk_downloader.store_tesis_locally(result)
                
                return result
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Failed to get tesis detail: {e}")
            return None
    
    async def validate_citation(
        self,
        citation: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Validate legal citation (KEY FOR ITOSTURRE)
        
        Args:
            citation: Citation text (e.g., "Tesis aislada 1a./J. 45/2023")
            context: Legal context/ruling text
        
        Returns:
            {
                'valid': bool,
                'registro': str,
                'status': 'vigente' | 'contradicción' | 'superada' | 'alucinación',
                'confidence': 0-1,
                'message': str,
                'full_tesis': dict
            }
        """
        
        try:
            # Extract registro from citation
            import re
            
            # Pattern: 1a./J. 45/2023 or similar
            registro_pattern = r'(\d+[a-z]\.)/(\w+)\. (\d+)/(\d+)'
            match = re.search(registro_pattern, citation, re.IGNORECASE)
            
            if not match:
                logger.warning(f"❌ Could not parse registro from: {citation}")
                return {
                    'valid': False,
                    'status': 'alucinación',
                    'confidence': 1.0,
                    'message': 'Could not parse citation format'
                }
            
            # Reconstruct registro
            registro = f"{match.group(1)}{match.group(2)}. {match.group(3)}/{match.group(4)}"
            
            # Get tesis detail
            tesis = await self.get_tesis_detail(registro)
            
            if not tesis:
                logger.warning(f"⚠️ Tesis not found: {registro}")
                return {
                    'valid': False,
                    'registro': registro,
                    'status': 'alucinación',
                    'confidence': 0.9,
                    'message': f'Citation {registro} not found in SCJN database',
                    'full_tesis': None
                }
            
            # Check vigencia (validity)
            vigencia = tesis.get('vigencia', 'desconocida')
            
            status_map = {
                'vigente': 'vigente',
                'contradicción': 'contradicción',
                'superada': 'superada',
                'desconocida': 'desconocida'
            }
            
            status = status_map.get(vigencia, 'desconocida')
            
            # Validate context if provided
            context_match_score = 1.0
            if context and tesis.get('sumario'):
                context_match_score = await self._calculate_semantic_similarity(
                    context,
                    tesis['sumario']
                )
            
            return {
                'valid': True,
                'registro': registro,
                'status': status,
                'confidence': context_match_score,
                'message': f"Citation is {status}",
                'full_tesis': tesis,
                'vigencia_details': tesis.get('vigencia_info', {})
            }
        
        except Exception as e:
            logger.error(f"❌ Citation validation failed: {e}")
            return {
                'valid': False,
                'status': 'error',
                'confidence': 0.0,
                'message': str(e)
            }
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between texts
        
        Returns:
            Score 0-1
        """
        
        try:
            if self.chroma_db:
                similarity = await self.chroma_db.calculate_similarity(text1, text2)
                return similarity
        except Exception as e:
            logger.warning(f"⚠️ Similarity calculation error: {e}")
        
        # Fallback: simple keyword overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.5
        
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        return overlap / total if total > 0 else 0.5
    
    def get_search_stats(self) -> dict:
        """Get search statistics"""
        
        return {
            'total_searches': self.search_stats['total_searches'],
            'local_hits': self.search_stats['local_hits'],
            'chroma_hits': self.search_stats['chroma_hits'],
            'live_hits': self.search_stats['live_hits'],
            'avg_response_time': round(self.search_stats['avg_response_time'], 3),
            'cache_hit_rate': round(
                (self.search_stats['local_hits'] + self.search_stats['chroma_hits']) / 
                max(self.search_stats['total_searches'], 1) * 100,
                1
            ) if self.search_stats['total_searches'] > 0 else 0
        }


# Usage with all components
"""
from backend.services.scjn.bulk_downloader import SCJNBulkDownloader
from backend.services.scjn.puppeteer_scout import SCJNPuppeteerScout
from backend.services.scjn.hybrid_search import HybridSearchAdapter

async def main():
    # Initialize components
    bulk_downloader = SCJNBulkDownloader()
    puppeteer_scout = SCJNPuppeteerScout()
    # chroma_db = ChromaDBInstance()
    
    # Create unified search
    hybrid_search = HybridSearchAdapter(
        bulk_downloader=bulk_downloader,
        puppeteer_scout=puppeteer_scout,
        # chroma_db=chroma_db
    )
    
    # Unified search
    results = await hybrid_search.unified_search(
        "amparo laboral",
        materia="Laboral",
        sala="Primera"
    )
    print(f"Found {results['total_found']} results in {results['response_time']}s")
    print(f"Response time: {results['response_time']:.3f}s")
    print(f"Sources: {results['sources']}")
    
    # Get tesis detail
    tesis = await hybrid_search.get_tesis_detail("1a./J. 45/2023")
    
    # Validate citation (Itosturre feature)
    validation = await hybrid_search.validate_citation(
        "Tesis aislada 1a./J. 45/2023",
        context="En materia de amparo laboral..."
    )
    print(f"Citation status: {validation['status']} ({validation['confidence']:.1%})")
    
    # Get stats
    print(hybrid_search.get_search_stats())
"""
