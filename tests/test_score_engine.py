import pytest
from app.score_engine import calculate_ipr_score, get_patent_risk_flags

def test_calculate_ipr_score_empty():
    score, breakdown, tier = calculate_ipr_score([])
    assert score == 0.0
    assert breakdown == []
    assert tier == "Emerging"

def test_calculate_ipr_score_single_patent():
    disclosures = [{"ip_type": "Patent"}]
    score, breakdown, tier = calculate_ipr_score(disclosures)
    assert score == 3.0
    assert len(breakdown) == 1
    assert breakdown[0]["ip_type"] == "Patent"
    assert breakdown[0]["count"] == 1
    assert breakdown[0]["credence"] == 3.0
    assert breakdown[0]["subtotal"] == 3.0
    assert tier == "Emerging"

def test_calculate_ipr_score_mixed():
    disclosures = [
        {"ip_type": "Patent"},
        {"ip_type": "Patent"},
        {"ip_type": "Copyright"},
        {"ip_type": "Trademark"},
    ]
    # Patent: 2 * 3.0 = 6.0
    # Copyright: 1 * 1.0 = 1.0
    # Trademark: 1 * 1.5 = 1.5
    # Total = 8.5
    score, breakdown, tier = calculate_ipr_score(disclosures)
    assert score == 8.5
    assert len(breakdown) == 3
    assert tier == "Developing"

def test_calculate_ipr_score_strong_tier():
    disclosures = [{"ip_type": "Patent"}] * 6  # 6 * 3.0 = 18.0
    score, breakdown, tier = calculate_ipr_score(disclosures)
    assert score == 18.0
    assert tier == "Strong"

def test_get_patent_risk_flags():
    disclosures = [
        {"title": "P1", "ip_type": "Patent", "risk_level": "High", "similarity_score": 85.0, "most_similar_patent": "M1"},
        {"title": "P2", "ip_type": "Patent", "risk_level": "Medium", "similarity_score": 50.0, "most_similar_patent": "M2"},
        {"title": "P3", "ip_type": "Patent", "risk_level": "Low", "similarity_score": 20.0, "most_similar_patent": "M3"},
        {"title": "C1", "ip_type": "Copyright", "risk_level": "High"}, # Not a patent
    ]
    flags = get_patent_risk_flags(disclosures)
    assert len(flags) == 2
    assert flags[0]["title"] == "P1"
    assert flags[1]["title"] == "P2"
    for f in flags:
        assert f["risk_level"] in ("Medium", "High")
