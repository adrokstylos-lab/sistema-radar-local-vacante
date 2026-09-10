export type BusinessStatus =
  | "activo"
  | "cerrado_temporal"
  | "cerrado_permanente"
  | "desconocido";

export type MarkerState = "jobs" | "open" | "unverified" | "closed";

export interface Job {
  id: number;
  title: string;
  title_category: string | null;
  scope: string;
  status: string;
  salary_min: number | null;
  salary_max: number | null;
  currency: string | null;
  salary_period: string | null;
  source: string | null;
  source_url: string | null;
}

export interface Contact {
  type: string; // telefono | whatsapp | web | email | facebook | instagram | tiktok | linkedin
  value: string;
}

export interface Hours {
  day_of_week: number; // 0=Lu .. 6=Do
  open_time: string | null; // "09:00"
  close_time: string | null;
}

export interface Business {
  id: number;
  display_name: string;
  primary_category: string | null;
  food_type?: string | null;
  rating?: number | null;
  reviews_count?: number | null;
  price_range?: string | null;
  status: BusinessStatus;
  lat: number;
  lng: number;
  distance_m?: number | null;
  municipality?: string | null;
  full_address?: string | null;
  postal_code?: string | null;
  chain_name?: string | null;
  services?: Record<string, boolean> | null;
  contacts: Contact[];
  hours: Hours[];
  jobs: Job[];
  sources: string[];
  updated_at?: string | null;
  is_demo: boolean;
}

export interface Zone {
  name: string;
  municipality: string;
  state: string;
  lat: number;
  lng: number;
  radius_m: number;
}

export interface Filters {
  query: string;
  category: string | null;
  jobTitle: string | null;
  hasJobs: boolean;
  openNow: boolean;
  minRating: number;
}
