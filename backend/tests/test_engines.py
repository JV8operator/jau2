import pytest
from backend.engines.readiness_scorer import compute_readiness_score
from backend.engines.benchmarking_engine import generate_benchmarks

def test_readiness_scorer_high():
    # cgpa: 9, int: 2, proj: 2, sm: 100, pp: 90
    # Expected category: High
    result = compute_readiness_score(9, 2, 2, 100, 90)
    assert result["category"] == "High"
    assert result["readiness_score"] > 80

def test_readiness_scorer_low():
    # cgpa: 5, int: 0, proj: 0, sm: 0, pp: 10
    result = compute_readiness_score(5, 0, 0, 0, 10)
    assert result["category"] == "Low"
    assert result["readiness_score"] < 50

def test_benchmarking_engine():
    # We can mock this but for quick sanity check, we check the structure
    result = generate_benchmarks({"cgpa": 8.0, "internships": 1, "projects": 1, "certificates": 0})
    assert "placed_averages" in result
    assert "gaps" in result
    assert "indicators" in result
