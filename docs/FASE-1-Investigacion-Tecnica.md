# Radar Local de Negocios y Vacantes
## FASE 1 — Informe de Investigación Técnica y Arquitectura

> **Estado:** Investigación. **No hay código todavía.** Este documento se detiene antes de la implementación y espera la instrucción `CONTINUAR FASE 2`.
> **Fecha:** 2026-09-09 · **Zona inicial:** Cofradía de San Miguel, Cuautitlán Izcalli, Estado de México, México.

---

## A. Viabilidad

### ¿Se puede construir?
**Sí, con matices importantes.** El sistema se divide en dos mitades con viabilidad muy distinta:

| Mitad | Viabilidad | Motivo |
|---|---|---|
| **Descubrimiento y datos de negocios** | 🟢 Alta | Existen APIs oficiales maduras (Google Places, OSM/Overpass, Foursquare, HERE) con datos geográficos estructurados y legales de usar. |
| **Detección de vacantes** | 🟡 Media / parcial | No existe una API única y legal que cubra Indeed, OCC, Computrabajo, LinkedIn, etc. La mayoría prohíbe scraping en sus Términos. La cobertura será **incompleta por diseño** y variable por establecimiento. |

### ¿Qué tan completo puede ser?
- **Negocios:** se puede alcanzar una cobertura muy alta (estimo 85–95% de los establecimientos con presencia digital en la zona) combinando 2 fuentes de mapas. Los negocios sin presencia en internet (fondas pequeñas, food trucks informales) simplemente no son detectables por medios automáticos: esa es la frontera dura.
- **Vacantes:** cobertura **oportunista, no exhaustiva**. Realista:
  - Cadenas/franquicias (McDonald's, Starbucks, OXXO): buena, tienen portales de empleo estructurados.
  - PyMEs independientes: baja. Publican en Facebook, en un cartel físico o de boca en boca. Muchas vacantes **no existen en internet** y por tanto son indetectables.

### Limitaciones estructurales (que ninguna cantidad de ingeniería resuelve)
1. **El dato no siempre existe.** Un negocio real sin web, sin redes y sin ficha en Google es invisible. El sistema debe reportar `NULL`/`desconocido`, no inventar.
2. **Las bolsas de empleo son adversariales.** LinkedIn, Indeed y Glassdoor bloquean activamente el scraping (legal y técnicamente). Depender de scrapearlas es construir sobre arena.
3. **Los datos caducan.** Horarios, teléfonos y vacantes cambian. El valor del sistema depende del *refresco*, no de una foto única. Esto es un costo recurrente, no puntual.
4. **Atribución de vacante ↔ sucursal.** Una vacante "Mesero – McDonald's" rara vez dice *qué* sucursal. Distinguir la sucursal de Cofradías de otra de Cuautitlán es el problema más difícil del proyecto y a menudo irresoluble con certeza.

**Conclusión de viabilidad:** El MVP es plenamente viable y aporta valor real como "radar de negocios + señal de empleo donde exista". Vender el sistema como "censo completo de todas las vacantes" **no** es viable y no se debe prometer.

---

## B. Fuentes de datos — Tabla comparativa

### B.1 Fuentes de NEGOCIOS (mapas / lugares)

| Fuente | API oficial | Cuenta / Auth | Límites | Costo | Calidad datos | Conveniencia |
|---|---|---|---|---|---|---|
| **Google Places (New)** | ✅ Sí | API key + billing | Cap gratis por SKU/mes (Pro: 5.000) | Nearby/Text $32/1k · Details $17/1k | 🟢 La mejor para MX: nombre, tel, web, horarios, rating, reseñas, estado | 🟢 Alta, pero la más cara |
| **OpenStreetMap + Overpass** | ✅ Sí (Overpass) | No requiere key (instancia pública) | Rate limit "justo"; mejor instancia propia | **Gratis** (dato abierto ODbL) | 🟡 Variable: buena geometría/categoría, floja en tel/web/horarios en zonas de MX | 🟢 Ideal como base gratuita |
| **Foursquare Places** | ✅ Sí | API key | Free tier generoso | Free + planes de pago | 🟡 Buena en POI y categorías; menor densidad en MX suburbano | 🟡 Buen complemento |
| **HERE Places** | ✅ Sí | API key | ~1k tx/día free | Pago por volumen | 🟡 Sólida, orientada a automoción/logística | 🟡 Alternativa |
| **Mapbox** | ✅ (Search/Geocoding) | Token | Free tier | Pago por volumen | 🟡 Geocoding bueno; POI menos rico que Google | 🟢 Bueno para **mapa** del dashboard |
| **SerpAPI (Google Maps)** | ✅ (wrapper) | API key de pago | Por plan | ~$50+/mes | 🟡 Devuelve resultados de Google Maps sin tocar su API directa | 🟡 Caro; útil puntualmente |
| **Apify (actores Maps/empleo)** | ✅ (plataforma) | Cuenta + créditos | Por consumo | Pago por uso | 🟡 Scraping "as a service"; traslada el riesgo de TOS al operador | 🟠 Zona gris legal |
| **INEGI DENUE** | ✅ Sí (API) | Token gratuito | Amplio | **Gratis** | 🟢 Censo oficial de establecimientos de México (¡muy relevante!) | 🟢 **Infravalorado, debe incluirse** |

> 💡 **Hallazgo clave:** el **DENUE del INEGI** es un directorio estadístico oficial y gratuito de unidades económicas de México, con giro (SCIAN), nombre y ubicación. Es una fuente base excelente y **legalmente limpia** para México que el encargo original no menciona. Recomiendo incorporarla.

### B.2 Fuentes de VACANTES

| Fuente | API oficial | Scraping permitido | Costo | Notas legales / prácticas |
|---|---|---|---|---|
| **Sitio oficial / careers del negocio** | A veces (feeds) | Depende del `robots.txt` de cada sitio | Gratis | 🟢 La fuente más limpia y de mayor confianza. Franquicias suelen tener portal (p.ej. workday, ATS). |
| **Google (búsqueda) + Google Jobs** | Vía SerpAPI (no oficial de Google) | Google Jobs no tiene API pública | SerpAPI de pago | 🟡 Google agrega ofertas; útil como índice, pero acceso indirecto. |
| **LinkedIn** | ❌ (API cerrada a partners) | ❌ **Prohibido** por TOS; bloqueo agresivo | — | 🔴 No scrapear. Riesgo legal (caso *hiQ* matizado) y técnico alto. |
| **Indeed** | ⚠️ API de publisher **descontinuada/restringida** | ❌ Prohibido | — | 🔴 Evitar scraping. |
| **OCC Mundial** | ❌ | ❌ TOS lo prohíbe | — | 🟠 Popular en MX; solo vía partnership o manual. |
| **Computrabajo** | ❌ | ❌ | — | 🟠 Muy usado en MX; misma restricción. |
| **Glassdoor** | ⚠️ API limitada (reviews) | ❌ | — | 🔴 Bloqueo fuerte. |
| **Jooble / Talent.com / Adzuna / Careerjet** | ✅ **Algunas tienen API/afiliados** | N/A | Free/afiliado | 🟢 **Agregadores con API son la vía legal**. Adzuna y Jooble ofrecen API de partner; cobertura MX parcial pero utilizable. |
| **Facebook / Instagram (Jobs, posts)** | ⚠️ Graph API muy restringida | ❌ scraping prohibido | — | 🟠 FB Jobs se ha reducido; acceso a posts públicos es limitado. Alto valor para PyMEs pero difícil y arriesgado. |

**Regla de oro aplicada (punto 6 del encargo):** para cada plataforma sin API oficial y con scraping prohibido → **NO se scrapea**. Se prioriza: (1) API oficial → (2) agregador con API (Adzuna/Jooble) → (3) sitio propio del negocio respetando `robots.txt` → (4) descubrimiento manual asistido. LinkedIn/Indeed/OCC/Computrabajo/Glassdoor entran en la lista de "no automatizar sin acuerdo".

**Sources:** [CP y coords de Cofradía de San Miguel](https://micodigopostal.org/estado-de-mexico/cuautitlan-izcalli/cofradia-de-san-miguel/) · [roadonmap – coordenadas](https://www.roadonmap.com/mx/donde-est%C3%A1/Cofradia_de_San_Miguel-Cuautitlan_Izcalli,estado_de_mexico/) · [Google Maps Platform – lista de precios](https://developers.google.com/maps/billing-and-pricing/pricing) · [Places API usage & billing](https://developers.google.com/maps/documentation/places/web-service/usage-and-billing)

---

## C. Arquitectura recomendada

La cadena lineal propuesta en el encargo es correcta conceptualmente, pero acoplada. Recomiendo la **misma secuencia lógica** reorganizada como **pipeline por etapas desacopladas mediante una base de datos como estado central + una cola de trabajos**. Esto da reintentos, idempotencia y observabilidad sin sobreingeniería.

```
                 ┌────────────────────────────────────────────┐
                 │        CONFIG DE ZONA (geographic_zones)     │
                 │  centro/polígono/radio · modificable         │
                 └───────────────────┬──────────────────────────┘
                                     │
   ┌──────────────── PIPELINE (jobs/tareas, orquestado por scheduler) ─────────────┐
   │                                                                               │
   │  [1] DISCOVERY      → PlaceProvider.search  (Google/OSM/DENUE)                 │
   │        │              guarda raw + source_requests (auditoría/costo)          │
   │        ▼                                                                       │
   │  [2] NORMALIZE      → limpia nombre, dirección, categoría → nombre_normalizado │
   │        ▼                                                                       │
   │  [3] DEDUPLICATE    → matching multi-señal + confidence → merge trazable       │
   │        ▼                                                                       │
   │  [4] ENRICH         → web oficial, redes, clasificación (SearchProvider)       │
   │        ▼              cada dato con {fuente, fecha, confianza}                 │
   │  [5] JOB DETECT     → JobProvider (careers + agregadores con API)              │
   │        ▼              normaliza · dedup · valida estado (activa/vencida)       │
   │  [6] SNAPSHOT       → business_snapshots / job_snapshots (historial)           │
   │                                                                               │
   └───────────────────────────────┬───────────────────────────────────────────────┘
                                    ▼
                       ┌────────────────────────┐
                       │  PostgreSQL + PostGIS    │  ← estado central + historial
                       └───────────┬─────────────┘
                                   ▼
                       ┌────────────────────────┐
                       │   API propia (REST)     │
                       └───────────┬─────────────┘
                          ┌────────┴─────────┐
                          ▼                  ▼
                   Dashboard + Mapa       Alertas
```

**Diferencias frente a la propuesta original y por qué:**
1. **La base de datos es el bus de estado**, no el último eslabón. Cada etapa lee/escribe estado y puede reintentarse sola. Un fallo en "vacantes" no pierde lo descubierto.
2. **Etapas idempotentes disparadas por scheduler**, no un flujo monolítico. Permite frecuencias distintas por etapa (punto 18) y control de costos (punto 19).
3. **`source_requests` es transversal**, envuelve toda llamada externa (caché + costo + rate limit), no un paso al final.
4. **Cola de trabajos ligera:** en el MVP basta una tabla `tasks` en Postgres (patrón *outbox/queue en DB*) — **no** se necesita Redis/RabbitMQ todavía. Se añade cuando el volumen lo exija (Fase 11/12).
5. **Providers detrás de interfaces** (punto 25): el pipeline no conoce a Google ni a OSM, solo la interfaz `PlaceProvider`.

---

## D. Stack recomendado

| Capa | Recomendación | Por qué (vs. alternativas) |
|---|---|---|
| **Lenguaje backend** | **Python 3.12** | Mejor ecosistema para datos/scraping/geo (pandas, shapely, rapidfuzz, httpx). Curva suave. Node/TS sería válido pero Python gana en ETL y librerías de matching. |
| **Framework API** | **FastAPI** | Async, tipado con Pydantic (encaja con "validar entradas"), OpenAPI automático, docs gratis. |
| **Base de datos** | **PostgreSQL 16 + PostGIS** | Consultas geoespaciales reales (radio, polígono, distancia, KNN) que SQLite no da bien. JSONB para datos semiestructurados. Es la pieza que **no** hay que escatimar. |
| **BD desarrollo** | **PostgreSQL local (Docker)**, no SQLite | PostGIS no está en SQLite; usar Postgres desde el día 1 evita divergencias dev/prod. Docker Compose lo hace trivial. |
| **ORM/migraciones** | **SQLAlchemy 2.0 + Alembic** (+ `geoalchemy2`) | Estándar, migraciones versionadas (punto Fase 3). |
| **Cliente HTTP** | **httpx** + **tenacity** (retries) | Async, timeouts, reintentos con backoff (observabilidad, punto 20). |
| **Matching/dedup** | **rapidfuzz** + **libpostal/usaddress** + **shapely** | Similitud de texto rápida + parsing de direcciones + distancia geo. |
| **Scheduler** | **APScheduler** (MVP) → **GitHub Actions cron** / **cron del host** | Simple al inicio; n8n es potente pero añade una pieza pesada innecesaria en el MVP. |
| **Frontend** | **Next.js (React) + TypeScript** | SSR, buen DX, despliegue fácil en Vercel. |
| **Mapa** | **MapLibre GL + teselas OSM/Mapbox** o **Leaflet** | Evita atar el dashboard a la facturación de Google Maps JS. Leaflet si se prioriza simplicidad. |
| **Hosting BD** | **Supabase** (Postgres+PostGIS gestionado, free tier) o **Railway** | Free tier real, PostGIS disponible, backups. |
| **Hosting API** | **Railway / Render / Fly.io** | Contenedor Python barato; free/hobby tier. |
| **Hosting frontend** | **Vercel** | Gratis para Next.js. |
| **Secretos** | **.env local + gestor de secretos del host** | Nunca en git (punto 21). |

**Un stack, una frase:** *Python + FastAPI + PostgreSQL/PostGIS en el backend; Next.js + MapLibre en el frontend; todo con proveedores intercambiables detrás de interfaces.* Cumple prioridades del punto 8: bajo costo inicial (todo tiene free tier), fácil de aprender, mantenible, escalable y bien documentado.

---

## E. Costos estimados

Supuestos: 1 negocio "descubierto y enriquecido" ≈ **1 Nearby/Text Search compartida entre varios negocios** + **1 Place Details** por negocio nuevo. Refrescos posteriores = solo Details. Precios Google verificados (sep-2026): Nearby/Text **$32/1k**, Place Details Pro **$17/1k**; caps gratis mensuales por tier (Pro 5.000 eventos, Essentials 10.000).

| Escenario | Estrategia | Costo APIs de mapas | Comentario |
|---|---|---|---|
| **MVP (validación)** | OSM/Overpass + DENUE (gratis) como base; Google solo para enriquecer ~100 fichas | **~$0–5** (dentro de caps gratis) | El MVP puede correr **casi gratis** si se usa OSM/DENUE primero y Google con moderación. |
| **100 negocios** | ~100 Details + ~15 búsquedas de grid | 115 llamadas → **dentro del free tier** = **$0** | Trivial. |
| **1.000 negocios** | ~1.000 Details + ~80 búsquedas de grid | ~1.080 eventos/mes → **dentro de caps gratis** = **~$0** | Aún gratis si se distribuye en el mes; picos podrían costar centavos. |
| **10.000 negocios** | 10.000 Details + ~600 búsquedas | Details: (10.000−5.000)×$17/1k = **$85** + búsquedas (600 gratis) ≈ **$85 una vez** (alta inicial) | El costo real recurrente es el **refresco**: refrescar 10k negocios 1×/mes ≈ (10.000−5.000)×$17/1k = **~$85/mes**. Con OSM/DENUE para lo que no requiera Google, baja. |

**Costos NO-Google a considerar:**
- **Vacantes vía agregadores (Adzuna/Jooble):** free/afiliado en volúmenes bajos; SerpAPI si se usa ≈ $50/mes plan básico.
- **Hosting:** $0 en free tiers al inicio; ~$5–20/mes al escalar (Railway/Render + Supabase Pro).
- **Geocoding:** $5/1k con 10k gratis/mes → normalmente $0 al inicio.

**Conclusión de costos:** el proyecto **arranca esencialmente gratis** y el costo crece con el *refresco* y el volumen de Google Details. Priorizar OSM/DENUE mantiene el costo cerca de cero hasta bien entrado el escalado.

---

## F. Riesgos

### Técnicos
- **Deduplicación imperfecta:** falsos merges (dos negocios distintos fusionados) o duplicados no detectados. *Mitigación:* umbrales de confianza + nunca fusionar "dudoso" automáticamente + trazabilidad total.
- **Atribución vacante→sucursal ambigua.** *Mitigación:* marcar `scope` (corporativa/sucursal/ciudad-desconocida) y no afirmar más de lo que el dato permite.
- **Datos obsoletos** (horarios, cierres). *Mitigación:* `last_verified_at` + snapshots + jobs de refresco con frecuencia por tipo.

### Legales / de cumplimiento
- **TOS de bolsas de empleo y de Google.** Scrapear LinkedIn/Indeed/OCC/Computrabajo viola sus términos y puede implicar responsabilidad. *Mitigación:* **no scrapear**; usar APIs/agregadores; respetar `robots.txt`; almacenar solo lo necesario.
- **Caché de Google Places:** su TOS restringe el almacenamiento prolongado de ciertos campos (place_id se puede guardar; otros datos tienen límites de caché). *Mitigación:* guardar `place_id` como ancla y refrescar campos según reglas; documentar la política.
- **Datos personales (LFPDPPP en MX):** teléfonos/correos de negocios suelen ser públicos, pero conviene tratar contacto como dato sensible y no exponerlo indebidamente.

### APIs / operativos
- **Cambios de precios de Google** (ya cambió el modelo en marzo 2025). *Mitigación:* arquitectura provider-agnóstica → poder migrar a OSM/HERE.
- **Rate limits y bloqueos.** *Mitigación:* caché, backoff, `source_requests`.
- **Dependencia de agregadores de empleo** con cobertura MX parcial. *Mitigación:* diseñar para "cobertura parcial es aceptable".

### Scraping (cuando sea inevitable y legal)
- Frágil ante cambios de HTML; posible bloqueo por IP. *Mitigación:* limitarlo a sitios propios de negocios que lo permitan; nunca como fuente primaria.

---

## G. Diseño del MVP (qué se construye primero)

**Objetivo del MVP:** *Descubrir los negocios de Cofradía de San Miguel, guardarlos deduplicados con su fuente e historial, y mostrarlos en una lista/mapa simple — con un enganche mínimo de detección de vacantes solo para franquicias con portal.*

**Incluye:**
1. Config de zona modificable (`geographic_zones`) con Cofradía de San Miguel como registro inicial.
2. **Un** `PlaceProvider` funcionando: **OSM/Overpass** (gratis) como primario + **Google Places** opcional para enriquecer.
3. Normalización + deduplicación con confidence score y merge trazable.
4. Enriquecimiento básico: web y redes (heurístico), clasificación de categoría.
5. Detección de vacantes **mínima**: solo careers de franquicias conocidas + **un** agregador con API (Adzuna o Jooble). Demostrar que el pipeline funciona, no cubrir todo.
6. Persistencia PostgreSQL+PostGIS con snapshots y `source_requests`.
7. API REST mínima: `GET /businesses`, `/businesses/:id`, `/jobs`, `/zones`, `/stats`.
8. Dashboard mínimo: lista + mapa + filtro por categoría y "tiene vacantes".

**NO incluye (fases posteriores):** múltiples proveedores de empleo, alertas, refrescos automáticos avanzados, autenticación de usuarios, escalado a municipio/estado.

**Criterio de éxito del MVP:** poder abrir el dashboard, ver los negocios de Cofradía de San Miguel clasificados, con al menos una franquicia mostrando una vacante real detectada por el pipeline, y cada dato mostrando su fuente y fecha.

---

## Modelo de datos preliminar

Relacional, PostgreSQL + PostGIS. Claves, FKs, índices y `timestamptz` en todas las tablas. Coordenadas como `geography(Point,4326)`.

- **`geographic_zones`** — `id`, `name`, `municipality`, `state`, `country`, `center geography(Point)`, `radius_m`, `polygon geography(Polygon)` (nullable), `is_active`, timestamps. *(la zona vive aquí, no en código)*
- **`businesses`** — `id`, `normalized_name`, `display_name`, `primary_category`, `secondary_categories jsonb`, `description`, `chain_id` (FK nullable a `chains`), `status` (activo/cerrado_temp/cerrado_perm/desconocido), `last_verified_at`, `confidence`, timestamps.
- **`business_locations`** — `id`, `business_id` FK, `full_address`, `colonia`, `municipality`, `state`, `postal_code`, `country`, `geog geography(Point)`, `map_url`, `provider_place_id`. Índice **GiST** en `geog`.
- **`business_hours`** — `id`, `business_id` FK, `day_of_week`, `open_time`, `close_time`, `source`, `confidence`.
- **`business_contacts`** — `id`, `business_id` FK, `type` (phone/whatsapp/web/email/facebook/instagram/tiktok/linkedin/otro), `value`, `source`, `confidence`, `verified_at`. *(un renglón por dato de contacto → flexible)*
- **`business_sources`** — `id`, `business_id` FK, `provider`, `provider_place_id`, `raw jsonb`, `fetched_at`. *(de dónde salió cada negocio)*
- **`business_snapshots`** — `id`, `business_id` FK, `snapshot jsonb`, `diff jsonb`, `created_at`. *(historial: antes/después)*
- **`chains`** — `id`, `name`, `normalized_name`, `careers_url`, `ats_type`. *(franquicias)*
- **`jobs`** — `id`, `business_id` FK (nullable si aún no atribuida), `chain_id` FK nullable, `title`, `title_category` (mesero/cocinero/…), `description`, `salary_min`, `salary_max`, `currency`, `salary_period`, `schedule`, `shift`, `requirements jsonb`, `experience`, `education`, `address`, `modality`, `posted_at`, `detected_at`, `last_verified_at`, `source`, `source_url`, `contact jsonb`, `status` (activa/posible/vencida/eliminada/desconocido), `scope` (sucursal/corporativa/ciudad_desconocida), `confidence`.
- **`job_sources`** — `id`, `job_id` FK, `provider`, `raw jsonb`, `fetched_at`.
- **`job_snapshots`** — `id`, `job_id` FK, `snapshot jsonb`, `created_at`. *(apareció/desapareció)*
- **`scans`** — `id`, `zone_id` FK, `provider`, `strategy` (radio/grid/poligono), `area_covered jsonb`, `started_at`, `finished_at`, `results_count`, `errors jsonb`, `status`.
- **`source_requests`** — `id`, `provider`, `endpoint`, `request_hash`, `response_cached bool`, `cost_estimate`, `status_code`, `latency_ms`, `created_at`. *(costo + caché + observabilidad)*
- **`match_log`** — `id`, `business_a`, `business_b`, `signals jsonb`, `score`, `decision` (auto_merge/manual_review/rejected), `created_at`. *(trazabilidad de dedup — nada dudoso se fusiona sin registro)*

---

## Estrategia geográfica

- **Cofradía de San Miguel** (verificado): centro aproximado **19.683° N, −99.215° W**, CP **54715**. ⚠️ Coordenada a confirmar con geocoder oficial antes de fijarla (punto 26 exige no asumir).
- **MVP:** **búsqueda por radio** desde el centro (radio ~1.5–2 km cubre la colonia). Simple y suficiente.
- **Escalado a municipio/estado:** **grid adaptativo** — dividir el área en celdas; densificar celdas con muchos resultados (Google limita ~20 resultados por búsqueda, obligando a subdividir). **Geohash** como clave de celda para deduplicar cobertura.
- **Anti-redundancia:** registrar en `scans` el área ya cubierta (polígono/celdas) y no re-consultar celdas recientes salvo refresco programado.

---

## Estrategia de deduplicación

**Señales (en orden de fuerza):**
1. `provider + place_id` idéntico → **coincidencia exacta**.
2. Teléfono normalizado idéntico → exacta/probable.
3. Dominio web idéntico → probable.
4. `nombre_normalizado` + distancia geográfica < 75 m → probable.
5. Similitud de nombre (rapidfuzz ≥ 0.9) + < 150 m → dudosa.
6. Redes sociales idénticas → probable.

**Niveles de confianza y acción:**
| Nivel | Umbral | Acción |
|---|---|---|
| Exacta | place_id o teléfono/dominio igual | Merge automático + registro en `match_log`. |
| Probable | señales fuertes combinadas | Merge automático **con** `match_log`, reversible. |
| Dudosa | solo similitud de texto/proximidad | **Cola de revisión manual**, nunca merge automático. |

Ejemplo "McDonald's / McDonalds / McDonald's Cofradías": mismo `chain_id`, pero se distinguen por `place_id`/coordenadas → se mantienen como sucursales separadas, no se fusionan.

---

## Estrategia de vacantes

Pipeline por establecimiento, **priorizando legalidad**:
1. Si tiene `chain_id` con `careers_url` → consultar portal/ATS de la franquicia (fuente de **alta** confianza).
2. Consultar **agregador con API** (Adzuna/Jooble) filtrando por empresa + zona.
3. Sitio propio del negocio (`/careers`, `/empleo`, `/trabaja-con-nosotros`) respetando `robots.txt`.
4. Normalizar → mapear a `title_category` (mesero, cocinero…) → deduplicar → validar estado.
5. **Distinguir** vacante activa / vencida / duplicada / de otra sucursal / corporativa → campo `scope` + `confidence`. Nunca afirmar sucursal sin evidencia.
6. Guardar `job_snapshots` para saber cuándo apareció y desapareció.

**Excluidas de automatización** (solo con acuerdo/manual): LinkedIn, Indeed, OCC, Computrabajo, Glassdoor.

---

## Estructura futura del proyecto (referencia, se crea en Fase 2)

```
sistema-de-vacantes/
├── README.md
├── .env.example            # nunca .env real en git
├── docker-compose.yml      # postgres+postgis local
├── config/
│   └── zones.yaml          # zona inicial modificable
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers
│   │   ├── core/          # config, logging, settings
│   │   ├── db/            # modelos SQLAlchemy, sesión
│   │   ├── pipeline/      # discovery, normalize, dedup, enrich, jobs
│   │   ├── providers/     # ← adaptadores intercambiables
│   │   │   ├── base.py            # interfaces PlaceProvider/JobProvider/…
│   │   │   ├── google_places/
│   │   │   ├── openstreetmap/
│   │   │   ├── denue/
│   │   │   ├── jobs/              # adzuna/, jooble/, careers/
│   │   │   └── search/
│   │   └── services/
│   └── tests/
├── migrations/             # Alembic
├── scripts/                # seeds, tareas CLI
├── docs/                   # este informe y decisiones (ADR)
└── logs/
```

Interfaces (punto 25): `PlaceProvider.search_places()/get_place_details()`, `JobProvider.search_jobs()/get_job_details()`, `SearchProvider.search_web()`, `GeocoderProvider.geocode()/reverse_geocode()`. El pipeline depende solo de estas interfaces → proveedores sustituibles sin reescribir.

---

## DECISIONES PROPUESTAS

1. **Stack:** Python 3.12 + FastAPI + PostgreSQL 16/PostGIS + Next.js/TypeScript + MapLibre. Docker Compose para dev.
2. **Postgres desde el día 1** (no SQLite) por PostGIS; Supabase/Railway para hosting con free tier.
3. **Fuentes de negocios en el MVP:** OSM/Overpass + INEGI DENUE (gratis) como base; Google Places solo para enriquecer. → arranque casi sin costo.
4. **Incorporar DENUE (INEGI)** como fuente oficial gratuita (no estaba en el encargo, aporta mucho en México).
5. **Vacantes:** empezar con careers de franquicias + **un** agregador con API (Adzuna o Jooble). **No scrapear** LinkedIn/Indeed/OCC/Computrabajo/Glassdoor.
6. **Arquitectura:** pipeline por etapas idempotentes con Postgres como estado central y una tabla `tasks` como cola (sin Redis por ahora).
7. **Principios duros:** `NULL` en vez de inventar; cada dato con `{fuente, fecha, confianza}`; dedup dudosa nunca automática; todo cambio a `snapshots`.
8. **Zona en configuración** (`geographic_zones` + `config/zones.yaml`), Cofradía de San Miguel como registro inicial con coordenada a confirmar.

---

## PREGUNTAS ABIERTAS
*(solo lo que realmente necesita tu decisión; para todo lo demás aplicaré las Decisiones Propuestas)*

1. **Google Places en el MVP:** ¿configuro el proyecto para usar Google Places desde ya (necesitarías crear una API key y activar billing, aunque el costo sea ~$0 en free tier), o arranco **solo con OSM + DENUE** y dejamos Google para más adelante? *(Recomiendo: solo OSM+DENUE en el MVP.)*
2. **Agregador de empleo:** ¿tienes preferencia o cuenta en **Adzuna** o **Jooble**? Si no, elijo yo el que tenga mejor cobertura MX y API gratuita.
3. **Postura ante scraping:** confirmo que **no** scrapearemos plataformas que lo prohíben (LinkedIn/Indeed/OCC/Computrabajo). ¿De acuerdo, o quieres explorar acuerdos/uso manual para alguna?
4. **Alcance de vacantes:** ¿aceptas que la cobertura de vacantes de PyMEs independientes será **parcial** (muchas no están en internet), y que el sistema priorizará franquicias al inicio?
5. **Coordenada de la zona:** ¿confirmo el centro de Cofradía de San Miguel con un geocoder oficial en Fase 4, o me pasas tú un punto/polígono exacto?
6. **Docker:** ¿tienes Docker Desktop instalado en esta máquina Windows? Es la vía más limpia para Postgres+PostGIS en local. Si no, propongo alternativa.

---

## DETENTE

**No escribiré código todavía.** Quedo a la espera de tu instrucción:

> **CONTINUAR FASE 2**

(idealmente acompañada de tus respuestas a las Preguntas Abiertas; si no respondes, aplicaré las Decisiones Propuestas por defecto).
