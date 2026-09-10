import { motion } from "framer-motion";
import type { Zone } from "../types";
import SearchBar from "./SearchBar";
import StatsWidgets from "./StatsWidgets";

interface Props {
  zone: Zone | null;
  stats: { total: number; withJobs: number; totalJobs: number; categories: number };
  query: string;
  onQuery: (v: string) => void;
  filtersOpen: boolean;
  onToggleFilters: () => void;
}

export default function HudTopBar({ zone, stats, query, onQuery, filtersOpen, onToggleFilters }: Props) {
  return (
    <motion.header
      initial={{ y: -70, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 200, damping: 26, delay: 0.15 }}
      className="glass pointer-events-auto absolute inset-x-2 top-3 z-30 flex items-center gap-3 rounded-2xl px-3 py-2 sm:inset-x-4 sm:top-4 sm:gap-4 sm:px-4"
    >
      {/* Identidad del sistema */}
      <div className="flex shrink-0 items-center gap-2.5">
        <div className="relative grid h-9 w-9 place-items-center rounded-lg border border-ice/30 bg-ice/10">
          <span className="absolute h-9 w-9 animate-ping rounded-lg border border-ice/20" />
          <span className="text-ice">◎</span>
        </div>
        <div className="leading-tight">
          <div className="hud-title text-sm font-bold tracking-wide text-bright">RADAR LOCAL</div>
          <div className="hud-label hidden sm:block">Negocios &amp; Vacantes</div>
        </div>
      </div>

      <div className="hidden h-9 w-px bg-white/10 lg:block" />

      {/* Zona */}
      <div className="hidden leading-tight lg:block">
        <div className="hud-label">Zona activa</div>
        <div className="text-sm font-semibold text-bright">
          {zone ? zone.name : "—"}
          <span className="ml-1 text-haze">· {zone?.municipality}</span>
        </div>
      </div>

      {/* Lado derecho */}
      <div className="ml-auto flex items-center gap-3">
        <div className="hidden md:block">
          <StatsWidgets stats={stats} />
        </div>
        <SearchBar value={query} onChange={onQuery} />
        <button
          onClick={onToggleFilters}
          className={`shrink-0 rounded-lg border px-3 py-2 text-sm transition ${
            filtersOpen
              ? "border-ice/40 bg-ice/10 text-bright"
              : "border-white/10 bg-white/[0.03] text-ghost hover:bg-white/[0.08]"
          }`}
        >
          ▤<span className="ml-1 hidden sm:inline">Filtros</span>
        </button>
      </div>
    </motion.header>
  );
}
