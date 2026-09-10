import { motion } from "framer-motion";
import type { Dispatch, SetStateAction } from "react";
import type { Filters } from "../types";

interface Props {
  filters: Filters;
  setFilters: Dispatch<SetStateAction<Filters>>;
  categories: [string, number][];
  jobTitles: string[];
  onReset: () => void;
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={`flex w-full items-center justify-between rounded-lg border px-3 py-2 text-sm transition ${
        checked
          ? "border-ice/40 bg-ice/10 text-bright"
          : "border-white/10 bg-white/[0.02] text-ghost hover:bg-white/[0.05]"
      }`}
    >
      {label}
      <span className={`h-3 w-3 rounded-full ${checked ? "bg-ice shadow-glow" : "bg-steel"}`} />
    </button>
  );
}

export default function FiltersPanel({ filters, setFilters, categories, jobTitles, onReset }: Props) {
  const set = (patch: Partial<Filters>) => setFilters((f) => ({ ...f, ...patch }));

  return (
    <motion.aside
      initial={{ x: -60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -60, opacity: 0 }}
      transition={{ type: "spring", stiffness: 260, damping: 30 }}
      className="glass pointer-events-auto absolute left-2 top-24 bottom-6 z-30 flex w-[260px] max-w-[82vw] flex-col overflow-hidden rounded-2xl sm:left-4"
    >
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <span className="hud-title font-semibold text-bright">Filtros</span>
        <button onClick={onReset} className="hud-label transition hover:text-ice">
          Reiniciar
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        <div>
          <div className="hud-label mb-2">Categoría</div>
          <div className="flex flex-wrap gap-1.5">
            {categories.map(([c, n]) => {
              const active = filters.category === c;
              return (
                <button
                  key={c}
                  onClick={() => set({ category: active ? null : c })}
                  className={`rounded-full px-2.5 py-1 text-xs transition ${
                    active
                      ? "bg-bright text-ink"
                      : "border border-white/10 bg-white/[0.03] text-ghost hover:bg-white/[0.08]"
                  }`}
                >
                  {c} <span className="opacity-60">{n}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <div className="hud-label mb-2">Puesto (vacante)</div>
          <select
            value={filters.jobTitle ?? ""}
            onChange={(e) => set({ jobTitle: e.target.value || null })}
            className="w-full rounded-lg border border-white/10 bg-carbon/80 px-2.5 py-2 text-sm text-ghost outline-none focus:border-ice/40"
          >
            <option value="">Cualquiera</option>
            {jobTitles.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        <div>
          <div className="hud-label mb-2">
            Rating mínimo: <span className="text-bright">{filters.minRating || "—"}</span>
          </div>
          <input
            type="range" min={0} max={5} step={0.5} value={filters.minRating}
            onChange={(e) => set({ minRating: Number(e.target.value) })}
            className="w-full accent-ice"
          />
        </div>

        <div className="space-y-2">
          <Toggle label="Con vacantes" checked={filters.hasJobs} onChange={(v) => set({ hasJobs: v })} />
          <Toggle label="Abierto ahora" checked={filters.openNow} onChange={(v) => set({ openNow: v })} />
        </div>
      </div>
    </motion.aside>
  );
}
