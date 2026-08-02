from __future__ import annotations

import argparse
import json
import logging
from datetime import date, datetime
from pathlib import Path

from Python.connectors.registry import load_connector
from Python.core.merge import build_active_database
from Python.extractors.listing_fields import extract_listing_fields
from Python.workbook.writer import read_master, write_master


def configure_logging() -> None:
    Path("Logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler("Logs/latest_run.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", default="Output/Renewable_Tender_Tracker_V13.xlsx")
    parser.add_argument("--agencies", default="Config/agencies.json")
    parser.add_argument("--rules", default="Config/scope_rules.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    configure_logging()
    logger = logging.getLogger("daily_update")
    agencies = json.loads(Path(args.agencies).read_text(encoding="utf-8"))
    rules = json.loads(Path(args.rules).read_text(encoding="utf-8"))
    workbook_path = Path(args.workbook)

    previous = read_master(workbook_path)
    scanned = []
    health = []

    for config in agencies:
        if not config.get("enabled", True):
            continue
        started = datetime.utcnow()
        connector = load_connector(config["module"], config)
        result = connector.run()
        accepted = []
        for raw in result.records:
            accepted.append(extract_listing_fields(raw))
        scanned.extend(accepted)
        health.append({
            "agency": config["agency"],
            "module": config["module"],
            "source_url": config["source_url"],
            "started": started.isoformat(),
            "finished": (result.finished or datetime.utcnow()).isoformat(),
            "records_found": len(result.records),
            "accepted": len(accepted),
            "status": result.status,
            "errors": result.errors,
        })
        logger.info("%s: %s records; %s", config["agency"], len(result.records), result.status)

    active, exclusions = build_active_database(previous, scanned, rules, date.today())
    report = {
        "version": "13.0",
        "run_time": datetime.now().isoformat(timespec="seconds"),
        "previous_records": len(previous),
        "scanned_records": len(scanned),
        "active_records": len(active),
        "excluded_records": len(exclusions),
        "connector_health": health,
    }
    Path("Logs/latest_run.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    Path("Logs/connector_health.json").write_text(json.dumps(health, indent=2, default=str), encoding="utf-8")

    if not args.dry_run:
        write_master(workbook_path, active, exclusions, "Success")

    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
