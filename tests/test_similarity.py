import pytest
from app.patent_similarity import find_similar_patents, classify_risk

def test_classify_risk():
    assert classify_risk(80) == "High"
    assert classify_risk(71) == "High"
    assert classify_risk(70) == "Medium"
    assert classify_risk(40) == "Medium"
    assert classify_risk(39) == "Low"
    assert classify_risk(0) == "Low"

def test_find_similar_patents_no_keyerror():
    # This should not raise KeyError now that we've fixed the 'abstract' vs 'description' key issue.
    # The description is very similar to the first mock patent in mock_patents.json
    description = "A solar-powered device for purifying water using a parabolic collector."
    result = find_similar_patents(description)
    
    assert "similarity_score" in result
    assert "risk_level" in result
    assert "most_similar_patent" in result
    assert "all_scores" in result
    
    assert result["similarity_score"] > 0
    assert isinstance(result["all_scores"], list)
    assert len(result["all_scores"]) > 0

def test_find_similar_patents_high_similarity():
    # Use exact description from mock_patents.json
    description = "A portable water purification device utilizing concentrated solar energy to eliminate microorganisms and chemical contaminants from water sources. The system employs a parabolic solar collector combined with UV sterilization to achieve high levels of pathogen removal suitable for rural deployment."
    result = find_similar_patents(description)
    
    # Similarity should be very high (near 100%)
    assert result["similarity_score"] > 95
    assert result["risk_level"] == "High"
    assert result["most_similar_patent"] == "Solar-Powered Water Purification System"
