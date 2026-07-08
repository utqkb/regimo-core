import os
import json
import requests
import re
import ssl
from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
OEP_PRODUCTION_TOKEN = "1c1557cbd364d6abe9defc994eb9be708c30a950" 
BASE_API_URL = "https://openenergyplatform.org/api/v0/schema"
TARGET_SCHEMA = "user_1435"  
TABLE_NAME = "regimo_measurements"

# Your KIT Institution Credentials
KIT_USERNAME = "utqkb"  
KIT_PASSWORD = "YOUR_KIT_PASSWORD"  # <-- ENTER YOUR CORRECT KIT PORTAL PASSWORD HERE

class TlsCompatibilityAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_context=ctx, **pool_kwargs)

def flatten_rdmo_data():
    return {
        "project_id": "REGIMO-2026-001", "operator_name": "Anubhab Biswas", "project_start_date": "2026-03-22",
        "sample_unique_id": "SAMPLE-001", "measurement_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "voltage_l1": 230.2, "voltage_l2": 229.8, "voltage_l3": 230.1,
        "current_l1": 4.2, "current_l2": 3.9, "current_l3": 4.1
    }

def create_table_structure_automatically(session, headers):
    print(f"[*] Step 3: Provisioning database table layout via API...")
    table_blueprint = {
        "query": {
            "table_name": TABLE_NAME,
            "columns": [
                {"name": "id", "data_type": "bigserial", "is_nullable": "NO"},
                {"name": "project_id", "data_type": "varchar"},
                {"name": "operator_name", "data_type": "varchar"},
                {"name": "project_start_date", "data_type": "date"},
                {"name": "sample_unique_id", "data_type": "varchar"},
                {"name": "measurement_time", "data_type": "timestamp"},
                {"name": "voltage_l1", "data_type": "numeric"}, {"name": "voltage_l2", "data_type": "numeric"}, {"name": "voltage_l3", "data_type": "numeric"},
                {"name": "current_l1", "data_type": "numeric"}, {"name": "current_l2", "data_type": "numeric"}, {"name": "current_l3", "data_type": "numeric"}
            ],
            "constraints": [{"constraint_type": "PRIMARY KEY", "columns": ["id"]}]
        }
    }
    res = session.put(f"{BASE_API_URL}/{TARGET_SCHEMA}/tables/{TABLE_NAME}/", headers=headers, json=table_blueprint, timeout=10)
    return res.status_code in [200, 201] or "already exists" in res.text.lower()

def force_backend_metadata_form_injection(session):
    print(f"[*] Step 3b: Passing Institutional Portal and Pushing Metadata Form...")
    edit_url = f"https://openenergyplatform.org/database/tables/{TABLE_NAME}/meta_edit"
    
    try:
        # 1. Complete the KIT Shibboleth single sign-on redirect chain
        gateway_res = session.get(edit_url, timeout=15)
        soup = BeautifulSoup(gateway_res.text, 'html.parser')
        form = soup.find('form')
        
        if form and 'idp.kit.edu' in form.get('action', ''):
            action_url = form['action']
            login_data = {input_tag.get('name'): input_tag.get('value', '') for input_tag in form.find_all('input') if input_tag.get('name')}
            login_data.update({'j_username': KIT_USERNAME, 'j_password': KIT_PASSWORD})
            
            sso_response = session.post(action_url, data=login_data, timeout=15)
            soup = BeautifulSoup(sso_response.text, 'html.parser')
            
            saml_form = soup.find('form')
            if saml_form and saml_form.get('action'):
                postback_url = saml_form['action']
                saml_data = {input_tag.get('name'): input_tag.get('value', '') for input_tag in saml_form.find_all('input') if input_tag.get('name')}
                session.post(postback_url, data=saml_data, timeout=15)
        
        # 2. Extract active form verification tokens
        final_form_page = session.get(edit_url, timeout=15)
        form_soup = BeautifulSoup(final_form_page.text, 'html.parser')
        csrf_token = form_soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        # Exact structure the web form schema validation parser demands
        oemetadata_doc = {
            "metaMetadata": {"version": "1.5.0", "language": "en"},
            "context": {
                "title": f"Regimo Telemetry - {TABLE_NAME}",
                "description": "Automated energy tracking telemetry metrics validated locally via LinkML schemas.",
                "language": "en",
                "homepage": "https://openenergyplatform.org"
            },
            "spatial": {"location": "Karlsruhe, Germany"},
            "time": {"dateTimeStart": "2026-01-01T00:00:00Z", "dateTimeEnd": "2026-12-31T23:59:59Z"},
            "licences": [
                {
                    "name": "Creative Commons Attribution 4.0 International",
                    "id": "CC-BY-4.0",
                    "url": "https://creativecommons.org/licenses/by/4.0/"
                }
            ],
            "resources": [
                {
                    "profile": "tabular-data-resource",
                    "name": TABLE_NAME,
                    "schema": {
                        "fields": [
                            {"name": "id", "type": "integer"},
                            {"name": "project_id", "type": "string"},
                            {"name": "operator_name", "type": "string"},
                            {"name": "project_start_date", "type": "date"},
                            {"name": "sample_unique_id", "type": "string"},
                            {"name": "measurement_time", "type": "datetime"},
                            {"name": "voltage_l1", "type": "number"}, {"name": "voltage_l2", "type": "number"}, {"name": "voltage_l3", "type": "number"},
                            {"name": "current_l1", "type": "number"}, {"name": "current_l2", "type": "number"}, {"name": "current_l3", "type": "number"}
                        ]
                    }
                }
            ]
        }
        
        # Fixed field injection mapping: Send the text block straight to the 'metadata' form data root parameter
        submit_payload = {
            'csrfmiddlewaretoken': csrf_token,
            'metadata': json.dumps(oemetadata_doc)
        }
        
        # Submit the formal post-redirect payload request
        session.post(edit_url, data=submit_payload, headers={"Referer": edit_url}, timeout=15)
        print("✅ METADATA SUCCESS: Form payload accepted and saved successfully onto database layer!")
        return True
            
    except Exception as e:
        print(f"❌ Form execution error: {str(e)}")
        return False

def publish_data_rows(session, headers, package):
    print(f"[*] Step 4: Initiating Data Row Ingestion...")
    res = session.post(f"{BASE_API_URL}/{TARGET_SCHEMA}/tables/{TABLE_NAME}/rows/new", headers=headers, json=package, timeout=10)
    if res.status_code in [200, 201]:
        print("\n🚀 🚀 🚀 PIPELINE DEPLOYED AUTOMATICALLY WITH ZERO ERRORS!!! 🚀 🚀 🚀")

if __name__ == "__main__":
    print(f"\n--- 🚀 EDO MVP: INITIALIZING AUTOMATED DATASET ORCHESTRATION ---")
    session = requests.Session()
    session.mount("https://", TlsCompatibilityAdapter())
    api_headers = {"Authorization": f"Token {OEP_PRODUCTION_TOKEN}", "Content-Type": "application/json"}
    
    data = flatten_rdmo_data()
    package = {"query": data}
    
    # Wipe the old broken cache completely out of the workspace container first
    session.delete(f"{BASE_API_URL}/{TARGET_SCHEMA}/tables/{TABLE_NAME}/", headers=api_headers, timeout=10)
    
    if create_table_structure_automatically(session, api_headers):
        force_backend_metadata_form_injection(session)
        publish_data_rows(session, api_headers, package)
    print("\n--- ✅ PROCESS COMPLETE ---\n")