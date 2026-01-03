from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

# Pega tu base_url aquí (la que ya tienes)
BASE_URL = "https://www.datos.gov.co/resource/c82u-588k.json"

# Tamaño de página para SODA2 (Socrata)
PAGE_SIZE = 50000
TIMEOUT = 60

CORE_COLUMNS = [
    "codigo_camara",
    "camara_comercio",
    "matricula",
    "razon_social",
    "numero_identificacion",
    "nit",
    "digito_verificacion",
    "cod_ciiu_act_econ_pri",
    "cod_ciiu_act_econ_sec",
    "fecha_matricula",
    "fecha_renovacion",
    "ultimo_ano_renovado",
    "fecha_vigencia",
    "fecha_cancelacion",
    "estado_matricula",
    "tipo_sociedad",
    "organizacion_juridica",
    "categoria_matricula",
    "representante_legal",
    "num_identificacion_representante_legal",
    "fecha_actualizacion",
]
