"""Datos DEMO (ficticios) claramente identificados.

- Todo lo insertado lleva is_demo=True y/o source="DEMO".
- Idempotente: borra los DEMO existentes y reinserta, SIN tocar datos reales.

Reutilizado por scripts/seed_demo.py y por las pruebas (conftest).
"""
from __future__ import annotations

from datetime import datetime, time, timezone

from geoalchemy2.elements import WKTElement
from sqlalchemy import delete
from sqlalchemy.orm import Session

from backend.app.db.constants import SOURCE_DEMO
from backend.app.db.models import (
    Business,
    BusinessContact,
    BusinessHours,
    BusinessLocation,
    BusinessSource,
    Chain,
    GeographicZone,
    Job,
    JobSource,
)
from backend.app.db.session import SessionLocal


def point(lat: float, lng: float) -> WKTElement:
    """PostGIS espera POINT(lng lat)."""
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


def clear_demo(session: Session) -> None:
    session.execute(delete(Job).where(Job.is_demo.is_(True)))
    session.execute(delete(Business).where(Business.is_demo.is_(True)))
    session.execute(delete(Chain).where(Chain.is_demo.is_(True)))
    session.execute(delete(GeographicZone).where(GeographicZone.is_demo.is_(True)))
    session.flush()


def seed(session: Session) -> dict:
    now = datetime.now(timezone.utc)

    zone = GeographicZone(
        name="Cofradía de San Miguel (DEMO)", municipality="Cuautitlán Izcalli",
        state="Estado de México", country="México", postal_code="54715",
        priority=1, strategy="radius", center=point(19.683, -99.215),
        radius_m=1800, is_active=True, is_demo=True,
    )
    session.add(zone)

    chain = Chain(name="Tacos El Demo", normalized_name="tacos el demo",
                  careers_url="https://ejemplo-demo.mx/empleo", is_demo=True)
    session.add(chain)
    session.flush()

    b1 = Business(
        normalized_name="restaurante el buen sabor demo",
        display_name="Restaurante El Buen Sabor (DEMO)", primary_category="restaurante",
        secondary_categories=["comida_mexicana", "familiar"],
        description="Negocio ficticio para pruebas.", food_type="Comida mexicana",
        services={"dine_in": True, "takeout": True, "delivery": False},
        price_range="$$", rating=4.3, reviews_count=128, status="activo",
        confidence="probable", last_verified_at=now, verification_source=SOURCE_DEMO, is_demo=True,
    )
    b1.locations.append(BusinessLocation(
        full_address="Av. Ficticia 123, Cofradía de San Miguel", colonia="Cofradía de San Miguel",
        municipality="Cuautitlán Izcalli", state="Estado de México", postal_code="54715",
        country="México", geog=point(19.6835, -99.2145), provider=SOURCE_DEMO,
        provider_place_id="demo-place-0001"))
    b1.hours.extend([BusinessHours(day_of_week=d, open_time=time(9, 0), close_time=time(22, 0),
                                   source=SOURCE_DEMO, confidence="probable") for d in range(0, 6)])
    b1.contacts.extend([
        BusinessContact(type="telefono", value="+52 55 0000 0001", source=SOURCE_DEMO, confidence="probable"),
        BusinessContact(type="web", value="https://ejemplo-demo.mx", source=SOURCE_DEMO, confidence="inferido"),
    ])
    b1.sources.append(BusinessSource(provider=SOURCE_DEMO, provider_place_id="demo-place-0001",
                                     raw={"nota": "dato ficticio"}, fetched_at=now))

    b2 = Business(
        normalized_name="cafe demo central", display_name="Café Demo Central (DEMO)",
        primary_category="cafeteria", secondary_categories=["cafe", "postres"], food_type="Cafetería",
        services={"dine_in": True, "takeout": True, "delivery": True, "uber_eats": True},
        price_range="$", rating=4.6, reviews_count=54, status="activo", confidence="probable",
        last_verified_at=now, verification_source=SOURCE_DEMO, is_demo=True,
    )
    b2.locations.append(BusinessLocation(
        full_address="Calle Demo 456, Cofradía de San Miguel", colonia="Cofradía de San Miguel",
        municipality="Cuautitlán Izcalli", state="Estado de México", postal_code="54715",
        country="México", geog=point(19.6820, -99.2160), provider=SOURCE_DEMO,
        provider_place_id="demo-place-0002"))
    b2.contacts.append(BusinessContact(type="instagram", value="@cafe_demo_central",
                                       source=SOURCE_DEMO, confidence="inferido"))

    b3 = Business(
        normalized_name="tacos el demo cofradias", display_name="Tacos El Demo - Cofradías (DEMO)",
        primary_category="taqueria", chain_id=chain.id, food_type="Tacos",
        services={"dine_in": True, "takeout": True}, price_range="$", rating=4.1, reviews_count=210,
        status="activo", confidence="confirmado", last_verified_at=now,
        verification_source=SOURCE_DEMO, is_demo=True,
    )
    b3.locations.append(BusinessLocation(
        full_address="Blvd. Demo 789, Cofradía de San Miguel", colonia="Cofradía de San Miguel",
        municipality="Cuautitlán Izcalli", state="Estado de México", postal_code="54715",
        country="México", geog=point(19.6845, -99.2130), provider=SOURCE_DEMO,
        provider_place_id="demo-place-0003"))
    session.add_all([b1, b2, b3])
    session.flush()

    j1 = Job(
        business_id=b1.id, title="Mesero/a", title_category="mesero",
        description="Vacante ficticia de demostración.", salary_min=7000, salary_max=9000,
        currency="MXN", salary_period="mes", schedule="Lunes a sábado, turno mixto", shift="mixto",
        requirements={"edad_minima": 18}, experience="No indispensable", modality="presencial",
        posted_at=now, detected_at=now, last_verified_at=now, source=SOURCE_DEMO,
        source_url="https://ejemplo-demo.mx/empleo/mesero", status="activa", scope="sucursal",
        confidence="probable", is_demo=True,
    )
    j1.sources.append(JobSource(provider=SOURCE_DEMO, raw={"nota": "ficticio"}, fetched_at=now))
    j2 = Job(
        business_id=b3.id, chain_id=chain.id, title="Cocinero/a", title_category="cocinero",
        description="Vacante ficticia de demostración.", salary_min=9000, salary_max=12000,
        currency="MXN", salary_period="mes", schedule="Rol de turnos", modality="presencial",
        posted_at=now, detected_at=now, last_verified_at=now, source=SOURCE_DEMO,
        source_url="https://ejemplo-demo.mx/empleo/cocinero", status="activa", scope="sucursal",
        confidence="confirmado", is_demo=True,
    )
    session.add_all([j1, j2])
    session.flush()
    return {"zonas": 1, "cadenas": 1, "negocios": 3, "vacantes": 2}


def run() -> dict:
    session = SessionLocal()
    try:
        clear_demo(session)
        counts = seed(session)
        session.commit()
        return counts
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
