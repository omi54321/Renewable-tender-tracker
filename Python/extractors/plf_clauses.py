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


def _window(text: str, start: int, end: int, radius: int = 220) -> str:
    return " ".join(text[max(0,start-radius):min(len(text),end+radius)].split())


def _best(matches: Iterable[Evidence]) -> Evidence | None:
    ranked = list(matches)
    if not ranked:
        return None
    return sorted(ranked, key=lambda x: (x.confidence, len(x.snippet)), reverse=True)[0]


def extract_percentage_field(
    text: str,
    field: str,
    patterns: list[tuple[str,float]],
) -> Evidence | None:
    candidates: list[Evidence] = []
    for pattern, confidence in patterns:
        for match in re.finditer(pattern, text, re.I | re.S):
            value = float(match.group(1))
            if 0 <= value <= 100:
                candidates.append(Evidence(
                    field=field,
                    value=value,
                    unit="%",
                    confidence=confidence,
                    snippet=_window(text, match.start(), match.end()),
                    pattern=pattern,
                ))
    return _best(candidates)


def extract_plf_cuf_availability(text: str) -> list[Evidence]:
    normalized = " ".join(text.split())
    output: list[Evidence] = []

    libraries = {
        "Minimum Annual PLF %": [
            (rf"(?:minimum|min\.?)\s+(?:guaranteed\s+)?annual\s+plf(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .98),
            (rf"annual\s+plf.{0,80}?(?:not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .94),
            (rf"(?:not\s+less\s+than|at\s+least)\s*{PERCENT}.{{0,50}}annual\s+plf", .92),
        ],
        "Minimum Monthly PLF %": [
            (rf"(?:minimum|min\.?)\s+(?:guaranteed\s+)?monthly\s+plf(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .98),
            (rf"monthly\s+plf.{0,80}?(?:not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .94),
        ],
        "Minimum CUF %": [
            (rf"(?:minimum|min\.?)\s+(?:annual\s+)?cuf(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .97),
            (rf"cuf.{0,80}?(?:not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .92),
        ],
        "Annual Availability %": [
            (rf"(?:minimum|min\.?)\s+annual\s+availability(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .98),
            (rf"annual\s+availability.{0,80}?(?:not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .94),
        ],
        "Monthly Availability %": [
            (rf"(?:minimum|min\.?)\s+monthly\s+availability(?:\s+shall\s+be|\s+of|\s*:)?\s*{PERCENT}", .98),
            (rf"monthly\s+availability.{0,80}?(?:not\s+less\s+than|minimum|at\s+least)\s*{PERCENT}", .94),
        ],
        "Allowed Shortfall %": [
            (rf"(?:shortfall|deviation|tolerance).{{0,80}}?(?:up\s+to|not\s+exceeding|maximum)\s*{PERCENT}", .92),
            (rf"(?:up\s+to|not\s+exceeding)\s*{PERCENT}.{{0,80}}?(?:shortfall|deviation|tolerance)", .90),
        ],
        "Maximum External Energy %": [
            (rf"(?:external|green\s+market|bilateral).{{0,120}}?(?:up\s+to|maximum|not\s+more\s+than)\s*{PERCENT}", .94),
            (rf"(?:up\s+to|maximum|not\s+more\s+than)\s*{PERCENT}.{{0,120}}?(?:external|green\s+market|bilateral)", .92),
        ],
    }

    for field, patterns in libraries.items():
        found = extract_percentage_field(normalized, field, patterns)
        if found:
            output.append(found)

    # Declared CUF range
    range_match = re.search(
        rf"(?:declared\s+)?cuf.{{0,80}}?{PERCENT}\s*(?:to|-)\s*{PERCENT}",
        normalized, re.I | re.S
    )
    if range_match:
        lower, upper = float(range_match.group(1)), float(range_match.group(2))
        if 0 <= lower <= upper <= 100:
            snippet = _window(normalized, range_match.start(), range_match.end())
            output.extend([
                Evidence("Declared CUF Lower %", lower, "%", .95, snippet, pattern="CUF range"),
                Evidence("Declared CUF Upper %", upper, "%", .95, snippet, pattern="CUF range"),
            ])

    # Peak energy obligation
    energy_match = re.search(
        rf"{NUMBER}\s*mwh\s*(?:per|/)\s*mw\s*(?:per|/)\s*day",
        normalized, re.I
    )
    if energy_match:
        output.append(Evidence(
            "Peak Supply MWh/MW/Day",
            float(energy_match.group(1)),
            "MWh/MW/day",
            .98,
            _window(normalized, energy_match.start(), energy_match.end()),
            pattern="MWh per MW per day",
        ))

    # Under-supply penalty formula/text
    penalty_patterns = [
        (r"((?:shortfall|under[- ]supply|failure\s+to\s+supply).{0,500}?(?:penalty|damages|compensation).{0,500})", .94),
        (r"((?:penalty|liquidated\s+damages).{0,250}?(?:shortfall|under[- ]supply).{0,500})", .90),
        (r"((?:1\.5|one\s+point\s+five)\s*(?:times|x).{0,350}?(?:shortfall|energy|tariff|market))", .92),
    ]
    penalty_candidates = []
    for pattern, confidence in penalty_patterns:
        for match in re.finditer(pattern, normalized, re.I | re.S):
            penalty_candidates.append(Evidence(
                "Under-Supply Penalty",
                " ".join(match.group(1).split())[:1000],
                "Text",
                confidence,
                _window(normalized, match.start(), match.end(), 280),
                pattern=pattern,
            ))
    best_penalty = _best(penalty_candidates)
    if best_penalty:
        output.append(best_penalty)

    # Charging/external energy permissions
    external_patterns = [
        (r"((?:energy|power).{0,250}?(?:procured|sourced).{0,120}?(?:power\s+exchange|green\s+market|bilateral).{0,500})", .92),
        (r"((?:charging|charge).{0,250}?(?:exchange|green\s+market|bilateral|external\s+source).{0,500})", .94),
    ]
    ext_candidates = []
    for pattern, confidence in external_patterns:
        for match in re.finditer(pattern, normalized, re.I | re.S):
            ext_candidates.append(Evidence(
                "Charging / External Energy Conditions",
                " ".join(match.group(1).split())[:1000],
                "Text",
                confidence,
                _window(normalized, match.start(), match.end(), 280),
                pattern=pattern,
            ))
    best_external = _best(ext_candidates)
    if best_external:
        output.append(Evidence(
            "External / Exchange Energy Allowed",
            "Yes",
            "Boolean",
            best_external.confidence,
            best_external.snippet,
            pattern=best_external.pattern,
        ))
        output.append(best_external)

    return output


def to_dicts(evidence: list[Evidence]) -> list[dict[str, Any]]:
    return [asdict(item) for item in evidence]
