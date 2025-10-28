# 🕷️ SCJN Infrastructure for RepletO/Itosturre

## Overview

Complete SCJN jurisprudence extraction and search infrastructure for RepletO. Designed as the RAG backbone for Itosturre legal validator.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ITOSTURRE (Frontend)                     │
└────────────────────┬────────────────────────────────────────┘
                     │ Search Requests
        ┌────────────▼────────────┐
        │   RepletO API Gateway   │
        │  /api/v1/scjn/search    │
        └────────────┬────────────┘
                     │
        ┌────────────┴───────────────────────┐
        │                                    │
┌───────▼──────────┐            ┌──────────▼──────────┐
│  PUPPETEER SCOUT │            │  CHROMADB CACHE    │
│ (On-demand)      │            │ (Pre-indexed)      │
├──────────────────┤            ├────────────────────┤
│ • Fast searches  │            │ • Instant results  │
│ • Dynamic data   │            │ • Weekly updates   │
│ • Live SCJN      │            │ • Vectorized data  │
└────────┬─────────┘            └─────────┬──────────┘
         │                               │
         └───────────┬───────────────────┘
                     │
        ┌────────────▼──────────────┐
        │   SELENIUM CRAWLER        │
        │  (Weekly Sync - Monday)   │
        ├───────────────────────────┤
        │ • Full bulk extraction    │
        │ • All materias/salas      │
        │ • Pagination handling     │
        │ • JSON dump & vectorize   │
        └───────────────────────────┘
```

## Components

### 1. **Puppeteer Scout** (`puppeteer_scout.py`)
Real-time search using headless Chrome automation.

**Features:**
- Fast on-demand searches
- Dynamic web scraping
- Extract tesis details
- Pagination support
- Smart delay handling

**Usage:**
```python
async with SCJNPuppeteerContext() as scout:
    results = await scout.search_tesis(
        query="amparo laboral",
        materia="Laboral",
        sala="Primera",
        limit=20
    )
```

### 2. **Selenium Crawler** (`crawler.py`)
Weekly comprehensive bulk crawl of all SCJN data.

**Features:**
- All materia/sala combinations
- Pagination handling
- Full content extraction
- JSON export
- Detailed error logging

**Coverage:**
- Materias: Civil, Penal, Laboral, Fiscal, Constitucional, Administrativa, Mercantil
- Salas: Primera, Segunda, Pleno
- Years: Last 5 years (2020-2025)

### 3. **Sync Scheduler** (`scheduler.py`)
Automated weekly synchronization using APScheduler.

**Schedule:**
```
Monday 2 AM     → Full SCJN Crawl
Tuesday 2 AM    → Vectorization
Wednesday 2 AM  → Cache Validation
Daily 6 PM      → Quick Sync (new tesis only)
```

### 4. **API Endpoints** (`endpoints/scjn.py`)
FastAPI endpoints exposing SCJN search and validation.

**Endpoints:**
- `POST /api/v1/scjn/search` - Multi-source search
- `GET /api/v1/scjn/tesis/{registro}` - Get specific tesis
- `POST /api/v1/scjn/validate` - Validate citations (for Itosturre)
- `GET /api/v1/scjn/sources/status` - Check data freshness
- `POST /api/v1/scjn/sync/trigger` - Manual sync

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Key packages:
- `selenium` - Browser automation
- `pyppeteer` - Puppeteer for Python
- `beautifulsoup4` - HTML parsing
- `apscheduler` - Job scheduling
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings

### 2. Setup Chrome/Chromium
```bash
# Ubuntu
sudo apt-get install chromium-browser

# macOS
brew install chromium

# Windows
# Download from https://chromium.woolyss.com/
# Or use your existing Chrome installation
```

### 3. Initialize RepletO with SCJN
```python
# In main.py or startup

from backend.services.scjn import SCJNWeeklySyncScheduler

# Setup scheduler
scheduler = SCJNWeeklySyncScheduler()
await scheduler.start()
```

## Usage Examples

### Real-time Search
```bash
curl -X POST "http://localhost:8000/api/v1/scjn/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "amparo laboral derecho a la huelga",
    "materia": "Laboral",
    "sala": "Primera",
    "year": 2023,
    "limit": 20
  }'
