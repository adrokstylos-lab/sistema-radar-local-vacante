import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Business, Zone } from "../types";

// Estilo vector oscuro gratuito (sin API key). Soporta pitch/bearing (cámara 3D).
export const DARK_STYLE =
  "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

export function createMap(container: HTMLElement, zone: Zone): maplibregl.Map {
  const map = new maplibregl.Map({
    container,
    style: DARK_STYLE,
    center: [zone.lng, zone.lat],
    zoom: 13.4,
    pitch: 42,
    bearing: -14,
    antialias: true,
    attributionControl: false,
    dragRotate: true,
    touchZoomRotate: true,
    touchPitch: true,
    pitchWithRotate: true,
    cooperativeGestures: false,
  });

  // Gestos: ratón (arrastrar = pan, ctrl/derecho = rotar/inclinar, rueda = zoom)
  // y móvil (arrastrar = pan, dos dedos = pinch-zoom + rotar + inclinar).
  map.dragPan.enable();
  map.scrollZoom.enable();
  map.dragRotate.enable();
  map.keyboard.enable();
  map.doubleClickZoom.enable();
  map.touchZoomRotate.enable();
  map.touchZoomRotate.enableRotation();
  map.touchPitch.enable();

  map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-left");
  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right");
  return map;
}

/**
 * Movimiento cinematográfico al seleccionar: una reorientación fluida en curva
 * que rota la cámara, la inclina y se acerca al local (efecto "dive").
 */
export function flyToBusiness(map: maplibregl.Map, b: Business): void {
  const bearing = (map.getBearing() + 42) % 360;
  map.flyTo({
    center: [b.lng, b.lat],
    zoom: 17,
    pitch: 62,
    bearing,
    duration: 2200,
    curve: 1.7,
    speed: 0.8,
    essential: true,
  });
}

export function resetCamera(map: maplibregl.Map, zone: Zone): void {
  map.flyTo({
    center: [zone.lng, zone.lat],
    zoom: 13.4,
    pitch: 42,
    bearing: -14,
    duration: 1400,
    curve: 1.5,
    essential: true,
  });
}
