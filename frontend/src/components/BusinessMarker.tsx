import type { Business } from "../types";
import { markerState, STATE_COLOR } from "../lib/format";

/**
 * Crea el elemento DOM de un marcador de negocio (para maplibregl.Marker).
 * Se estiliza con CSS (ver index.css: .marker). Los marcadores con vacantes
 * tienen anillo pulsante.
 */
export function createMarkerElement(
  b: Business,
  onClick: (b: Business) => void
): HTMLElement {
  const state = markerState(b);
  const el = document.createElement("div");
  el.className = `marker marker--${state}`;
  el.style.setProperty("--mk", STATE_COLOR[state]);
  el.dataset.id = String(b.id);
  el.innerHTML = `<div class="marker__ring"></div><div class="marker__dot"></div>`;
  el.title = b.display_name;
  el.addEventListener("click", (e) => {
    e.stopPropagation();
    onClick(b);
  });
  return el;
}

/** Crea el elemento DOM de un clúster (grupo de negocios). */
export function createClusterElement(
  count: number,
  onClick: () => void
): HTMLElement {
  const size = count < 10 ? 34 : count < 50 ? 42 : 52;
  const el = document.createElement("div");
  el.className = "cluster";
  el.style.width = `${size}px`;
  el.style.height = `${size}px`;
  el.innerHTML = `<span>${count}</span>`;
  el.addEventListener("click", (e) => {
    e.stopPropagation();
    onClick();
  });
  return el;
}
