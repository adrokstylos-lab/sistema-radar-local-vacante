# Producción (Fase 11) — todo con planes gratuitos

## Hosting recomendado (gratis)

| Componente | Servicio (free tier) | Notas |
|---|---|---|
| Base de datos | **Supabase** (Postgres 16 + PostGIS) | PostGIS incluido; backups automáticos; free tier con pausa por inactividad. Alternativa: Neon. |
| API + Dashboard | **Render** (Web Service) o **Fly.io** | Contenedor desde el `Dockerfile`. La API sirve también el dashboard en `/`. Render free duerme por inactividad. |
| Tareas programadas | **GitHub Actions** (cron) | Ver `docs/AUTOMATIZACION.md`. Gratis para repos. |

> La API y el dashboard van juntos (mismo servicio), así que no hace falta hosting de frontend aparte.

## Despliegue con Docker

```bash
docker build -t radar .
docker run -p 8000:8000 -e DATABASE_URL=... -e JOOBLE_API_KEY=... radar
```
El contenedor aplica migraciones (`alembic upgrade head`) y arranca la API. En
Render/Fly se define el servicio a partir del `Dockerfile` y las variables de entorno.

## Variables de entorno / secretos

Definir en el panel del host (NUNCA en git). Ver `.env.example`:
- `DATABASE_URL` (de Supabase; formato `postgresql+psycopg://...`)
- `GOOGLE_PLACES_API_KEY`, `JOOBLE_API_KEY` (opcionales)
- `ENVIRONMENT=production`
- `CORS_ORIGINS` (solo si el frontend se sirviera desde otro dominio)

## Seguridad (checklist)
- [x] Secretos solo por variables de entorno; `.env` en `.gitignore`.
- [x] Sin claves en el código.
- [ ] Revocar y regenerar la API key de Google que se compartió en texto plano; restringirla por API (Places) e IP/referrer.
- [x] API de solo lectura (métodos GET); CORS restringido por `CORS_ORIGINS`.
- [x] Validación de entrada vía FastAPI/Pydantic.
- [ ] Poner la API detrás de HTTPS (lo dan Render/Fly).
- [ ] (Opcional) Rate limiting a nivel de gateway si se abre al público.

## Backups
- **Supabase**: backups automáticos diarios en el free tier.
- Manual (portátil):
  ```bash
  pg_dump "$DATABASE_URL_PG" -Fc -f backup_$(date +%F).dump   # usar la URL sin el sufijo +psycopg
  # restaurar: pg_restore -d "$DATABASE_URL_PG" backup_YYYY-MM-DD.dump
  ```

## Monitorización / observabilidad
- Salud: `GET /health` (app) y `GET /health/db` (conexión a BD).
- Uptime externo gratis: **UptimeRobot** apuntando a `/health`.
- Historial interno: tablas `task_runs` (ejecuciones), `scans` (cobertura),
  `source_requests` (costo/latencia/errores por proveedor).

## CI/CD
- `.github/workflows/ci.yml`: levanta PostGIS de servicio, aplica migraciones y
  corre `pytest` en cada push/PR. Gratis.
- Despliegue continuo: conectar el repo a Render/Fly para redeploy automático al
  hacer push a `main` (opcional).

## Rate limits y costos (recap)
- **OSM/Overpass, DENUE**: gratis; se controla el volumen con las frecuencias de Fase 10.
- **Google Places**: solo enriquecer, dentro de los caps gratis; cada llamada se
  registra en `source_requests` (control de costo).
- **Jooble**: 500 peticiones **de por vida** → `job_scan` semanal, una consulta por franquicia.
- Caché/observabilidad: `source_requests` evita repetir y permite auditar consumo.
