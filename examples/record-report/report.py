"""Turn selected records into a report value."""
import json


def build_report(records):
    identifiers = [str(record["id"]) for record in records]
    return {"count": len(identifiers), "identifiers": identifiers}


def serialize_report(report):
    return json.dumps(report, ensure_ascii=False, sort_keys=True)