```

### Get Specific Tesis
```bash
curl "http://localhost:8000/api/v1/scjn/tesis/1a./J. 45/2023"
```

### Validate Legal Text (Itosturre)
```bash
curl -X POST "http://localhost:8000/api/v1/scjn/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Conforme a la Primera Sala, jurisprudencia 45 del 2023..."
  }'
```

### Check Data Status
```bash
curl "http://localhost:8000/api/v1/scjn/sources/status"
```

### Trigger Manual Sync
```bash
# Quick sync (new tesis only)
curl -X POST "http://localhost:8000/api/v1/scjn/sync/trigger"

# Full crawl
curl -X POST "http://localhost:8000/api/v1/scjn/sync/trigger?full_crawl=true"
```

## Data Flow for Itosturre

```
Itosturre User Input
    │ "Amparo laboral por derecho a la huelga"
    │
    ▼
Itosturre Frontend
    │ POST /api/v1/scjn/search
    │
    ▼
RepletO SCJN Search
    │
    ├─→ Check ChromaDB Cache (if fresh)
    │   └─→ Return cached results (< 1s)
    │
    └─→ If not cached, Puppeteer Scout
        └─→ Live search on SCJN (2-5s)
        
        ▼
Results with Metadata
    │ - Registro SCJN
    │ - Título
    │ - Contenido completo
    │ - Ponente
    │ - Fecha
    │ - Vigencia
    │
    ▼
Itosturre Validator
    │ Applies semáforo logic
    │ 🟢 Vigente y verificada
    │ 🟡 Contradicción detectada
    │ 🔴 Superada o alucinación
    │
    ▼
User Gets Validated Result
    │ "Esta jurisprudencia es vigente ✅"
    │ "Puede usarse con confianza"
```

## Performance Characteristics

### Search Performance
- **Cached search:** ~200ms (ChromaDB)
- **Live search:** 2-5s (Puppeteer on SCJN)
- **Bulk crawl:** ~30-60 minutes (full week of data)

### Storage
- Full SCJN dump: ~500MB-1GB (JSON)
- Vectorized in ChromaDB: ~2-5GB (with embeddings)

### Scaling
- Can handle 10,000+ concurrent searches (with proper infrastructure)
- Weekly sync can be parallelized by materia

## Configuration

### Environment Variables
```bash
# Puppeteer
PUPPETEER_HEADLESS=true
PUPPETEER_TIMEOUT=30

# Selenium
SELENIUM_HEADLESS=true
SELENIUM_TIMEOUT=30

# Scheduler
SCJN_SYNC_ENABLED=true
SCJN_SYNC_MONDAY=02:00
SCJN_SYNC_DAILY=18:00
```

### Scheduler Customization
Edit `scheduler.py` to modify:
- Sync schedule times
- Materia/sala/year combinations
- Data export formats
- Error retry strategies

## Troubleshooting

### Browser Not Found
```
Error: Failed to launch chrome
Solution: Install chromium or set CHROME_PATH
```

### Rate Limiting
```
Error: 429 Too Many Requests
Solution: Increase delays in crawler.py and puppeteer_scout.py
```

### Memory Issues
```
Error: Out of memory during crawl
Solution: 
1. Reduce browser instances
2. Close browsers after each batch
3. Stream JSON instead of loading all in memory
```

### ChromaDB Issues
```
Error: ChromaDB connection failed
Solution: Ensure ChromaDB service is running
```

## Integration with Itosturre

Itosturre legal validator consumes these endpoints:

1. **Citation Extraction** → `/api/v1/scjn/validate`
2. **Result Fetching** → `/api/v1/scjn/search`
3. **Specific Lookup** → `/api/v1/scjn/tesis/{registro}`
4. **Status Monitoring** → `/api/v1/scjn/sources/status`

Semáforo validation happens in Itosturre layer, not RepletO.

## Next Steps

- [ ] Implement PostgreSQL + pgvector for production scale
- [ ] Add caching layer (Redis)
- [ ] Implement rate limiting and request queuing
- [ ] Add DOF (Diario Oficial) integration
- [ ] Implement local data import/custom data
- [ ] Add full-text search capabilities
- [ ] Implement GraphQL API

## Contributing

When adding new features:
1. Follow the existing patterns (Scout for live, Crawler for bulk)
2. Add tests in `tests/test_scjn_*.py`
3. Update documentation
4. Ensure backward compatibility with Itosturre

## License

MIT - Part of RepletO/Itosturre ecosystem
