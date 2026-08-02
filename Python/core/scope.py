from __future__ import annotations

from datetime import date, datetime
from typing import Any


def _text(record: dict[str, Any]) -> str:
    return " ".join(str(v or "") for v in record.values()).lower()


def eligibility(record: dict[str, Any], rules: dict[str, Any]) -> tuple[bool, str]:
    text = _text(record)

    excluded_keyword_groups = []
    if rules.get("exclude_rooftop"):
        excluded_keyword_groups.append(("Rooftop solar excluded", ("rooftop", "roof top")))
    if rules.get("exclude_kusum"):
        excluded_keyword_groups.append(("PM-KUSUM excluded", ("pm-kusum", "kusum component", "component-a")))
    if rules.get("exclude_supply_installation"):
        excluded_keyword_groups.append(("Supply / installation excluded", (
            "supply and installation", "supply & installation", "installation of",
        )))
    if rules.get("exclude_epc_turnkey_bos"):
        excluded_keyword_groups.append(("EPC / turnkey / BoS excluded", (
            "epc", "turnkey", "balance of system", " bos ",
        )))
    if rules.get("exclude_om_only"):
        excluded_keyword_groups.append(("O&M-only tender excluded", (
            "operation and maintenance", "o&m of", "annual maintenance",
        )))

    for reason, keywords in excluded_keyword_groups:
        if any(keyword in text for keyword in keywords):
            return False, reason

    capacity = record.get("Capacity MW")
    if capacity in (None, ""):
        if rules.get("require_confirmed_capacity", True):
            return False, "Capacity not confirmed"
    else:
        try:
            capacity_value = float(str(capacity).replace(",", ""))
        except ValueError:
            return False, "Invalid capacity"
        if capacity_value < float(rules.get("minimum_capacity_mw", 100)):
            return False, "Capacity below configured minimum"

    return True, ""


def active_on_date(record: dict[str, Any], scan_date: date, rules: dict[str, Any]) -> tuple[bool, str]:
    status = str(record.get("Status", "")).strip()
    if status in set(rules.get("closed_statuses", [])):
        return False, f"Status is {status}"

    deadline = record.get("Bid Submission Date")
    if isinstance(deadline, datetime):
        deadline = deadline.date()

    if (
        deadline
        and deadline < scan_date
        and rules.get("remove_expired_without_verified_extension", True)
    ):
        return False, "Deadline expired without verified extension"

    return True, ""
