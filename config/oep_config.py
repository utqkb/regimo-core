
from shared_utils.project_handling import find_project_root, find_workspace_root

BASE_DIR = find_workspace_root()                   # path to root
SUB_BASE_DIR = find_project_root()                 # path to subproject
MODELS_DIR = BASE_DIR / "shared/models"
RESULT_DIR = BASE_DIR / "shared/results"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

RAW_METADATA_DIR = BASE_DIR / "shared/metadata"
METADATA_DIR = RAW_METADATA_DIR / "preprocessed"
SCHEMA_PATH = MODELS_DIR / "data-model-oep.yaml"

OEP_API_BASE = "https://openenergyplatform.org/api/v0"
SCHEMA = "model_draft"                             # Common schemas: 'model_draft', 'sandbox', 'public'
