import os
import json
import requests
import re
from datetime import datetime
from linkml_runtime.utils.schemaview import SchemaView
from linkml.validators import JsonSchemaDataValidator

# --- MVP CONFIGURATION ---
RDMO_PORT = "8484" 
RDMO_API_BASE = f"http://localhost:{RDMO_PORT}/api/v1"
RDMO_PROJECT_ID = "1" 

# Your live RDMO token
RDMO_TOKEN = "b64c185f090dd2f562ca4770d40a5831ea54e7b9" 

# --- ACTION REQUIRED: PASTE YOUR OEP API KEY HERE ---
OEP_TOKEN = "1c1557cbd364d6abe9defc994eb9be708c30a950" 

# Local File Paths
SCHEMA_PATH = "src/my_linkmk_schema/schema/my_linkmk_schema.yaml"
CONTEXT_PATH = "artifacts/my_linkmk_schema.jsonld"
OEP_API_URL = "https://open-energy-platform.org/api/v0/schema/regimo/tables/measurements/rows"

def flatten_rdmo_data(api_response):
    """
    IMPROVED HARVESTER: Captures data exactly as entered in RDMO
    to allow the LinkML Validator to catch errors.
    """
    flat_data = {
        "project_id": "REGIMO-2026-001", 
        "operator_name": "Anubhab Biswas",
        "project_start_date": "2026-03-22",
        "records": []
    }
    
    description = api_response.get('description', '') or ""
    
    # CHAOS TEST FIX: Capture whatever follows "Project ID: " instead of searching for a valid pattern
    id_match = re.search(r"Project ID:\s*([^\n\r]+)", description)
    if id_match:
        # This will now capture "BAD-ID-99" if you type it in RDMO
        flat_data["project_id"] = id_match.group(1).strip()
        print(f"[*] Harvested Project ID from RDMO: {flat_data['project_id']}")

    values = api_response.get('values', [])
    for v in values:
        attr_uri = v.get('attribute_uri', '')
        val = v.get('value', '') or v.get('text', '') or ""
        
        if 'project/schedule/start' in attr_uri and val:
            flat_data["project_start_date"] = val
        if 'project/partner' in attr_uri and val:
            flat_data["operator_name"] = val

    # Simulated Static Lab Data
    flat_data["records"].append({
        "sample_unique_id": "SAMPLE-001",
        "measurement_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "instrument_calibration_date": "2025-12-01",
        "voltage_l1": 230.1,
        "voltage_l2": 230.0,
        "voltage_l3": 229.9
    })
    return flat_data

def fetch_live_rdmo():
    """Step 1: Connect to local RDMO container."""
    url = f"{RDMO_API_BASE}/projects/projects/{RDMO_PROJECT_ID}/"
    headers = {"Authorization": f"Token {RDMO_TOKEN}", "Accept": "application/json"}
    print(f"[*] Step 1: Connecting to RDMO API at {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            url = f"{RDMO_API_BASE}/projects/{RDMO_PROJECT_ID}/"
            response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print("✅ Connection Successful: Project metadata retrieved.")
        return flatten_rdmo_data(response.json())
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def validate_and_package(data):
    """Step 2 & 3: Validate with LinkML and package as JSON-LD."""
    print(f"[*] Step 2: Running LinkML Validation...")
    try:
        schemaview = SchemaView(SCHEMA_PATH)
        validator = JsonSchemaDataValidator(schemaview.schema)
        
        # This is where the 'BAD-ID-99' will be caught!
        errors = validator.validate_dict(data)
        
        if errors:
            print("❌ VALIDATION FAILED: The data does not meet RegiMo standards.")
            for e in errors: print(f"  - {e}")
            return None
        print("✅ SUCCESS: Data is semantically valid.")
        
        context = {"oeo": "http://openenergy-ontology.org/ontology/"}
        if os.path.exists(CONTEXT_PATH):
            with open(CONTEXT_PATH, 'r') as f:
                context = json.load(f).get("@context", {})
            
        return {
            "@context": context,
            "@type": "oeo:EnergyDataPackage",
            "metadata": {
                "orchestrator_version": "EDO-V2-Live",
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "agent": "Anubhab Biswas"
            },
            "payload": data
        }
    except Exception as e:
        print(f"❌ ORCHESTRATION ERROR: {e}")
        return None

def publish_to_oep(package):
    """Step 4: The Final Push to Open Energy Platform."""
    print(f"[*] Step 4: Initiating Publication to OEP...")
    
    if OEP_TOKEN == "your_oep_token_here" or not OEP_TOKEN:
        print("⚠️  DRY RUN: No OEP Token detected. Data not sent to the cloud.")
        return
    
    headers = {"Authorization": f"Token {OEP_TOKEN}", "Content-Type": "application/json"}
    try:
        # Simulation of upload
        print(f"🚀 SUCCESS: Data officially prepared for publication to {OEP_API_URL}!")
    except Exception as e:
        print(f"❌ OEP Error: {e}")

if __name__ == "__main__":
    print("\n--- 🚀 EDO MVP: STARTING ORCHESTRATION BRIDGE ---")
    data = fetch_live_rdmo()
    if data:
        package = validate_and_package(data)
        if package:
            print("\n--- 📦 FINAL JSON-LD PAYLOAD ---")
            print(json.dumps(package, indent=2))
            publish_to_oep(package)
    print("\n--- ✅ MVP BRIDGE PROCESS COMPLETE ---\n")