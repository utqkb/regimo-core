import os
import yaml
import json
import requests
from datetime import datetime
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.dumpers import json_dumper
from linkml_runtime.utils.schemaview import SchemaView
from linkml.validators import JsonSchemaDataValidator

# Attempt to import the Python classes generated in Stage 3
# IMPORTANT: If you see 'unexpected keyword argument' errors, you must run:
# gen-python src/my_linkmk_schema/schema/my_linkmk_schema.yaml > src/my_linkmk_schema/datamodel/my_linkmk_schema.py
try:
    from my_linkmk_schema.datamodel.my_linkmk_schema import ProjectSubmission
except ImportError:
    print("Warning: Could not import generated datamodel. Ensure 'gen-python' was successful.")
    ProjectSubmission = None

def publish_to_oep(payload):
    """
    Simulates sending the validated payload to the OEP API.
    In a real scenario, you would use an actual API Key.
    """
    api_key = "" # Placeholder for the OEP API Key
    target_url = "https://open-energy-platform.org/api/v0/schema/regimo/tables/measurements/rows"
    
    print("\n[*] Step 5: Initiating API Handshake with OEP...")
    
    if not api_key:
        print("⚠️  DRY RUN MODE: No API Key found. Skipping actual network request.")
        print(f"👉 To go live, POST the payload to: {target_url}")
        return True

    # Real implementation would look like this:
    # try:
    #     response = requests.post(target_url, json=payload, headers={"Authorization": f"Token {api_key}"})
    #     response.raise_for_status()
    #     print("🚀 SUCCESS: Data is now live on the OEP!")
    # except Exception as e:
    #     print(f"❌ API ERROR: {e}")
    #     return False

def run_oep_bridge():
    """
    Simulates the 'Publish to OEP' process:
    1. Validates the YAML data against the LinkML rules.
    2. Converts the data into a Python object.
    3. Transforms the object into a JSON-LD payload.
    4. Attaches the @context for OEP interoperability.
    5. Sends the package to the OEP API.
    """
    
    schema_path = "src/my_linkmk_schema/schema/my_linkmk_schema.yaml"
    data_path = "examples/3phase_test.yaml"
    context_path = "artifacts/my_linkmk_schema.jsonld"

    print("--- 🚀 STARTING OEP BRIDGE SIMULATION ---")

    # 1. Validation Step (The Guardrail)
    print(f"[*] Step 1: Validating {data_path} against schema...")
    
    try:
        # We use SchemaView to properly parse the YAML file into a Schema object
        schemaview = SchemaView(schema_path)
        validator = JsonSchemaDataValidator(schemaview.schema)
        
        with open(data_path, 'r') as f:
            data_to_validate = yaml.safe_load(f)

        errors = validator.validate_dict(data_to_validate)
    except Exception as e:
        print(f"❌ ERROR: System error during validation setup: {e}")
        return
    
    if errors:
        print(f"❌ ERROR: Validation failed. Data is not OEP-ready.")
        for error in errors:
            print(f"  - {error}")
        return
    else:
        print("✅ SUCCESS: Data is valid and safe for publication.")

    # 2. Object Instantiation
    print("[*] Step 2: Instantiating RegiMo Python Model...")
    if ProjectSubmission:
        try:
            # We use the YAML loader to turn the raw file into a Python object
            project_obj = yaml_loader.load(data_path, target_class=ProjectSubmission)
        except TypeError as te:
            print(f"❌ ERROR: Python Datamodel Mismatch!")
            print(f"Details: {te}")
            print("\nFIX: Your Python classes are out of date. Run this command:")
            print(f"gen-python {schema_path} > src/my_linkmk_schema/datamodel/my_linkmk_schema.py")
            return
        except Exception as e:
            print(f"❌ ERROR: Failed to load data into Python model: {e}")
            return
    else:
        print("❌ ERROR: Python Datamodel missing. Check your Stage 3 setup.")
        return

    # 3. JSON-LD Conversion (The Interoperability Step)
    print("[*] Step 3: Converting to JSON-LD using OEO Context...")
    
    # Dump the Python object to a standard JSON format
    json_data = json.loads(json_dumper.dumps(project_obj))
    
    # Inject the @context from your automated artifact
    if os.path.exists(context_path):
        with open(context_path, 'r') as cf:
            context_data = json.load(cf)
            json_data["@context"] = context_data.get("@context", {})
    
    # 4. Final Package Preparation
    print("[*] Step 4: Finalizing OEP Publication Package...")
    
    publication_package = {
        "metadata_standard": "RegiMo-LinkML-v0.2.0",
        "publication_timestamp": datetime.now().isoformat(),
        "target_platform": "Open Energy Platform (OEP)",
        "payload": json_data
    }

    print("\n--- 📦 FINAL OEP PAYLOAD (JSON-LD) ---")
    print(json.dumps(publication_package, indent=2))

    # 5. API Publication (The Handshake)
    publish_to_oep(publication_package)
    
    print("\n--- ✅ BRIDGE PROCESS COMPLETE ---")

if __name__ == "__main__":
    run_oep_bridge()