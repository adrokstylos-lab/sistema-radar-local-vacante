interface Props {
  value: string;
  onChange: (v: string) => void;
}

export default function SearchBar({ value, onChange }: Props) {
  return (
    <div className="relative">
      <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-haze">⌕</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Buscar establecimiento…"
        className="w-36 rounded-lg border border-white/10 bg-carbon/70 py-2 pl-8 pr-3 text-sm text-bright placeholder:text-haze/70 outline-none transition focus:border-ice/40 focus:shadow-glow sm:w-56"
      />
    </div>
  );
}
