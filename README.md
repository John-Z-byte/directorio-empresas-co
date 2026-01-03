# Directorio de Empresas Colombia (RUES)

## A reproducible, file-based data engineering pipeline built on public RUES data

This project implements a **deterministic, versioned, file-based data pipeline** using public data from the **Registro Único Empresarial y Social (RUES)**, published on datos.gov.co by CONFECÁMARAS.

It is designed to demonstrate **sound data engineering practices**: explicit schemas, immutable runs, clear logging, and analytical readiness—without scraping, guessing, or hidden enrichment.

---

## Problem Statement

### Reliability issues in large public open-data pipelines

Public datasets at national scale often introduce challenges such as:

- Massive row counts with API pagination limits  
- Schema ambiguity and silent drift  
- Reprocessing without version control  
- Ad-hoc transformations that break reproducibility  

This project treats **data as an auditable artifact**, enforcing contracts and layered transformations to ensure consistency over time.

---

## Project Objective

### Build a production-style analytical pipeline that:

- Ingests **millions of records** from a public API (Socrata / SODA2)  
- Separates data into **Bronze → Silver → Gold** layers  
- Produces **analysis-ready datasets** without aggregation side effects  
- Enforces **explicit schema control and logging**  
- Serves as a **professional Data Engineering portfolio project**

This project **does not** scrape websites or invent missing data.  
All outputs strictly respect the original data contract.

---

## Data Source

- **Platform:** datos.gov.co  
- **Provider:** CONFECÁMARAS  
- **Technology:** Socrata Open Data API (SODA2)  
- **Volume:** ~9 million records  
- **Observed columns:** 36  
- **Canonical model:** 21 columns  

⚠️ The dataset does **not** include municipality, address, phone, or email.  
The pipeline preserves this limitation by design.

---

## Data Architecture

### Bronze Layer — Raw ingestion

- Paginated API ingestion  
- JSONL persistence  
- Immutable snapshot per run  
- Row, column, and timing logs  

