from __future__ import annotations

from datetime import date
from typing import Any

from Python.core.hashing import stable_hash
from Python.core.scope import active_on_date, eligibility


def merge_corrigenda(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    existing_dates = list(existing.get("Corrigendum Date(s)", []) or [])
    new_dates = incoming.get("Corrigendum Date(s)", []) or []

    if isinstance(existing_dates, str):
        existing_dates = [d.strip() for d in existing_dates.split(";") if d.strip()]
    if isinstance(new_dates, str):
        new_dates = [d.strip() for d in new_dates.split(";") if d.strip()]

    all_dates = sorted(set(existing_dates + new_dates))
    existing["Corrigendum Date(s)"] = "; ".join(all_dates)
    existing["Latest Corrigendum Date"] = all_dates[-1] if all_dates else existing.get("Latest Corrigendum Date")
    existing["Corrigendum Count"] = len(all_dates)

    if incoming.get("Corrigendum Details"):
        existing["Corrigendum Details"] = incoming["Corrigendum Details"]

    if incoming.get("Bid Submission Date"):
        existing["Bid Submission Date"] = incoming["Bid Submission Date"]

    if incoming.get("Status") in {"Extended", "Corrigendum"}:
        existing["Status"] = incoming["Status"]

    return existing


def build_active_database(
    previous: list[dict[str, Any]],
    scanned: list[dict[str, Any]],
    rules: dict[str, Any],
    scan_date: date,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_key = {
        f"{str(row.get('Agency','')).upper()}|{str(row.get('Tender Number','')).upper()}": row
        for row in previous
    }
    exclusions: list[dict[str, Any]] = []

    for row in scanned:
        eligible, reason = eligibility(row, rules)
        if not eligible:
            exclusions.append({**row, "Exclusion Reason": reason})
            continue

        key = f"{str(row.get('Agency','')).upper()}|{str(row.get('Tender Number','')).upper()}"
        if key in by_key:
            current = by_key[key]
            current = merge_corrigenda(current, row)
            for field, value in row.items():
                if value not in (None, ""):
                    current[field] = value
            current["Source Record Hash"] = stable_hash(row)
            by_key[key] = current
        else:
            row["Source Record Hash"] = stable_hash(row)
            by_key[key] = row

    active: list[dict[str, Any]] = []
    for row in by_key.values():
        is_active, reason = active_on_date(row, scan_date, rules)
        if is_active:
            active.append(row)
        else:
            exclusions.append({**row, "Exclusion Reason": reason})

    return active, exclusions
