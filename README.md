# Radar Local de Negocios y Vacantes

Sistema para **descubrir, registrar, enriquecer y visualizar** establecimientos de
comida, bebidas y hospitalidad dentro de una zona geográfica, y **detectar vacantes**
públicas cuando existan.

Zona inicial: **Cofradía de San Miguel, Cuautitlán Izcalli, Estado de México** (modificable en `config/zones.yaml`).

> Estado actual: **Fase 2 — Scaffolding** completada. Sin lógica de negocio todavía.
> La investigación y arquitectura está en [docs/FASE-1-Investigacion-Tecnica.md](docs/FASE-1-Investigacion-Tecnica.md).

---

## Principio: todo con planes gratuitos

| Servicio | Rol | Coste |
|---|---|---|
| OpenStreetMap / Overpass | Fuente **primaria** de negocios | Gratis |
| INEGI DENUE | Fuente **primaria** oficial (México) | Gratis |
| Google Places (New) | **Solo enriquecer**, con caché | Gratis dentro de caps por SKU |
| Jooble | Agregador de vacantes | Gratis, **500 peticiones DE POR VIDA por key** ⚠️ |
| PostgreSQL + PostGIS | Base de datos | Gratis (Docker local) |

⚠️ **Jooble:** el límite es de por vida, no mensual → se cachea toda petición y se
consultan **solo franquicias**. Suficiente para demostrar el pipeline en el MVP.

⚠️ **Google:** para no salir del free tier, OSM/DENUE son primarios y Google se usa
solo para completar fichas, con caché.

---

## Stack

Python 3.12 · FastAPI · PostgreSQL 16 + PostGIS · SQLAlchemy 2 + Alembic ·
proveedores intercambiables detrás de interfaces (`backend/app/providers/base.py`).

## Requisitos

- Python 3.12+
- Docker Desktop (para PostgreSQL + PostGIS)

## Puesta en marcha (desarrollo)

1. **Base de datos** (PostGIS en Docker):
   ```bash
   docker compose up -d
   docker compose exec db psql -U postgres -d radar -c "SELECT postgis_version();"
   ```

2. **Entorno de Python**:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Secretos**: copia `.env.example` a `.env` y rellena las claves.
   `.env` **nunca** se sube a git.

4. **API**:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   Verifica: http://localhost:8000/health → `{"status":"ok"}`
   Docs automáticas: http://localhost:8000/docs

   Endpoints: `GET /businesses` (filtros `latitude,longitude,radius,category,municipality,has_jobs,job_title,open_now,min_rating,order_by`), `GET /businesses/{id}` (ficha completa), `GET /jobs` (filtros `job_title,scope,status,business_id,chain_id,has_salary`), `GET /jobs/{id}`, `GET /zones`, `GET /stats`. Por defecto solo datos reales; `?include_demo=true` incluye la demo.

   **Dashboard HUD** (React + MapLibre, estética táctica/videojuego): ver [frontend/README.md](frontend/README.md).
   ```bash
   cd frontend && npm install
   npm run dev     # desarrollo -> http://localhost:5173
   npm run build   # produccion -> lo sirve FastAPI en http://localhost:8000/
   ```
   Mapa oscuro inmersivo, marcadores por estado, cámara cinematográfica al seleccionar un
   local y ficha glass con horarios, contacto, vacantes y fuentes. Usa datos DEMO por defecto
   (`USE_MOCK` en `frontend/src/data/api.ts`).

5. **Migraciones + datos DEMO** (con la BD Docker arriba):
   ```bash
   alembic upgrade head
   python scripts/seed_demo.py
   ```
   `seed_demo.py` es idempotente y solo toca datos marcados `is_demo=True`
   (nunca datos reales).

6. **Descubrimiento real** (OpenStreetMap, gratis, sin key):
   ```bash
   python scripts/run_discovery.py
   ```
   Geocodifica el centro de la zona (Nominatim), lo guarda y descubre negocios
   reales en el radio (Overpass), registrando la ejecución en `scans` y cada
   llamada en `source_requests`. Es idempotente (no duplica por `provider_place_id`).

