Contexto del Proyecto — Directorio de Empresas (Colombia)

Estoy desarrollando un proyecto de Data Engineering basado en datos públicos del Registro Único Empresarial y Social (RUES) publicados en datos.gov.co (CONFECÁMARAS).

Objetivo general

Construir un pipeline de datos reproducible y versionado que:

Ingesta datos masivos (millones de registros) desde una API pública (Socrata / SODA2)

Estructure los datos en capas Bronze → Silver → Gold

Produzca datasets analíticos listos para consumo (Parquet)

Sirva como proyecto de portfolio profesional de Data Engineering

El foco es ingeniería de datos, no web scraping ni directorios comerciales.

Fuente de datos

Dataset: Personas Naturales, Personas Jurídicas y Entidades Sin Ánimo de Lucro

Plataforma: datos.gov.co

Tecnología de acceso: Socrata Open Data API (SODA2)

Volumen: ~9 millones de filas, ~36 columnas

Campos clave disponibles:

Identificación (NIT / número identificación)

Razón social

Estado de matrícula (ACTIVA, CANCELADA, etc.)

Fechas (matrícula, renovación, cancelación, actualización)

Tipo de sociedad / organización jurídica

CIIU

Representante legal

⚠️ El dataset NO contiene municipio, dirección, teléfono ni email.
El proyecto no intenta forzar esos datos.

Arquitectura implementada
Bronze

Ingesta paginada desde la API

Persistencia como JSONL

Snapshots versionados por fecha de corrida

Datos crudos, inmutables

Silver

Conversión a Parquet

Normalización de strings

Tipado de fechas

Selección explícita de columnas

Modelo base analítico

Gold

Datos estructurados, sin agregaciones

Tabla canónica lista para BI / análisis

Una versión por corrida (sin acumulación)

Stack técnico

Python 3.14

requests

pandas

pyarrow

YAML

Parquet

PowerShell (Windows)

Arquitectura file-based (sin base de datos)

Estructura del proyecto
directorio-empresas-co/
├── src/
│   └── directorio/
│       ├── ingest_soda.py      # Ingesta API (Bronze)
│       ├── transform.py        # Bronze → Silver
│       ├── publish.py          # Silver → Gold
│       └── config.py           # Contrato de columnas
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── configs/
│   └── targets.yml
├── requirements.txt
└── README.md

Estado actual

Ingesta confirmada (Bronze con datos reales)

Silver en Parquet creado correctamente

Gold generado como tabla estructurada

README documentado

Proyecto listo para extenderse

Próximo foco (a definir en la nueva conversación)

Cargas incrementales

Comparación entre runs

Métricas de churn

Tests de calidad

Orquestación

Analítica temporal avanzada

Intención

Este proyecto está pensado para:

Demostrar criterio de diseño

Mostrar buenas prácticas reales

Ser entendible por ingenieros senior y recruiters

Escalar sin rehacer arquitectura