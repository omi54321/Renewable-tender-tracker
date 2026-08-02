from Python.extractors.plf_clauses import extract_plf_cuf_availability, extract_page_evidence

def field(items,name): return next((x for x in items if x.field==name),None)

def test_annual_plf(): assert field(extract_plf_cuf_availability("Minimum guaranteed annual PLF shall be 80%."),"Minimum Annual PLF %").value==80

def test_monthly_plf(): assert field(extract_plf_cuf_availability("Monthly PLF shall not be less than 75%."),"Minimum Monthly PLF %").value==75

def test_minimum_cuf(): assert field(extract_plf_cuf_availability("Minimum annual CUF shall be 24%."),"Minimum CUF %").value==24

def test_cuf_range():
    r=extract_plf_cuf_availability("Declared CUF shall remain in the range of 21% to 27%.")
    assert field(r,"Declared CUF Lower %").value==21 and field(r,"Declared CUF Upper %").value==27

def test_availability():
    r=extract_plf_cuf_availability("Minimum annual availability shall be 95% and minimum monthly availability shall be 90%.")
    assert field(r,"Annual Availability %").value==95 and field(r,"Monthly Availability %").value==90

def test_round_trip_efficiency(): assert field(extract_plf_cuf_availability("Minimum AC-AC round trip efficiency shall be 85%."),"Round Trip Efficiency %").value==85

def test_peak_supply(): assert field(extract_plf_cuf_availability("The developer shall supply 4 MWh per MW per day."),"Peak Supply MWh/MW/Day").value==4

def test_cycles(): assert field(extract_plf_cuf_availability("The system shall complete 2 full cycles per day."),"Cycles Per Day").value==2

def test_shortfall(): assert field(extract_plf_cuf_availability("Permitted shortfall shall be up to 10%."),"Allowed Shortfall %").value==10

def test_external_cap(): assert field(extract_plf_cuf_availability("Energy sourced from green market may be up to 5% annually."),"Maximum External Energy %").value==5

def test_penalty(): assert field(extract_plf_cuf_availability("For shortfall, penalty shall be 1.5 times the PPA tariff multiplied by energy shortfall."),"Under-Supply Penalty") is not None

def test_exchange_allowed(): assert field(extract_plf_cuf_availability("Energy may be sourced from power exchange for charging the ESS."),"External / Exchange Energy Allowed").value=="Yes"

def test_page_evidence(): assert field(extract_page_evidence([(3,"Monthly PLF shall not be less than 75%.")]),"Minimum Monthly PLF %").page==3
