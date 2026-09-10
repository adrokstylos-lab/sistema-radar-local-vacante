import { motion } from "framer-motion";

interface Props {
  stats: { total: number; withJobs: number; totalJobs: number; categories: number };
}

function KPI({ label, value, accent }: { label: string; value: number; accent?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex min-w-[86px] flex-col rounded-lg border border-white/10 bg-white/[0.03] px-3 py-1.5"
    >
      <span className="hud-label">{label}</span>
      <span className="hud-title text-lg font-bold leading-none" style={{ color: accent ?? "#F5F8FF" }}>
        {value}
      </span>
    </motion.div>
  );
}

export default function StatsWidgets({ stats }: Props) {
  return (
    <div className="flex items-center gap-2">
      <KPI label="Negocios" value={stats.total} />
      <KPI label="Con vacantes" value={stats.withJobs} accent="#35E0A1" />
      <KPI label="Vacantes" value={stats.totalJobs} accent="#35E0A1" />
      <KPI label="Categorías" value={stats.categories} accent="#7DE3FF" />
    </div>
  );
}
