from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Any, Iterable

@dataclass
class Evidence:
    field: str
    value: Any
    unit: str
    confidence: float
    snippet: str
    page: int | None = None
    pattern: str = ""

PERCENT = r"(\d{1,3}(?:\.\d+)?)\s*%"
NUMBER = r"(\d+(?:\.\d+)?)"

def _normalize(text: str) -> str:
    return " ".join(text.replace("–", "-").replace("—", "-").split())

def _window(text: str, start: int, end: int, radius: int = 220) -> str:
    return text[max(0,start-radius):min(len(text),end+radius)]

def _best(items: Iterable[Evidence]) -> Evidence | None:
    values = list(items)
    return max(values, key=lambda x: (x.confidence, len(x.snippet))) if values else None

def _percentage(text: str, field: str, patterns: list[tuple[str,float]]) -> Evidence | None:
    candidates = []
    for pattern, confidence in patterns:
        for m in re.finditer(pattern, text, re.I | re.S):
            value = float(m.group(1))
            if 0 <= value <= 100:
                candidates.append(Evidence(field, value, "%", confidence, _window(text,m.start(),m.end()), pattern=pattern))
    return _best(candidates)

def extract_plf_cuf_availability(text: str) -> list[Evidence]:
    t = _normalize(text)
    output: list[Evidence] = []

    rules = {
        "Minimum Annual PLF %": [
            (rf"(?:minimum|min\.?|guaranteed)\s+(?:guaranteed\s+)?annual\s+plf(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .99),
            (rf"annual\s+plf.{{0,100}}?(?:shall\s+)?(?:not\s+be\s+less\s+than|not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .97),
            (rf"(?:not\s+less\s+than|at\s+least)\s*{PERCENT}.{{0,70}}?annual\s+plf", .94),
        ],
        "Minimum Monthly PLF %": [
            (rf"(?:minimum|min\.?|guaranteed)\s+(?:guaranteed\s+)?monthly\s+plf(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .99),
            (rf"monthly\s+plf.{{0,100}}?(?:shall\s+)?(?:not\s+be\s+less\s+than|not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .98),
            (rf"(?:not\s+less\s+than|at\s+least)\s*{PERCENT}.{{0,70}}?monthly\s+plf", .94),
        ],
        "Minimum CUF %": [
            (rf"(?:minimum|min\.?|guaranteed)\s+(?:annual\s+)?cuf(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .98),
            (rf"(?:annual\s+)?cuf.{{0,100}}?(?:shall\s+)?(?:not\s+be\s+less\s+than|not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .96),
        ],
        "Annual Availability %": [
            (rf"(?:minimum|min\.?)\s+annual\s+(?:system\s+)?availability(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .99),
            (rf"annual\s+(?:system\s+)?availability.{{0,100}}?(?:not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .96),
        ],
        "Monthly Availability %": [
            (rf"(?:minimum|min\.?)\s+monthly\s+(?:system\s+)?availability(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .99),
            (rf"monthly\s+(?:system\s+)?availability.{{0,100}}?(?:not\s+be\s+less\s+than|not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .97),
        ],
        "Round Trip Efficiency %": [
            (rf"(?:minimum|min\.?)\s+(?:ac[- ]?ac\s+|dc[- ]?dc\s+)?round\s*trip\s+efficiency(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .98),
            (rf"round\s*trip\s+efficiency.{{0,100}}?(?:not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .95),
        ],
        "Allowed Shortfall %": [
            (rf"(?:shortfall|deviation|tolerance).{{0,100}}?(?:up\s+to|not\s+exceeding|maximum|permitted)\s*{PERCENT}", .95),
            (rf"(?:up\s+to|not\s+exceeding|maximum)\s*{PERCENT}.{{0,100}}?(?:shortfall|deviation|tolerance)", .93),
        ],
        "Maximum External Energy %": [
            (rf"(?:external|green\s+market|power\s+exchange|bilateral).{{0,160}}?(?:up\s+to|maximum|not\s+more\s+than)\s*{PERCENT}", .96),
            (rf"(?:up\s+to|maximum|not\s+more\s+than)\s*{PERCENT}.{{0,160}}?(?:external|green\s+market|power\s+exchange|bilateral)", .94),
        ],
    }
    for field, patterns in rules.items():
        item = _percentage(t, field, patterns)
        if item: output.append(item)

    # CUF range
    for pattern in [
        rf"(?:declared\s+)?cuf.{{0,100}}?{PERCENT}\s*(?:to|-)\s*{PERCENT}",
        rf"cuf\s+range.{{0,60}}?{PERCENT}\s*(?:to|-)\s*{PERCENT}",
    ]:
        m = re.search(pattern, t, re.I | re.S)
        if m:
            lo, hi = float(m.group(1)), float(m.group(2))
            if 0 <= lo <= hi <= 100:
                snip = _window(t,m.start(),m.end())
                output += [Evidence("Declared CUF Lower %",lo,"%",.96,snip,pattern=pattern), Evidence("Declared CUF Upper %",hi,"%",.96,snip,pattern=pattern)]
                break

    # Energy obligation
    patterns = [
        (rf"{NUMBER}\s*mwh\s*(?:per|/)\s*mw\s*(?:per|/)\s*day", "MWh/MW/day", .99),
        (rf"{NUMBER}\s*kwh\s*(?:per|/)\s*kw\s*(?:per|/)\s*day", "kWh/kW/day", .96),
    ]
    for pattern, unit, confidence in patterns:
        m = re.search(pattern,t,re.I)
        if m:
            output.append(Evidence("Peak Supply MWh/MW/Day",float(m.group(1)),unit,confidence,_window(t,m.start(),m.end()),pattern=pattern)); break

    # Cycle requirement
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:full\s+)?cycles?\s*(?:per|/)\s*day", t, re.I)
    if m: output.append(Evidence("Cycles Per Day",float(m.group(1)),"cycles/day",.97,_window(t,m.start(),m.end()),pattern="cycles per day"))

    # Penalty text
    penalty_patterns = [
        (r"((?:shortfall|under[- ]supply|failure\s+to\s+supply).{0,700}?(?:penalty|liquidated\s+damages|compensation).{0,700})", .96),
        (r"((?:penalty|liquidated\s+damages).{0,350}?(?:shortfall|under[- ]supply).{0,700})", .93),
        (r"((?:1\.5|one\s+point\s+five)\s*(?:times|x).{0,500}?(?:shortfall|energy|tariff|market))", .95),
    ]
    candidates=[]
    for pattern, confidence in penalty_patterns:
        for m in re.finditer(pattern,t,re.I|re.S):
            candidates.append(Evidence("Under-Supply Penalty",m.group(1)[:1200],"Text",confidence,_window(t,m.start(),m.end(),300),pattern=pattern))
    item=_best(candidates)
    if item: output.append(item)

    # Exchange/charging permission and conditions
    ext_patterns = [
        (r"((?:energy|power).{0,300}?(?:procured|sourced|purchased).{0,180}?(?:power\s+exchange|green\s+market|bilateral).{0,700})", .95),
        (r"((?:charging|charge).{0,350}?(?:exchange|green\s+market|bilateral|external\s+source).{0,700})", .96),
    ]
    candidates=[]
    for pattern, confidence in ext_patterns:
        for m in re.finditer(pattern,t,re.I|re.S):
            candidates.append(Evidence("Charging / External Energy Conditions",m.group(1)[:1200],"Text",confidence,_window(t,m.start(),m.end(),300),pattern=pattern))
    item=_best(candidates)
    if item:
        output.append(Evidence("External / Exchange Energy Allowed","Yes","Boolean",item.confidence,item.snippet,pattern=item.pattern))
        output.append(item)
    elif re.search(r"(?:shall\s+not|not\s+permitted|not\s+allowed).{0,100}(?:exchange|external\s+energy|green\s+market|bilateral)",t,re.I):
        m=re.search(r"(?:shall\s+not|not\s+permitted|not\s+allowed).{0,180}(?:exchange|external\s+energy|green\s+market|bilateral)",t,re.I)
        output.append(Evidence("External / Exchange Energy Allowed","No","Boolean",.94,_window(t,m.start(),m.end()),pattern="negative permission"))

    # Merchant use
    m=re.search(r"((?:merchant|third[- ]party).{0,650})",t,re.I|re.S)
    if m: output.append(Evidence("Third-Party / Merchant Use",m.group(1)[:1000],"Text",.88,_window(t,m.start(),m.end(),260),pattern="merchant/third-party"))
    return output

def extract_page_evidence(pages: list[tuple[int,str]]) -> list[Evidence]:
    evidence=[]
    for page, text in pages:
        for item in extract_plf_cuf_availability(text):
            item.page=page
            evidence.append(item)
    # retain best per field
    best={}
    for item in evidence:
        old=best.get(item.field)
        if old is None or item.confidence > old.confidence: best[item.field]=item
    return list(best.values())

def to_dicts(items: list[Evidence]) -> list[dict[str,Any]]:
    return [asdict(i) for i in items]
