import { useEffect, useMemo, useState } from "react";
import { loadBusinesses, loadZone } from "../data/api";
import { activeJobs, haversineM, isOpenNow, markerState } from "../lib/format";
import type { Business, Filters, Zone } from "../types";

const EMPTY_FILTERS: Filters = {
  query: "",
  category: null,
  jobTitle: null,
  hasJobs: false,
  openNow: false,
  minRating: 0,
};

export function useDashboard() {
  const [zone, setZone] = useState<Zone | null>(null);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      const [z, bs] = await Promise.all([loadZone(), loadBusinesses()]);
      if (!alive) return;
      const withDist = bs.map((b) => ({
        ...b,
        distance_m: haversineM(z.lat, z.lng, b.lat, b.lng),
      }));
      withDist.sort((a, b) => (a.distance_m ?? 0) - (b.distance_m ?? 0));
      setZone(z);
      setBusinesses(withDist);
      setLoading(false);
    })();
    return () => {
      alive = false;
    };
  }, []);

  const categories = useMemo(() => {
    const set = new Map<string, number>();
    businesses.forEach((b) => {
      const c = b.primary_category ?? "otros";
      set.set(c, (set.get(c) ?? 0) + 1);
    });
    return [...set.entries()].sort((a, b) => b[1] - a[1]);
  }, [businesses]);

  const jobTitles = useMemo(() => {
    const set = new Set<string>();
    businesses.forEach((b) => b.jobs.forEach((j) => j.title_category && set.add(j.title_category)));
    return [...set].sort();
  }, [businesses]);

  const filtered = useMemo(() => {
    const q = filters.query.trim().toLowerCase();
    return businesses.filter((b) => {
      if (q && !b.display_name.toLowerCase().includes(q)) return false;
      if (filters.category && b.primary_category !== filters.category) return false;
      if (filters.hasJobs && activeJobs(b).length === 0) return false;
      if (filters.jobTitle && !b.jobs.some((j) => j.title_category === filters.jobTitle)) return false;
      if (filters.openNow && isOpenNow(b.hours) !== true) return false;
      if (filters.minRating > 0 && (b.rating ?? 0) < filters.minRating) return false;
      return true;
    });
  }, [businesses, filters]);

  const stats = useMemo(() => {
    const withJobs = filtered.filter((b) => activeJobs(b).length > 0);
    const totalJobs = filtered.reduce((n, b) => n + activeJobs(b).length, 0);
    return {
      total: filtered.length,
      withJobs: withJobs.length,
      totalJobs,
      categories: new Set(filtered.map((b) => b.primary_category)).size,
    };
  }, [filtered]);

  const selected = useMemo(
    () => businesses.find((b) => b.id === selectedId) ?? null,
    [businesses, selectedId]
  );

  return {
    zone, businesses, filtered, loading, filters, setFilters,
    categories, jobTitles, stats,
    selected, selectedId, setSelectedId,
    resetFilters: () => setFilters(EMPTY_FILTERS),
    markerState,
  };
}

export type DashboardState = ReturnType<typeof useDashboard>;
