import { motion } from "framer-motion";
import type { ReactNode } from "react";
import type { Business } from "../types";
import {
  activeJobs, dayName, formatDistance, formatSalary, isOpenNow,
  markerState, STATE_COLOR, STATE_LABEL, STATUS_LABEL,
} from "../lib/format";
import VacancyBadge from "./VacancyBadge";

interface Props {
  business: Business;
  onClose: () => void;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="mt-4">
      <div className="hud-label mb-1.5">{title}</div>
      {children}
    </div>
  );
}

export default function BusinessDetailsPanel({ business: b, onClose }: Props) {
  const state = markerState(b);
  const jobs = activeJobs(b);
  const open = isOpenNow(b.hours);

  return (
    <motion.aside
      key={b.id}
      initial={{ y: 24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: 24, opacity: 0 }}
      transition={{ type: "spring", stiffness: 260, damping: 28 }}
      className="glass pointer-events-auto absolute z-30 flex flex-col overflow-hidden rounded-2xl inset-x-2 bottom-2 max-h-[70vh] sm:inset-x-auto sm:right-4 sm:top-24 sm:bottom-6 sm:max-h-none sm:w-[380px]"
    >
      {/* Cabecera */}
      <div className="relative border-b border-white/10 p-5">
        <div className="absolute inset-x-0 top-0 h-[2px]" style={{ background: STATE_COLOR[state] }} />
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="hud-label" style={{ color: STATE_COLOR[state] }}>
              {STATE_LABEL[state]}
            </div>
            <h2 className="hud-title mt-0.5 text-xl font-bold text-bright">{b.display_name}</h2>
            <div className="mt-0.5 text-sm text-ghost">
              {b.primary_category ?? "—"}
              {b.food_type ? ` · ${b.food_type}` : ""}
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-md border border-white/10 px-2 py-1 text-haze transition hover:bg-white/10 hover:text-bright"
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>
        {b.is_demo && (
          <span className="mt-2 inline-block rounded bg-unver/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-unver ring-1 ring-unver/40">
            Dato DEMO
          </span>
        )}
      </div>

      {/* Cuerpo */}
      <div className="flex-1 overflow-y-auto p-5 pt-2">
        {/* Métricas rápidas */}
        <div className="mt-3 grid grid-cols-3 gap-2">
          <Metric label="Distancia" value={formatDistance(b.distance_m)} />
          <Metric label="Rating" value={b.rating ? `★ ${b.rating}` : "—"} />
          <Metric
            label="Ahora"
            value={open == null ? "—" : open ? "Abierto" : "Cerrado"}
            accent={open ? "#35E0A1" : undefined}
          />
        </div>

        <Section title="Vacantes activas">
          <VacancyBadge count={jobs.length} />
          <div className="mt-2 space-y-2">
            {jobs.map((j) => (
              <div key={j.id} className="rounded-lg border border-white/10 bg-white/[0.03] p-2.5">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-bright">{j.title}</span>
                  <span className="hud-label">{j.title_category ?? ""}</span>
                </div>
                <div className="mt-0.5 text-xs text-ghost">
                  {formatSalary(j)} · alcance: {j.scope}
                </div>
              </div>
            ))}
          </div>
        </Section>

        <Section title="Ubicación">
          <p className="text-sm text-ghost">{b.full_address ?? "—"}</p>
          <p className="mt-0.5 text-xs text-haze">
            {b.municipality ?? ""} {b.postal_code ? `· CP ${b.postal_code}` : ""}
          </p>
        </Section>

        <Section title="Horario">
          {b.hours.length ? (
            <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs text-ghost">
              {b.hours.map((h, i) => (
                <div key={i} className="flex justify-between">
                  <span className="text-haze">{dayName(h.day_of_week)}</span>
                  <span>
                    {h.open_time?.slice(0, 5)}–{h.close_time?.slice(0, 5)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-haze">Sin información</p>
          )}
        </Section>

        <Section title="Contacto">
          {b.contacts.length ? (
            <ul className="space-y-1 text-sm">
              {b.contacts.map((c, i) => (
                <li key={i} className="flex justify-between gap-3">
                  <span className="hud-label pt-0.5">{c.type}</span>
                  <span className="truncate text-right text-ghost">{c.value}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-haze">Sin información</p>
          )}
        </Section>

        <Section title="Estado & fuentes">
          <div className="flex items-center justify-between text-xs">
            <span className="text-haze">{STATUS_LABEL[b.status] ?? b.status}</span>
            <span className="text-haze">{b.sources.join(", ") || "—"}</span>
          </div>
          {b.updated_at && (
            <div className="mt-1 text-[11px] text-haze/70">
              Actualizado {new Date(b.updated_at).toLocaleDateString()}
            </div>
          )}
        </Section>
      </div>
    </motion.aside>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/[0.03] px-2 py-2 text-center">
      <div className="hud-label">{label}</div>
      <div className="mt-0.5 text-sm font-semibold" style={{ color: accent ?? "#F5F8FF" }}>
        {value}
      </div>
    </div>
  );
}