7. **Deduplicación** (fusiona duplicados, registra decisiones en `match_log`):
   ```bash
   python scripts/run_dedup.py
   ```
   Solo fusiona coincidencias fuertes; las dudosas quedan como `manual_review`.
   Las fusiones son reversibles (`businesses.merged_into_id`).

8. **Enriquecimiento** (desde etiquetas OSM ya guardadas, sin llamadas nuevas):
   ```bash
   python scripts/run_enrich.py
   ```
   Completa tipo de comida, servicios, horarios y cadena/franquicia con su fuente
   y confianza. Lo que no existe queda en `NULL` (nunca se inventa).

9. **Vacantes**:
   ```bash
   python scripts/run_jobs_demo.py   # demo del pipeline sin red ni key
   python scripts/run_jobs.py        # real: requiere JOOBLE_API_KEY en .env
   ```
   Clasifica el puesto, parsea salario, deduplica por URL e infiere el alcance
   (sucursal / corporativa / ciudad_desconocida) sin afirmar de más.
   Jooble: key gratuita con **500 peticiones de por vida** → una consulta por franquicia.

10. **Escalado por grid** (áreas grandes por celdas + geohash, sin redundancia):
    ```bash
    python scripts/run_grid_demo.py
    ```
    Divide un bbox en celdas, escanea cada una, registra la cobertura en `scans`
    (con geohash) y omite celdas ya escaneadas hace poco. Zonas 2/3 en `config/zones.yaml`.

11. **Tareas programadas** (ver [docs/AUTOMATIZACION.md](docs/AUTOMATIZACION.md)):
    ```bash
    python scripts/run_task.py --list
    python scripts/run_task.py data_quality
    ```
    Cada ejecución se registra en `task_runs` (historial/observabilidad). Frecuencias
    sugeridas y recetas de agendado (Windows/cron/GitHub Actions) en el doc.

12. **Tests**:
    ```bash
    pytest
    ```

## Estructura

```
backend/app/
  api/         endpoints FastAPI
  core/        config (.env) y logging
  db/          base declarativa y sesión SQLAlchemy
  providers/   adaptadores intercambiables (google_places, openstreetmap, denue, jobs, search)
  pipeline/    etapas: discovery -> normalize -> dedup -> enrich -> job_detect -> snapshot
config/        zones.yaml (zona modificable, sin tocar código)
migrations/    Alembic (esquema en Fase 3)
scripts/       seeds y tareas CLI (Fase 3+)
docs/          informes y decisiones
```

## Seguridad

- Secretos solo en `.env` (ignorado por git). Nunca en código.
- Google Places API key: restringir por API (solo Places) y por IP/referrer.
- No se hace scraping de plataformas que lo prohíben (LinkedIn, Indeed, OCC, Computrabajo, Glassdoor).

## Roadmap por fases

- [x] Fase 1 — Investigación y arquitectura
- [x] Fase 2 — Scaffolding
- [x] Fase 3 — Base de datos (14 tablas, PostGIS, migración Alembic, modelos, seed DEMO)
- [x] Fase 4 — Descubrimiento geográfico (OSM/Overpass + geocoder Nominatim)
- [x] Fase 5 — Normalización y deduplicación (matching multi-señal, merge reversible, match_log)
- [x] Fase 6 — Enriquecimiento (tipo de comida, servicios, horarios, cadena; desde OSM, con fuente)
- [x] Fase 7 — Vacantes (pipeline Jooble + clasificación de puesto, alcance, dedup)
- [x] Fase 8 — API (businesses/jobs/zones/stats con filtros geográficos y de vacantes)
- [x] Fase 9 — Dashboard (mapa Leaflet + filtros + lista + ficha; servido por FastAPI)
- [x] Fase 10 — Automatizaciones (6 tareas, historial task_runs, manejo de errores)
- [x] Fase 11 — Producción (Docker, CI en GitHub Actions, /health/db, backups/seguridad; ver [docs/PRODUCCION.md](docs/PRODUCCION.md))
- [x] Fase 12 — Escalado (grid + geohash, cobertura por celda, omisión de redundantes)
```
