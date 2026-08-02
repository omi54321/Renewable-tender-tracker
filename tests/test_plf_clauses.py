from Python.extractors.plf_clauses import extract_plf_cuf_availability


def get_field(items, name):
    return next((x for x in items if x.field == name), None)


def test_annual_plf():
    text = "The minimum guaranteed annual PLF shall be 80% during each contract year."
    result = extract_plf_cuf_availability(text)
    item = get_field(result, "Minimum Annual PLF %")
    assert item is not None
    assert item.value == 80
    assert item.confidence >= 0.9


def test_monthly_plf():
    text = "Monthly PLF shall not be less than 75%."
    result = extract_plf_cuf_availability(text)
    item = get_field(result, "Minimum Monthly PLF %")
    assert item is not None
    assert item.value == 75


def test_cuf_range():
    text = "The declared CUF shall remain in the range of 21% to 27%."
    result = extract_plf_cuf_availability(text)
    assert get_field(result, "Declared CUF Lower %").value == 21
    assert get_field(result, "Declared CUF Upper %").value == 27


def test_availability():
    text = "Minimum annual availability shall be 95% and minimum monthly availability shall be 90%."
    result = extract_plf_cuf_availability(text)
    assert get_field(result, "Annual Availability %").value == 95
    assert get_field(result, "Monthly Availability %").value == 90


def test_peak_supply_and_external_cap():
    text = "The SPD shall supply 4 MWh per MW per day. Energy sourced from green market shall be up to 5% annually."
    result = extract_plf_cuf_availability(text)
    assert get_field(result, "Peak Supply MWh/MW/Day").value == 4
    assert get_field(result, "Maximum External Energy %").value == 5


def test_penalty():
    text = "For shortfall beyond the permitted limit, penalty shall be 1.5 times the PPA tariff multiplied by energy shortfall."
    result = extract_plf_cuf_availability(text)
    assert get_field(result, "Under-Supply Penalty") is not None
