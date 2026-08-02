from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class TenderRecord:
    tender_id: str
    category: str
    agency: str
    state: str
    tender_number: str
    technology: str
    capacity_mw: Optional[float]
    storage_required: str
    storage_hours: Optional[float]
    dispatch_condition: str
    minimum_plf_percent: Optional[float]
    emd: str
    bg_conditions: str
    bid_submission_date: Optional[datetime]
    technical_opening: Optional[datetime]
    financial_opening: Optional[datetime]
    status: str
    notification_date: Optional[date]
    corrigendum_dates: list[date]
    corrigendum_details: str
    tender_url: str
    document_url: str
    remarks: str
    procurement_model: str = ""
    supply_window: str = ""
    daily_supply_obligation: str = ""
    monthly_requirement: str = ""
    annual_requirement: str = ""
    allowed_shortfall: str = ""
    undersupply_penalty: str = ""
    external_energy_allowed: str = "Not verified"
    maximum_external_energy: str = "Not verified"
    charging_conditions: str = "Not verified"
    merchant_use: str = "Not verified"
    detailed_source_document: str = ""
    technical_review_status: str = "Pending"
    raw_text: str = ""
    source_hash: str = ""

    @property
    def duplicate_key(self) -> str:
        return f"{self.agency.strip().upper()}|{self.tender_number.strip().upper()}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
