import type { Business, Hours, Job, MarkerState } from "../types";

export function haversineM(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371000;
  const p1 = (lat1 * Math.PI) / 180;
  const p2 = (lat2 * Math.PI) / 180;
  const dp = ((lat2 - lat1) * Math.PI) / 180;
  const dl = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dp / 2) ** 2 + Math.cos(p1) * Math.cos(p2) * Math.sin(dl / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export function markerState(b: Business): MarkerState {
  if (b.status.startsWith("cerrado")) return "closed";
  if (b.jobs.some((j) => j.status === "activa" || j.status === "posible")) return "jobs";
  if (b.status === "desconocido") return "unverified";
  return "open";
}

export const STATE_COLOR: Record<MarkerState, string> = {
  jobs: "#35E0A1",
  open: "#7DE3FF",
  unverified: "#F5C36B",
  closed: "#E5556E",
};

export const STATE_LABEL: Record<MarkerState, string> = {
  jobs: "Con vacantes",
  open: "Activo",
  unverified: "No verificado",
  closed: "Cerrado",
};

export const STATUS_LABEL: Record<string, string> = {
  activo: "Operativo",
  cerrado_temporal: "Cerrado temporalmente",
  cerrado_permanente: "Cerrado permanentemente",
  desconocido: "Sin verificar",
};

const DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

export function dayName(i: number): string {
  return DAYS[i] ?? "?";
}

export function isOpenNow(hours: Hours[]): boolean | null {
  if (!hours.length) return null;
  const now = new Date();
  const wd = (now.getDay() + 6) % 7; // JS: 0=Dom -> nuestro 0=Lun
  const today = hours.filter((h) => h.day_of_week === wd && h.open_time && h.close_time);
  if (!today.length) return false;
  const cur = now.getHours() * 60 + now.getMinutes();
  return today.some((h) => {
    const [oh, om] = (h.open_time as string).split(":").map(Number);
    const [ch, cm] = (h.close_time as string).split(":").map(Number);
    return cur >= oh * 60 + om && cur <= ch * 60 + cm;
  });
}

export function formatDistance(m?: number | null): string {
  if (m == null) return "—";
  return m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(1)} km`;
}

export function formatSalary(j: Job): string {
  if (j.salary_min == null) return "Salario no publicado";
  const per = j.salary_period ? `/${j.salary_period}` : "";
  const cur = j.currency ?? "";
  if (j.salary_max && j.salary_max !== j.salary_min) {
    return `$${j.salary_min.toLocaleString()}–$${j.salary_max.toLocaleString()} ${cur}${per}`;
  }
  return `$${j.salary_min.toLocaleString()} ${cur}${per}`;
}

export function activeJobs(b: Business): Job[] {
  return b.jobs.filter((j) => j.status === "activa" || j.status === "posible");
}
