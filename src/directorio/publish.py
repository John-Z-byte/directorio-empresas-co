# src/directorio/publish.py
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pyarrow.parquet as pq

from directorio.config import DATA_DIR, CORE_COLUMNS
from directorio.logging_utils import setup_logger, StepTimer, file_mb

logger = setup_logger()


def _latest_run_dir(silver_dir: Path) -> Path:
    runs = [p for p in silver_dir.glob("run_date=*") if p.is_dir()]
    if not runs:
        raise FileNotFoundError(f"No run_date folders in {silver_dir}")
    return sorted(runs, key=lambda p: p.name)[-1]


def publish_gold(run_date: str) -> None:
    t = StepTimer.start("gold")

    silver_path = DATA_DIR / "silver" / f"run_date={run_date}" / "empresas.parquet"
    if not silver_path.exists():
        raise FileNotFoundError(f"Silver parquet not found: {silver_path.as_posix()}")

    gold_dir = DATA_DIR / "gold" / f"run_date={run_date}"
    gold_dir.mkdir(parents=True, exist_ok=True)

    gold_path = gold_dir / "empresas.parquet"
    manifest_path = gold_dir / "manifest.json"

    logger.info(f"gold | start | run_date={run_date}")
    logger.info(f"gold | input={silver_path.as_posix()} size_mb={file_mb(silver_path)}")

    # Copy Parquet (fast, no recompute)
    shutil.copy2(silver_path, gold_path)

    # Validate quickly with pyarrow
    pf = pq.ParquetFile(gold_path)
    schema_cols = [f.name for f in pf.schema_arrow]
    rows = pf.metadata.num_rows

    missing = [c for c in CORE_COLUMNS if c not in schema_cols]
    extra = [c for c in schema_cols if c not in CORE_COLUMNS]

    if missing:
        logger.error(f"gold | schema FAIL | missing_cols={missing}")
        raise ValueError("Gold schema mismatch")
    if extra:
        logger.warning(f"gold | schema WARN | extra_cols={extra}")

    manifest = {
        "run_date": run_date,
        "rows": int(rows),
        "cols": int(len(schema_cols)),
        "columns": schema_cols,
        "source": "silver/empresas.parquet",
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_mb": file_mb(gold_path),
        "seconds": round(t.done(), 2),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info(f"gold | output={gold_path.as_posix()} size_mb={file_mb(gold_path)}")
    logger.info(f"gold | done | rows={rows:,} cols={len(schema_cols)} seconds={manifest['seconds']}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish Silver -> Gold (copy + validate + manifest)")
    ap.add_argument("--run-date", type=str, default="", help="YYYY-MM-DD. If empty, uses latest run_date in silver/.")
    args = ap.parse_args()

    silver_dir = DATA_DIR / "silver"
    if args.run_date:
        run_date = args.run_date
    else:
        run_date = _latest_run_dir(silver_dir).name.split("run_date=")[1]

    publish_gold(run_date)


if __name__ == "__main__":
    main()
