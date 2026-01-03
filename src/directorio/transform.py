# src/directorio/transform.py
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from directorio.config import DATA_DIR, CORE_COLUMNS
from directorio.logging_utils import setup_logger, StepTimer, file_mb

logger = setup_logger()

DATE_COLS = [
    "fecha_matricula",
    "fecha_renovacion",
    "fecha_vigencia",
    "fecha_cancelacion",
    "fecha_actualizacion",
]

# Fuerza estabilidad de schema: columnas que deben ser string sí o sí
FORCE_STRING_COLS = [
    # IDs / NITs / DV (pueden venir con nulls y pandas los vuelve float)
    "numero_identificacion",
    "nit",
    "digito_verificacion",
    "num_identificacion_representante_legal",
    # CIIU son códigos (a veces vienen como número, a veces como texto)
    "cod_ciiu_act_econ_pri",
    "cod_ciiu_act_econ_sec",
]

# Campos numéricos “seguros”
NUMERIC_COLS = [
    "codigo_camara",
    "matricula",
    "ultimo_ano_renovado",
]


def _latest_run_dir(bronze_dir: Path) -> Path:
    runs = [p for p in bronze_dir.glob("run_date=*") if p.is_dir()]
    if not runs:
        raise FileNotFoundError(f"No run_date folders in {bronze_dir}")
    return sorted(runs, key=lambda p: p.name)[-1]


def _normalize_strings(df: pd.DataFrame) -> pd.DataFrame:
    obj_cols = [c for c in df.columns if df[c].dtype == "object"]
    for c in obj_cols:
        df[c] = (
            df[c].astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
    return df


def bronze_to_silver_one_parquet(
    run_date: str,
    *,
    chunksize: int = 200_000,
) -> None:
    t = StepTimer.start("silver")

    bronze_run = DATA_DIR / "bronze" / f"run_date={run_date}"
    bronze_jsonl = bronze_run / "data.jsonl"
    bronze_manifest = bronze_run / "manifest.json"

    silver_run = DATA_DIR / "silver" / f"run_date={run_date}"
    silver_run.mkdir(parents=True, exist_ok=True)
    silver_parquet = silver_run / "empresas.parquet"

    logger.info(f"silver | start | run_date={run_date}")
    logger.info(f"silver | input={bronze_jsonl.as_posix()} size_mb={file_mb(bronze_jsonl)}")

    manifest = json.loads(bronze_manifest.read_text(encoding="utf-8"))
    logger.info(
        f"silver | bronze_manifest | rows={manifest.get('rows'):,} "
        f"cols_observed={manifest.get('columns_observed_count')} pages={manifest.get('pages')}"
    )

    expected = CORE_COLUMNS

    writer: pq.ParquetWriter | None = None
    total_rows = 0
    chunk_n = 0

    reader = pd.read_json(bronze_jsonl, lines=True, chunksize=chunksize)

    for chunk in reader:
        chunk_n += 1

        if chunk_n == 1:
            missing = [c for c in expected if c not in chunk.columns]
            extra = [c for c in chunk.columns if c not in expected]
            if missing:
                logger.error(f"silver | schema FAIL | missing_cols={missing}")
                raise ValueError("Schema mismatch: missing columns vs CORE_COLUMNS")
            if extra:
                logger.warning(f"silver | schema WARN | extra_cols_count={len(extra)} (will drop extras)")
            logger.info(f"silver | schema OK | expected_cols={len(expected)}")

        # Contract: keep only expected columns in order
        chunk = chunk[[c for c in expected if c in chunk.columns]].copy()

        # Normalize general strings
        chunk = _normalize_strings(chunk)

        # Dates (warning is ok; optimize later with format="ISO8601" if you want)
        for c in DATE_COLS:
            if c in chunk.columns:
                chunk[c] = pd.to_datetime(chunk[c], errors="coerce")

        # Force stable strings (critical for Parquet schema stability)
        for c in FORCE_STRING_COLS:
            if c in chunk.columns:
                chunk[c] = chunk[c].astype("string").str.strip()

        # Safe numerics
        for c in NUMERIC_COLS:
            if c in chunk.columns:
                chunk[c] = pd.to_numeric(chunk[c], errors="coerce")

        total_rows += len(chunk)

        if chunk_n == 1:
            dtypes_preview = {c: str(chunk[c].dtype) for c in chunk.columns[:12]}
            logger.info(f"silver | dtypes(sample)={dtypes_preview}")

        logger.info(f"silver | chunk={chunk_n} rows_chunk={len(chunk):,} rows_total={total_rows:,}")

        table = pa.Table.from_pandas(chunk, preserve_index=False)

        if writer is None:
            writer = pq.ParquetWriter(silver_parquet, table.schema, compression="snappy")

        writer.write_table(table)

    if writer is not None:
        writer.close()

    logger.info(f"silver | output={silver_parquet.as_posix()} size_mb={file_mb(silver_parquet)}")
    logger.info(f"silver | done | rows={total_rows:,} cols={len(expected)} seconds={t.done():.2f}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Bronze JSONL -> Silver Parquet (single file)")
    ap.add_argument("--run-date", type=str, default="", help="YYYY-MM-DD. If empty, uses latest run_date folder.")
    ap.add_argument("--chunksize", type=int, default=200_000, help="Rows per chunk (memory control).")
    args = ap.parse_args()

    bronze_dir = DATA_DIR / "bronze"
    if args.run_date:
        run_date = args.run_date
    else:
        run_date = _latest_run_dir(bronze_dir).name.split("run_date=")[1]

    bronze_to_silver_one_parquet(run_date, chunksize=args.chunksize)


if __name__ == "__main__":
    main()
