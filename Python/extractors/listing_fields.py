from __future__ import annotations

import re
from typing import Any


TECHNOLOGY_RULES = [
    (r"solar\s*\+\s*bess|solar.{0,80}battery", "Solar + BESS"),
    (r"firm and dispatchable|\bfdre\b", "FDRE"),
    (r"wind[- ]solar hybrid|hybrid renewable", "Hybrid"),
    (r"battery energy storage|\bbess\b", "BESS"),
    (r"pumped storage|\bphes\b|\bpsp\b", "Pumped Storage"),
    (r"\bwind\b", "Wind"),
    (r"\bsolar\b|solar pv", "Solar"),
]


def _number(pattern: str, text: str):
    match = re.search(pattern, text, re.I | re.S)
    return float(match.group(1).replace(",", "")) if match else None


def extract_listing_fields(record: dict[str, Any]) -> dict[str, Any]:
    text = " ".join(str(record.get(k, "")) for k in ("Title", "Raw Text"))
    output = dict(record)
    output["Technology"] = "Other"

    for pattern, technology in TECHNOLOGY_RULES:
        if re.search(pattern, text, re.I):
            output["Technology"] = technology
            break

    pair = re.search(r"(\d+(?:\.\d+)?)\s*mw\s*/\s*(\d+(?:\.\d+)?)\s*mwh", text, re.I)
    if pair:
        output["Capacity MW"] = float(pair.group(1))
        output["Storage Hours"] = round(float(pair.group(2)) / float(pair.group(1)), 2)
        output["Storage Required"] = "Yes"
    else:
        output["Capacity MW"] = _number(r"(\d+(?:\.\d+)?)\s*mw\b", text)
        output["Storage Hours"] = _number(r"(\d+(?:\.\d+)?)\s*(?:hour|hours|hrs)\b", text)
        output["Storage Required"] = "Yes" if output["Storage Hours"] else "No"

    if re.search(r"corrigendum|amendment", text, re.I):
        output["Status"] = "Corrigendum"
    elif re.search(r"extended|extension|revised.{0,20}date", text, re.I):
        output["Status"] = "Extended"
    else:
        output["Status"] = "Open"

    output["Remarks"] = text[:1000]
    return output
