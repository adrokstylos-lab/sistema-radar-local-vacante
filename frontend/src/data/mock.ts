import type { Business, Zone } from "../types";

// Centro real de Cofradía de San Miguel, Cuautitlán Izcalli (confirmado con geocoder).
export const DEMO_ZONE: Zone = {
  name: "Cofradía de San Miguel",
  municipality: "Cuautitlán Izcalli",
  state: "Estado de México",
  lat: 19.6895,
  lng: -99.2263,
  radius_m: 1800,
};

const week = (open: string, close: string) =>
  Array.from({ length: 6 }, (_, d) => ({ day_of_week: d, open_time: open, close_time: close }));

let _id = 1;
const nid = () => _id++;

/** Todos los datos aquí son FICTICIOS (DEMO) para probar la interfaz. */
export const DEMO_BUSINESSES: Business[] = [
  {
    id: nid(), display_name: "Restaurante El Buen Sabor", primary_category: "restaurante",
    food_type: "Comida mexicana", rating: 4.3, reviews_count: 128, price_range: "$$",
    status: "activo", lat: 19.6902, lng: -99.2251, municipality: "Cuautitlán Izcalli",
    full_address: "Av. Cofradía 123, Cofradía de San Miguel", postal_code: "54715",
    services: { dine_in: true, takeout: true, delivery: false },
    contacts: [
      { type: "telefono", value: "+52 55 1234 0001" },
      { type: "web", value: "https://elbuensabor-demo.mx" },
      { type: "instagram", value: "@buensabor_demo" },
    ],
    hours: week("09:00", "22:00"),
    jobs: [
      { id: nid(), title: "Mesero/a", title_category: "mesero", scope: "sucursal", status: "activa",
        salary_min: 7000, salary_max: 9000, currency: "MXN", salary_period: "mes", source: "DEMO", source_url: "#" },
    ],
    sources: ["DEMO"], updated_at: "2026-09-08T10:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Café Aurora", primary_category: "cafeteria",
    food_type: "Cafetería de especialidad", rating: 4.6, reviews_count: 54, price_range: "$",
    status: "activo", lat: 19.6871, lng: -99.2288, municipality: "Cuautitlán Izcalli",
    full_address: "Calle Arcángel 45, Cofradía de San Miguel",
    services: { dine_in: true, takeout: true, delivery: true, wifi: true },
    contacts: [{ type: "instagram", value: "@cafe_aurora" }, { type: "telefono", value: "+52 55 1234 0002" }],
    hours: week("07:00", "21:00"),
    jobs: [
      { id: nid(), title: "Barista", title_category: "barista", scope: "sucursal", status: "activa",
        salary_min: 180, salary_max: null, currency: "MXN", salary_period: "dia", source: "DEMO", source_url: "#" },
    ],
    sources: ["DEMO"], updated_at: "2026-09-07T14:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Taquería La Bendición", primary_category: "taqueria",
    food_type: "Tacos y guisados", rating: 4.4, reviews_count: 302, price_range: "$",
    status: "activo", lat: 19.6918, lng: -99.2279, municipality: "Cuautitlán Izcalli",
    full_address: "Av. Huehuetoca 200", services: { dine_in: true, takeout: true },
    contacts: [{ type: "telefono", value: "+52 55 1234 0003" }],
    hours: week("10:00", "23:00"), jobs: [],
    sources: ["DEMO"], updated_at: "2026-09-06T18:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Bar Neón Norte", primary_category: "bar",
    food_type: "Bar / cocteles", rating: 4.1, reviews_count: 89, price_range: "$$",
    status: "activo", lat: 19.6864, lng: -99.2242, municipality: "Cuautitlán Izcalli",
    full_address: "Blvd. Nocturno 8", services: { dine_in: true, reservations: true },
    contacts: [{ type: "instagram", value: "@neon_norte" }, { type: "web", value: "https://neonnorte-demo.mx" }],
    hours: week("17:00", "23:59"),
    jobs: [
      { id: nid(), title: "Bartender", title_category: "bartender", scope: "sucursal", status: "activa",
        salary_min: 9000, salary_max: 13000, currency: "MXN", salary_period: "mes", source: "DEMO", source_url: "#" },
    ],
    sources: ["DEMO"], updated_at: "2026-09-08T22:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Little Caesars", primary_category: "comida_rapida",
    food_type: "Pizza", rating: 4.0, reviews_count: 410, price_range: "$", chain_name: "Little Caesars",
    status: "activo", lat: 19.6949, lng: -99.2231, municipality: "Cuautitlán Izcalli",
    full_address: "Plaza Cofradía L-4", services: { takeout: true, delivery: true },
    contacts: [{ type: "web", value: "https://littlecaesars.com.mx" }],
    hours: week("11:00", "22:00"), jobs: [],
    sources: ["DEMO"], updated_at: "2026-09-05T12:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Burger King", primary_category: "comida_rapida",
    food_type: "Hamburguesas", rating: 3.9, reviews_count: 655, price_range: "$", chain_name: "Burger King",
    status: "activo", lat: 19.6957, lng: -99.2205, municipality: "Cuautitlán Izcalli",
    full_address: "Av. Huehuetoca s/n", services: { dine_in: true, takeout: true, delivery: true, drive_through: true },
    contacts: [{ type: "web", value: "https://burgerking.com.mx" }, { type: "telefono", value: "+52 55 2611 0301" }],
    hours: [
      ...Array.from({ length: 4 }, (_, d) => ({ day_of_week: d, open_time: "10:00", close_time: "21:00" })),
      { day_of_week: 4, open_time: "10:00", close_time: "22:00" },
      { day_of_week: 5, open_time: "10:00", close_time: "22:00" },
      { day_of_week: 6, open_time: "10:00", close_time: "21:00" },
    ],
    jobs: [
      { id: nid(), title: "Cajero/a", title_category: "cajero", scope: "sucursal", status: "activa",
        salary_min: 6500, salary_max: 8000, currency: "MXN", salary_period: "mes", source: "DEMO", source_url: "#" },
    ],
    sources: ["DEMO"], updated_at: "2026-09-08T09:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Toks", primary_category: "restaurante",
    food_type: "Cocina mexicana", rating: 4.2, reviews_count: 512, price_range: "$$", chain_name: "Toks",
    status: "activo", lat: 19.6931, lng: -99.2189, municipality: "Cuautitlán Izcalli",
    full_address: "Valle Dorado, Av. Principal", services: { dine_in: true, reservations: true },
    contacts: [{ type: "web", value: "https://toks.com.mx" }],
    hours: week("07:00", "23:00"), jobs: [],
    sources: ["DEMO"], updated_at: "2026-09-04T11:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Panadería Maná", primary_category: "panaderia",
    food_type: "Panadería", rating: null, reviews_count: null, price_range: "$",
    status: "desconocido", lat: 19.6883, lng: -99.2312, municipality: "Cuautitlán Izcalli",
    full_address: "Paseo de la Caridad 1", contacts: [{ type: "telefono", value: "+52 55 4685 4279" }],
    hours: [], jobs: [], sources: ["DEMO"], updated_at: "2026-08-20T00:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Pastelería La Esperanza", primary_category: "pasteleria",
    food_type: "Pastelería", rating: null, status: "desconocido",
    lat: 19.6866, lng: -99.2274, municipality: "Cuautitlán Izcalli",
    full_address: "Cofradía de San Miguel s/n", contacts: [], hours: [], jobs: [],
    sources: ["DEMO"], updated_at: "2026-08-18T00:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Cantina El Farolito", primary_category: "cantina",
    food_type: "Cantina tradicional", rating: 4.0, reviews_count: 76, price_range: "$$",
    status: "cerrado_temporal", lat: 19.6908, lng: -99.2321, municipality: "Cuautitlán Izcalli",
    full_address: "Callejón del Farol 3", contacts: [{ type: "telefono", value: "+52 55 1234 0010" }],
    hours: week("13:00", "23:00"), jobs: [],
    sources: ["DEMO"], updated_at: "2026-07-30T00:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Sushi Katana", primary_category: "restaurante",
    food_type: "Sushi / japonesa", rating: 4.5, reviews_count: 143, price_range: "$$$",
    status: "activo", lat: 19.6939, lng: -99.2258, municipality: "Cuautitlán Izcalli",
    full_address: "Av. Cofradía 400", services: { dine_in: true, delivery: true, reservations: true },
    contacts: [{ type: "web", value: "https://sushikatana-demo.mx" }, { type: "instagram", value: "@sushi_katana" }],
    hours: week("13:00", "22:30"),
    jobs: [
      { id: nid(), title: "Cocinero/a", title_category: "cocinero", scope: "sucursal", status: "activa",
        salary_min: 10000, salary_max: 14000, currency: "MXN", salary_period: "mes", source: "DEMO", source_url: "#" },
      { id: nid(), title: "Lavaloza", title_category: "lavaloza", scope: "sucursal", status: "activa",
        salary_min: 6000, salary_max: null, currency: "MXN", salary_period: "mes", source: "DEMO", source_url: "#" },
    ],
    sources: ["DEMO"], updated_at: "2026-09-08T16:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Cervecería Grafito", primary_category: "bar",
    food_type: "Cervecería artesanal", rating: 4.3, reviews_count: 198, price_range: "$$",
    status: "activo", lat: 19.6852, lng: -99.2295, municipality: "Cuautitlán Izcalli",
    full_address: "Av. Metal 22", services: { dine_in: true, outdoor_seating: true },
    contacts: [{ type: "instagram", value: "@grafito_beer" }, { type: "telefono", value: "+52 55 1234 0012" }],
    hours: week("15:00", "23:59"),
    jobs: [
      { id: nid(), title: "Mesero/a", title_category: "mesero", scope: "sucursal", status: "activa",
        salary_min: 6500, salary_max: 8500, currency: "MXN", salary_period: "mes", source: "DEMO", source_url: "#" },
      { id: nid(), title: "Garrotero", title_category: "garrotero", scope: "sucursal", status: "activa",
        salary_min: 5500, salary_max: null, currency: "MXN", salary_period: "mes", source: "DEMO", source_url: "#" },
    ],
    sources: ["DEMO"], updated_at: "2026-09-07T20:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Pizzería Vulcano", primary_category: "pizzeria",
    food_type: "Pizza al horno", rating: 4.0, reviews_count: 65, price_range: "$$",
    status: "activo", lat: 19.6875, lng: -99.2226, municipality: "Cuautitlán Izcalli",
    full_address: "Calle Volcán 9", services: { takeout: true, delivery: true },
    contacts: [{ type: "telefono", value: "+52 55 1234 0013" }],
    hours: week("12:00", "22:00"), jobs: [],
    sources: ["DEMO"], updated_at: "2026-09-03T00:00:00Z", is_demo: true,
  },
  {
    id: nid(), display_name: "Fonda Doña Rosa", primary_category: "fonda",
    food_type: "Comida corrida", rating: null, status: "desconocido",
    lat: 19.6924, lng: -99.2305, municipality: "Cuautitlán Izcalli",
    full_address: "Mercado local, local 12", contacts: [], hours: week("08:00", "18:00"), jobs: [],
    sources: ["DEMO"], updated_at: "2026-08-25T00:00:00Z", is_demo: true,
  },
];
