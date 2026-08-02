from Python.core.scope import eligibility


def test_rooftop_is_excluded():
    ok, reason = eligibility(
        {"Capacity MW": 500, "Title": "Rooftop Solar Project"},
        {"exclude_rooftop": True, "minimum_capacity_mw": 100}
    )
    assert not ok
    assert "Rooftop" in reason


def test_sub_100_is_excluded():
    ok, reason = eligibility(
        {"Capacity MW": 99, "Title": "Utility Solar"},
        {"minimum_capacity_mw": 100}
    )
    assert not ok
