from __future__ import annotations
import json
from pathlib import Path
from directorio.logging_utils import setup_logger, StepTimer
from directorio.config import DATA_DIR

logger = setup_logger()

def bronze_check(run_date: str) -> None:
    t = StepTimer.start("bronze_check")
    p = DATA_DIR / "bronze" / f"run_date={run_date}" / "data.jsonl"
    m = DATA_DIR / "bronze" / f"run_date={run_date}" / "manifest.json"

    logger.info(f"bronze_check | start | run_date={run_date}")
    manifest = json.loads(m.read_text(encoding="utf-8"))

    first = None
    last = None
    count = 0
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            if first is None:
                first = obj
            last = obj
            count += 1

    logger.info(f"bronze_check | lines_counted={count:,} manifest_rows={manifest['rows']:,}")
    logger.info(f"bronze_check | first_keys={sorted(list(first.keys()))}")
    logger.info(f"bronze_check | last_keys={sorted(list(last.keys()))}")
    logger.info(f"bronze_check | done | seconds={t.done():.2f}")

if __name__ == "__main__":
    bronze_check("2026-01-03")
