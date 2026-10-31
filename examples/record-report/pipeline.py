"""Coordinate a selection and report; configuration errors occur before run."""
from report import build_report, serialize_report
from select_records import select_records
from settings import Settings


def run(records, settings=None):
    config = Settings() if settings is None else settings
    try:
        chosen = select_records(records, config.minimum, config.limit)
        report = build_report(chosen)
        return {"ok": True, "report": report, "text": serialize_report(report)}
    except (KeyError, TypeError) as error:
        return {"ok": False, "reason": type(error).__name__}
