from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import requests

from directorio.config import DATA_DIR, BASE_URL, PAGE_SIZE, TIMEOUT
from directorio.logging_utils import setup_logger, StepTimer

logger = setup_logger()

def run_date_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()

def bronze_outdir(run_date: str) -> Path:
    out = DATA_DIR / "bronze" / f"run_date={run_date}"
    out.mkdir(parents=True, exist_ok=True)
    return out

def fetch_page(session: requests.Session, offset: int, limit: int) -> list[dict]:
    params = {"$limit": limit, "$offset": offset}
    r = session.get(BASE_URL, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        raise ValueError("La API no devolvió una lista JSON (esperado SODA2).")
    return data

def ingest_bronze() -> None:
    t = StepTimer.start("bronze")
    run_date = run_date_utc()
    outdir = bronze_outdir(run_date)
    out_jsonl = outdir / "data.jsonl"
    out_manifest = outdir / "manifest.json"

    logger.info(f"bronze | start | run_date={run_date}")
    logger.info(f"bronze | base_url={BASE_URL}")
    logger.info(f"bronze | output={out_jsonl.as_posix()}")

    total_rows = 0
    cols_union: set[str] = set()
    pages = 0

    with requests.Session() as s, out_jsonl.open("w", encoding="utf-8") as f:
        offset = 0
        while True:
            page = fetch_page(s, offset=offset, limit=PAGE_SIZE)
            if not page:
                break

            pages += 1
            total_rows += len(page)

            # columnas observadas (unión)
            for row in page:
                cols_union.update(row.keys())
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

            logger.info(f"bronze | page={pages} rows_page={len(page):,} rows_total={total_rows:,} offset={offset:,}")

            # si vino menos que el límite, se acabó
            if len(page) < PAGE_SIZE:
                break
            offset += PAGE_SIZE

    manifest = {
        "run_date": run_date,
        "base_url": BASE_URL,
        "page_size": PAGE_SIZE,
        "pages": pages,
        "rows": total_rows,
        "columns_observed_count": len(cols_union),
        "columns_observed_sample": sorted(list(cols_union))[:30],  # muestra
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seconds": round(t.done(), 2),
    }
    out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info(f"bronze | done | rows={total_rows:,} cols_observed={len(cols_union)} pages={pages} seconds={manifest['seconds']}")

if __name__ == "__main__":
    ingest_bronze()
