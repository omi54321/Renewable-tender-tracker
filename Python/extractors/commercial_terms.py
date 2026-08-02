from __future__ import annotations

import re
from typing import Any


def extract_commercial_terms(text: str) -> dict[str, Any]:
    normalized = " ".join(text.split())
    result: dict[str, Any] = {
        "Minimum PLF %": None,
        "Monthly Minimum / Reconciliation": "Not verified",
        "Annual PLF / CUF / Energy Requirement": "Not verified",
        "Allowed Shortfall / Availability Tolerance": "Not verified",
        "Under-Supply Penalty": "Not verified",
        "External / Exchange Energy Allowed": "Not verified",
        "Maximum External Energy": "Not verified",
        "Charging / External Energy Conditions": "Not verified",
        "Third-Party / Merchant Use": "Not verified",
    }

    plf = re.search(r"(?:minimum|annual|monthly).{0,40}(?:plf|cuf).{0,20}(\d+(?:\.\d+)?)\s*%", normalized, re.I)
    if plf:
        result["Minimum PLF %"] = float(plf.group(1))

    shortfall = re.search(r"((?:shortfall|under[- ]supply).{0,350})", normalized, re.I)
    if shortfall:
        result["Under-Supply Penalty"] = shortfall.group(1)[:350]

    external = re.search(r"((?:exchange|green market|bilateral).{0,350})", normalized, re.I)
    if external:
        result["External / Exchange Energy Allowed"] = "Potentially allowed — review extracted condition"
        result["Charging / External Energy Conditions"] = external.group(1)[:350]

    merchant = re.search(r"((?:merchant|third[- ]party).{0,350})", normalized, re.I)
    if merchant:
        result["Third-Party / Merchant Use"] = merchant.group(1)[:350]

    return result
