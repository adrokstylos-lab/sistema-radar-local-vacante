import type { Business, Zone } from "../types";
import { DEMO_BUSINESSES, DEMO_ZONE } from "./mock";

// Fuente de datos. Por defecto DEMO (para deploys sin backend, p. ej. Vercel).
// Para usar el FastAPI real en local, crea frontend/.env.local con:
//   VITE_USE_MOCK=false
export const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? "true") !== "false";

// Incluir también los datos DEMO del backend (para ver variedad de vacantes mientras
// no haya vacantes reales). Pon a false para ver únicamente datos reales.
const INCLUDE_DEMO = true;

export async function loadBusinesses(): Promise<Business[]> {
  if (USE_MOCK) return DEMO_BUSINESSES;
  try {
    const q = INCLUDE_DEMO ? "?include_demo=true&limit=200" : "?limit=200";
    const list = await fetch(`/businesses${q}`).then((r) => {
      if (!r.ok) throw new Error(String(r.status));
      return r.json() as Promise<{ id: number }[]>;
    });
    // El detalle (/businesses/{id}) trae jobs, contactos, horarios y fuentes.
    // Para datasets grandes conviene cargar el detalle de forma perezosa (al
    // seleccionar); aquí, con pocos negocios, se traen por adelantado.
    const details = await Promise.all(
      list.map((b) => fetch(`/businesses/${b.id}`).then((r) => r.json() as Promise<Business>))
    );
    return details.filter((b) => b && b.lat != null);
  } catch (err) {
    console.warn("API no disponible, usando datos DEMO:", err);
    return DEMO_BUSINESSES;
  }
}

export async function loadZone(): Promise<Zone> {
  if (USE_MOCK) return DEMO_ZONE;
  try {
    type ZoneRow = {
      name: string; municipality: string; state: string;
      lat: number | null; lng: number; radius_m: number | null; is_demo?: boolean;
    };
    const zones: ZoneRow[] = await fetch("/zones?include_demo=true").then((r) => r.json());
    const z =
      zones.find((x) => x.lat != null && !x.is_demo) ??
      zones.find((x) => x.lat != null) ??
      zones[0];
    if (!z || z.lat == null) return DEMO_ZONE;
    return {
      name: z.name, municipality: z.municipality, state: z.state,
      lat: z.lat, lng: z.lng, radius_m: z.radius_m ?? 1800,
    };
  } catch {
    return DEMO_ZONE;
  }
}
