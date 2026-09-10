"""Pruebas de normalización y de la lógica de decisión (sin BD)."""
from backend.app.pipeline.dedup import (
    DIST_EXACT,
    Signals,
    decide,
)
from backend.app.pipeline.normalize import (
    extract_domain,
    normalize_name,
    normalize_phone,
    normalize_social,
)


def test_normalize_phone():
    assert normalize_phone("+52 (55) 1234-5678") == "5512345678"
    assert normalize_phone("55 1234 5678") == "5512345678"
    assert normalize_phone("") is None


def test_extract_domain():
    assert extract_domain("https://www.Ejemplo.mx/empleo") == "ejemplo.mx"
    assert extract_domain("ejemplo.mx") == "ejemplo.mx"
    assert extract_domain(None) is None


def test_normalize_social():
    assert normalize_social("@Cafe_Demo") == "cafe_demo"
    assert normalize_social("https://instagram.com/cafe_demo/") == "cafe_demo"


def _sig(**kw) -> Signals:
    base = dict(name_exact=False, name_sim=0.0, distance_m=9999.0,
                phone_match=False, domain_match=False, social_match=False)
    base.update(kw)
    return Signals(**base)


def test_decide_auto_merge_by_phone():
    assert decide(_sig(phone_match=True))[0] == "auto_merge"


def test_decide_auto_merge_exact_name_close():
    assert decide(_sig(name_exact=True, name_sim=1.0, distance_m=20))[0] == "auto_merge"


def test_decide_manual_review_when_similar_but_no_strong_signal():
    d = decide(_sig(name_sim=0.88, distance_m=120))
    assert d[0] == "manual_review"


def test_decide_rejected_when_far():
    assert decide(_sig(name_exact=True, name_sim=1.0, distance_m=500))[0] == "rejected"
