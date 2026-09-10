"""Modelos de salida (Pydantic) de la API."""
from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel


class ContactOut(BaseModel):
    type: str
    value: str
    source: str | None = None
    confidence: str | None = None


class HoursOut(BaseModel):
    day_of_week: int
    open_time: time | None = None
    close_time: time | None = None
    source: str | None = None
    confidence: str | None = None


class JobOut(BaseModel):
    id: int
    title: str
    title_category: str | None = None
    description: str | None = None
    scope: str
    status: str
    confidence: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str | None = None
    salary_period: str | None = None
    modality: str | None = None
    address: str | None = None
    source: str | None = None
    source_url: str | None = None
    detected_at: datetime | None = None
    posted_at: datetime | None = None
    business_id: int | None = None
    chain_id: int | None = None
    is_demo: bool


class BusinessListItem(BaseModel):
    id: int
    display_name: str
    primary_category: str | None = None
    food_type: str | None = None
    rating: float | None = None
    reviews_count: int | None = None
    status: str
    municipality: str | None = None
    lat: float | None = None
    lng: float | None = None
    distance_m: float | None = None
    has_jobs: bool = False
    active_jobs_count: int = 0
    open_now: bool | None = None
    last_verified_at: datetime | None = None
    is_demo: bool


class BusinessDetail(BusinessListItem):
    secondary_categories: list | None = None
    description: str | None = None
    services: dict | None = None
    price_range: str | None = None
    confidence: str | None = None
    chain_id: int | None = None
    chain_name: str | None = None
    full_address: str | None = None
    postal_code: str | None = None
    contacts: list[ContactOut] = []
    hours: list[HoursOut] = []
    jobs: list[JobOut] = []
    sources: list[str] = []
    updated_at: datetime | None = None


class ZoneOut(BaseModel):
    id: int
    name: str
    municipality: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    priority: int | None = None
    strategy: str | None = None
    radius_m: int | None = None
    lat: float | None = None
    lng: float | None = None
    is_active: bool
    is_demo: bool


class StatsOut(BaseModel):
    total_businesses: int
    by_category: dict[str, int]
    businesses_with_jobs: int
    total_jobs: int
    jobs_by_category: dict[str, int]
    chains: int
    last_scan_at: datetime | None = None
