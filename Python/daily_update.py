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
    Path("Logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s", handlers=[logging.FileHandler("Logs/latest_run.log",encoding="utf-8"),logging.StreamHandler()])

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--workbook",default="Output/Renewable_Tender_Tracker_V14.xlsx")
    parser.add_argument("--agencies",default="Config/agencies.json")
    parser.add_argument("--rules",default="Config/scope_rules.json")
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    configure_logging(); logger=logging.getLogger("daily_update")
    agencies=json.loads(Path(args.agencies).read_text(encoding="utf-8"))
    rules=json.loads(Path(args.rules).read_text(encoding="utf-8"))
    workbook_path=Path(args.workbook)
    previous=read_master(workbook_path)
    scanned=[]; health=[]
    for config in agencies:
        if not config.get("enabled",True): continue
        started=datetime.utcnow()
        try:
            result=load_connector(config["module"],config).run()
            accepted=[extract_listing_fields(raw) for raw in result.records]
            scanned.extend(accepted)
            errors=result.errors
            status=result.status
        except Exception as exc:
            accepted=[]; errors=[str(exc)]; status="Failed"
            logger.exception("Connector failed: %s",config.get("agency"))
        health.append({"agency":config.get("agency"),"module":config.get("module"),"source_url":config.get("source_url"),"started":started.isoformat(),"finished":datetime.utcnow().isoformat(),"records_found":len(accepted),"accepted":len(accepted),"status":status,"errors":errors})
        logger.info("%s: %s accepted; %s",config.get("agency"),len(accepted),status)
    active,exclusions=build_active_database(previous,scanned,rules,date.today())
    report={"version":"14.0","run_time":datetime.now().isoformat(timespec="seconds"),"dry_run":args.dry_run,"previous_records":len(previous),"scanned_records":len(scanned),"active_records":len(active),"excluded_records":len(exclusions),"connector_health":health}
    logs=Path("Logs"); logs.mkdir(parents=True,exist_ok=True)
    (logs/"latest_run.json").write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    (logs/"connector_health.json").write_text(json.dumps(health,indent=2,default=str),encoding="utf-8")
    if not args.dry_run: write_master(workbook_path,active,exclusions,"Success")
    print(json.dumps(report,indent=2,default=str)); return 0
if __name__ == "__main__": raise SystemExit(main())
