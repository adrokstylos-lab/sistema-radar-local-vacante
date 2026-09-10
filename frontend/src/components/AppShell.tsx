import { AnimatePresence } from "framer-motion";
import { useState } from "react";
import type { DashboardState } from "../hooks/useDashboard";
import { STATE_COLOR, STATE_LABEL } from "../lib/format";
import type { MarkerState } from "../types";
import AnimatedOverlay from "./AnimatedOverlay";
import BusinessDetailsPanel from "./BusinessDetailsPanel";
import FiltersPanel from "./FiltersPanel";
import GiftEasterEgg from "./GiftEasterEgg";
import HudTopBar from "./HudTopBar";
import MapView from "./MapView";

const LEGEND: MarkerState[] = ["jobs", "open", "unverified", "closed"];

export default function AppShell({ d }: { d: DashboardState }) {
  // Filtros abiertos por defecto en escritorio, cerrados en móvil.
  const [filtersOpen, setFiltersOpen] = useState(
    typeof window === "undefined" ? true : window.innerWidth >= 768
  );

  return (
    <div className="relative h-full w-full overflow-hidden bg-void">
      {d.zone && (
        <MapView
          zone={d.zone}
          businesses={d.filtered}
          selectedId={d.selectedId}
          onSelect={(b) => d.setSelectedId(b ? b.id : null)}
        />
      )}

      <AnimatedOverlay />

      {/* HUD (por encima de la niebla) */}
      <div className="pointer-events-none absolute inset-0 z-20">
        <GiftEasterEgg />
        <HudTopBar
          zone={d.zone}
          stats={d.stats}
          query={d.filters.query}
          onQuery={(v) => d.setFilters((f) => ({ ...f, query: v }))}
          filtersOpen={filtersOpen}
          onToggleFilters={() => setFiltersOpen((v) => !v)}
        />

        <AnimatePresence>
          {filtersOpen && (
            <FiltersPanel
              filters={d.filters}
              setFilters={d.setFilters}
              categories={d.categories}
              jobTitles={d.jobTitles}
              onReset={d.resetFilters}
            />
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {d.selected && (
            <BusinessDetailsPanel business={d.selected} onClose={() => d.setSelectedId(null)} />
          )}
        </AnimatePresence>

        {/* Leyenda (oculta en móvil para no estorbar) */}
        <div className="glass pointer-events-auto absolute bottom-4 left-1/2 z-30 hidden -translate-x-1/2 items-center gap-4 rounded-full px-4 py-2 sm:flex">
          {LEGEND.map((s) => (
            <span key={s} className="flex items-center gap-1.5 text-[11px] text-ghost">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: STATE_COLOR[s] }} />
              {STATE_LABEL[s]}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
