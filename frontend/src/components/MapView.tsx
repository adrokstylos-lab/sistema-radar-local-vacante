import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import Supercluster from "supercluster";
import type { Business, Zone } from "../types";
import { createMap, flyToBusiness, resetCamera } from "../lib/map";
import { createClusterElement, createMarkerElement } from "./BusinessMarker";

interface Props {
  zone: Zone;
  businesses: Business[];
  selectedId: number | null;
  onSelect: (b: Business | null) => void;
}

function circlePolygon(lng: number, lat: number, radiusM: number, points = 72) {
  const coords: [number, number][] = [];
  const dLat = radiusM / 111320;
  const dLng = radiusM / (111320 * Math.cos((lat * Math.PI) / 180));
  for (let i = 0; i <= points; i++) {
    const t = (i / points) * 2 * Math.PI;
    coords.push([lng + dLng * Math.cos(t), lat + dLat * Math.sin(t)]);
  }
  return {
    type: "Feature" as const,
    properties: {},
    geometry: { type: "Polygon" as const, coordinates: [coords] },
  };
}

export default function MapView({ zone, businesses, selectedId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const indexRef = useRef<Supercluster | null>(null);
  const byIdRef = useRef<Map<number, Business>>(new Map());
  const selectedIdRef = useRef<number | null>(selectedId);
  const onSelectRef = useRef(onSelect);
  const readyRef = useRef(false);

  onSelectRef.current = onSelect;

  function buildIndex(list: Business[]) {
    const index = new Supercluster({ radius: 60, maxZoom: 16 });
    index.load(
      list
        .filter((b) => b.lat != null && b.lng != null)
        .map((b) => ({
          type: "Feature" as const,
          properties: { businessId: b.id },
          geometry: { type: "Point" as const, coordinates: [b.lng, b.lat] },
        }))
    );
    indexRef.current = index;
    byIdRef.current = new Map(list.map((b) => [b.id, b]));
  }

  function renderMarkers() {
    const map = mapRef.current;
    const index = indexRef.current;
    if (!map || !index) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    const b = map.getBounds();
    const bbox: [number, number, number, number] = [b.getWest(), b.getSouth(), b.getEast(), b.getNorth()];
    const zoom = Math.round(map.getZoom());
    const clusters = index.getClusters(bbox, zoom);

    for (const f of clusters) {
      const [lng, lat] = f.geometry.coordinates as [number, number];
      const props = f.properties as { cluster?: boolean; point_count?: number; cluster_id?: number; businessId?: number };
      let el: HTMLElement;
      if (props.cluster) {
        el = createClusterElement(props.point_count ?? 0, () => {
          const zoomTo = Math.min(index.getClusterExpansionZoom(props.cluster_id!), 18);
          map.easeTo({ center: [lng, lat], zoom: zoomTo, duration: 700, essential: true });
        });
      } else {
        const biz = byIdRef.current.get(props.businessId!);
        if (!biz) continue;
        el = createMarkerElement(biz, (bb) => onSelectRef.current(bb));
        if (biz.id === selectedIdRef.current) el.classList.add("marker--selected");
      }
      markersRef.current.push(new maplibregl.Marker({ element: el }).setLngLat([lng, lat]).addTo(map));
    }
  }

  // Crear mapa una vez
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = createMap(containerRef.current, zone);
    mapRef.current = map;

    map.on("load", () => {
      readyRef.current = true;
      map.addSource("zone", { type: "geojson", data: circlePolygon(zone.lng, zone.lat, zone.radius_m) });
      map.addLayer({ id: "zone-fill", type: "fill", source: "zone", paint: { "fill-color": "#7DE3FF", "fill-opacity": 0.04 } });
      map.addLayer({
        id: "zone-line", type: "line", source: "zone",
        paint: { "line-color": "#7DE3FF", "line-opacity": 0.35, "line-width": 1, "line-dasharray": [3, 3] },
      });
      buildIndex(businesses);
      renderMarkers();
    });

    map.on("moveend", renderMarkers);
    map.on("zoomend", renderMarkers);
    map.on("click", () => onSelectRef.current(null));

    return () => {
      map.remove();
      mapRef.current = null;
      readyRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [zone]);

  // Rebuild al cambiar la lista filtrada
  useEffect(() => {
    if (!readyRef.current) return;
    buildIndex(businesses);
    renderMarkers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [businesses]);

  // Selección: resaltar + cámara
  useEffect(() => {
    selectedIdRef.current = selectedId;
    const map = mapRef.current;
    if (!map) return;
    markersRef.current.forEach((m) => {
      const el = m.getElement();
      if (el.classList.contains("marker")) {
        el.classList.toggle("marker--selected", el.dataset.id === String(selectedId));
      }
    });
    if (selectedId != null) {
      const b = byIdRef.current.get(selectedId);
      if (b) flyToBusiness(map, b);
    } else if (readyRef.current) {
      resetCamera(map, zone);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  return <div ref={containerRef} className="absolute inset-0" />;
}
