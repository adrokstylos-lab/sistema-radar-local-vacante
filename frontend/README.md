# Dashboard HUD — Radar Local de Negocios y Vacantes

Interfaz visual tipo **HUD de videojuego / mapa táctico**: mapa oscuro inmersivo,
paneles glass translúcidos, marcadores estilizados y reacción cinematográfica del
mapa al seleccionar un local.

## Stack
- **Vite + React 18 + TypeScript**
- **Tailwind CSS** (tokens de diseño en `tailwind.config.js`)
- **Framer Motion** (animaciones de paneles/overlays)
- **MapLibre GL JS** (mapa oscuro con cámara 3D `flyTo`)
- Estilo de mapa: **CARTO dark-matter** (vector, gratis, sin API key)

## Cómo correr
Requiere Node.js 20+ y el backend FastAPI para datos reales (opcional; por defecto usa DEMO).

```bash
cd frontend
npm install
npm run dev        # desarrollo con hot reload -> http://localhost:5173
npm run build      # compila a dist/ (lo sirve FastAPI en http://localhost:8000/)
npm run typecheck  # verificación de tipos (opcional)
```

En **dev**, las rutas de la API (`/businesses`, `/stats`, …) se proxyean a
`http://localhost:8000` (ver `vite.config.ts`). En **producción**, `npm run build`
genera `frontend/dist/` y el FastAPI lo sirve (ver `backend/app/main.py`).

## Estructura
```
src/
  main.tsx, App.tsx          # entrada y raíz
  index.css                  # base HUD: glass, neblina, scanlines, marcadores, overrides MapLibre
  types.ts                   # tipos de dominio (Business, Job, Zone, Filters…)
  data/
    mock.ts                  # 14 negocios DEMO (con/sin vacantes, cerrado, no verificado)
    api.ts                   # capa de datos; USE_MOCK conmuta DEMO <-> FastAPI real
  lib/
    map.ts                   # init MapLibre, estilo dark, flyTo/reset cámara
    format.ts                # distancia, estado de marcador, colores, abierto-ahora, salario
  hooks/useDashboard.ts      # estado central: datos, filtros, selección, stats derivadas
  components/
    AppShell.tsx             # layout full-screen (mapa + HUD superpuesto)
    AnimatedOverlay.tsx      # neblina/vignette/scanlines + intro "boot"
    HudTopBar.tsx            # identidad, zona, KPIs, buscador, toggle filtros
    SearchBar.tsx  StatsWidgets.tsx
    FiltersPanel.tsx         # sidebar táctico (categoría, puesto, rating, con vacantes, abierto)
    MapView.tsx              # MapLibre + marcadores + cámara
    BusinessMarker.tsx       # elemento DOM del marcador (color/pulso por estado)
    BusinessDetailsPanel.tsx # ficha glass con todos los datos + vacantes
    VacancyBadge.tsx
```

## Cómo cambiar el estilo
- **Colores**: `tailwind.config.js` → `theme.extend.colors` (void, carbon, ice, vac, unver, closed…).
  Los colores de estado de marcador también en `src/lib/format.ts` (`STATE_COLOR`).
- **Tipografía**: `index.html` (Google Fonts) + `tailwind.config.js` (`fontFamily.hud/body`).
- **Glass / neblina / scanlines / marcadores**: `src/index.css` (clases `.glass`, `.fx-fog`, `.fx-scan`, `.marker`).
- **Mapa**: `src/lib/map.ts` → `DARK_STYLE` (cambiar por otro estilo MapLibre) y parámetros de
  cámara (`pitch`, `bearing`, `zoom`, `duration`).

## Cómo conectar el backend real
1. En `src/data/api.ts` cambia `USE_MOCK = false`.
2. Corre el FastAPI (`uvicorn backend.app.main:app --reload`) en :8000.
3. En dev, el proxy de Vite enruta las llamadas; en prod, mismo origen.
   Los endpoints ya existen: `/businesses?include_demo=…`, `/businesses/{id}`, `/zones`, `/stats`.
   Puede requerir mapear campos (p. ej. socials) según crezca el modelo.

> Todos los datos incluidos son **DEMO (ficticios)**, claramente marcados, solo para probar la UI.
