interface Props {
  count: number;
  className?: string;
}

export default function VacancyBadge({ count, className = "" }: Props) {
  if (count <= 0) {
    return (
      <span className={`hud-label rounded px-2 py-0.5 text-haze/80 ${className}`}>
        Sin vacantes
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full bg-vac/15 px-2.5 py-0.5 text-[11px] font-semibold text-vac ring-1 ring-vac/40 ${className}`}
    >
      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-vac" />
      {count} vacante{count > 1 ? "s" : ""}
    </span>
  );
}
