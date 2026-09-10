# Despliegue del dashboard (GitHub + Vercel)

El dashboard es una SPA (Vite) en `frontend/`. Se despliega como sitio estático en
Vercel. Usa **datos DEMO** por defecto (`VITE_USE_MOCK` no definido = mock), así
funciona sin backend. `vercel.json` (en la raíz) ya configura el build.

## 1. Crear el repositorio en GitHub

**Opción A — Web (rápida):**
1. Entra a https://github.com/new
2. Nombre sugerido: `radar-local-vacantes` · Visibilidad: **Private** (recomendado por el mensaje personal del easter egg) o Public.
3. **No** marques "Add README" (el repo local ya tiene contenido).
4. Crear. Copia la URL (p. ej. `https://github.com/TU_USUARIO/radar-local-vacantes.git`).

**Opción B — GitHub CLI:**
```bash
# instalar gh (winget install GitHub.cli) y autenticar:
gh auth login
gh repo create radar-local-vacantes --private --source . --remote origin --push
```

## 2. Subir el código (si usaste la Opción A)
```bash
git branch -M main
git remote add origin https://github.com/TU_USUARIO/radar-local-vacantes.git
git push -u origin main
```
> `.env` NO se sube (está en `.gitignore`). El repo no contiene secretos.

## 3. Desplegar en Vercel

**Opción A — Web (recomendada):**
1. Entra a https://vercel.com/new e inicia sesión con GitHub.
2. **Import** el repo `radar-local-vacantes`.
3. Vercel detecta `vercel.json` automáticamente (build de `frontend/`). Si te pide
   *Root Directory*, déjalo en la raíz (el `vercel.json` ya apunta a `frontend/`),
   o ponlo en `frontend` y framework **Vite**.
4. **Deploy**. En ~1 min tendrás la URL pública (`*.vercel.app`).

**Opción B — Vercel CLI:**
```bash
npx vercel login
npx vercel --prod
```

## Notas
- El deploy muestra datos DEMO. Para conectar un backend real habría que hospedar
  el FastAPI (ver `docs/PRODUCCION.md`) y definir `VITE_USE_MOCK=false` +
  la URL de la API en el frontend.
- Cada `git push` a `main` redepliega automáticamente si conectaste el repo en Vercel.
