# Automatización (Fase 10)

Tareas programables vía `scripts/run_task.py`. Cada ejecución queda registrada en
la tabla `task_runs` (nombre, inicio/fin, estado, stats, error) para observabilidad.

## Tareas y frecuencias sugeridas

| Tarea | Qué hace | Frecuencia sugerida | Motivo |
|---|---|---|---|
| `discovery_scan` | Descubre negocios nuevos (OSM) | **Semanal** | Los negocios aparecen despacio; OSM es gratis. |
| `business_refresh` | Enriquecimiento + deduplicación | **Semanal** | Mantiene fichas al día sin costo. |
| `job_scan` | Vacantes reales (Jooble) por franquicia | **Semanal** | ⚠️ Jooble = 500 peticiones **de por vida**; diario la agotaría. |
| `job_refresh` | Marca vacantes viejas como vencidas | **Cada 3 días** | Solo BD, gratis. |
| `closure_check` | Reporta negocios sin verificar hace mucho | **Mensual** | No cierra automáticamente (evita falsos cierres). |
| `data_quality` | Reporte de completitud | **Semanal** | Solo BD, gratis. |

```bash
python scripts/run_task.py --list          # ver tareas
python scripts/run_task.py data_quality    # ejecutar una
```

## Agendado

### Windows (Programador de tareas)
Crea una tarea básica que ejecute (ajusta rutas):
```
C:\Users\aleja\sistema de vacantes\venv\Scripts\python.exe C:\Users\aleja\sistema de vacantes\scripts\run_task.py data_quality
```
Configura el disparador (semanal/mensual) según la tabla. Repite por tarea.

### Linux/Mac (cron)
```cron
# m h dom mon dow  comando
0 3 * * 1  cd /ruta/proyecto && ./venv/bin/python scripts/run_task.py discovery_scan   # lunes 03:00
0 4 * * 1  cd /ruta/proyecto && ./venv/bin/python scripts/run_task.py business_refresh
0 5 * * 1  cd /ruta/proyecto && ./venv/bin/python scripts/run_task.py job_scan
0 2 */3 * * cd /ruta/proyecto && ./venv/bin/python scripts/run_task.py job_refresh
```

### GitHub Actions (cuando la BD esté en la nube, Fase 11)
```yaml
on:
  schedule:
    - cron: "0 3 * * 1"   # UTC
jobs:
  discovery:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - run: pip install -r requirements.txt
      - run: python scripts/run_task.py discovery_scan
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          JOOBLE_API_KEY: ${{ secrets.JOOBLE_API_KEY }}
```

## Manejo de errores
- `run_task` hace rollback y registra estado `error` con el mensaje; nunca deja el
  sistema a medias.
- Los reintentos ante fallos de red (429/5xx/timeout) están en la capa HTTP (tenacity).
- El CLI sale con código != 0 si la tarea falla (el agendador lo detecta).

## Consultar el historial
```sql
SELECT name, status, started_at, finished_at, stats, error
FROM task_runs ORDER BY id DESC LIMIT 20;
```
