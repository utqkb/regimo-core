import os
import requests
from typing import List
from neo4j import GraphDatabase
from my_linkmk_schema.datamodel.my_linkmk_schema import RDMOProject, QuestionnaireAnswer

RDMO_BASE_URL = "http://localhost:8484/api/v1/projects"
AUTH = ("admin", "admin1234")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")  # adjust if different

def fetch_rdmo_projects() -> List[RDMOProject]:
    response = requests.get(f"{RDMO_BASE_URL}/projects/", auth=AUTH)
    response.raise_for_status()
    raw_projects = response.json().get("results", [])

    validated_projects = []

    for raw_proj in raw_projects:
        proj_id = raw_proj["id"]
        
        val_response = requests.get(f"{RDMO_BASE_URL}/projects/{proj_id}/values/", auth=AUTH)
        val_response.raise_for_status()
        raw_values = val_response.json()

        answers = []
        linked_datasets = []

        for val in raw_values:
            val_text = val.get("text") or val.get("option_uri") or ""
            attr_path = val.get("attribute_uri", "")

            if "project/dataset/id" in attr_path and val_text:
                linked_datasets.append(val_text)

            answer = QuestionnaireAnswer(
                attribute_path=attr_path,
                value_text=val_text,
                value_datatype=val.get("value_type", "text"),
                unit=val.get("unit", "")
            )
            answers.append(answer)

        project_obj = RDMOProject(
            rdmo_id=proj_id,
            title=raw_proj["title"],
            description=raw_proj.get("description", ""),
            created=raw_proj.get("created"),
            updated=raw_proj.get("updated"),
            answers=answers,
            linked_oep_datasets=linked_datasets
        )
        validated_projects.append(project_obj)

    return validated_projects

def ingest_to_neo4j(projects: List[RDMOProject], uri: str, auth: tuple):
    query = """
    UNWIND $projects AS proj
    MERGE (p:RDMOProject {rdmo_id: proj.rdmo_id})
    SET p.title = proj.title,
        p.description = proj.description,
        p.created = proj.created,
        p.updated = proj.updated

    WITH p, proj
    UNWIND proj.answers AS ans
    MERGE (a:QuestionnaireAnswer {
        project_id: proj.rdmo_id,
        attribute_path: ans.attribute_path
    })
    SET a.value_text = ans.value_text,
        a.value_datatype = ans.value_datatype,
        a.unit = ans.unit
    MERGE (p)-[:HAS_ANSWER]->(a)

    WITH p, proj
    UNWIND proj.linked_oep_datasets AS dataset_id
    MERGE (m:MeasurementRecord {sample_unique_id: dataset_id})
    MERGE (p)-[:ASSOCIATED_WITH_MEASUREMENT]->(m)
    """

    # Prepare parameterized data payload
    payload = []
    for p in projects:
        payload.append({
            "rdmo_id": p.rdmo_id,
            "title": p.title,
            "description": p.description,
            "created": p.created,
            "updated": p.updated,
            "linked_oep_datasets": p.linked_oep_datasets,
            "answers": [
                {
                    "attribute_path": a.attribute_path,
                    "value_text": a.value_text,
                    "value_datatype": a.value_datatype,
                    "unit": a.unit
                } for a in p.answers
            ]
        })

    with GraphDatabase.driver(uri, auth=auth) as driver:
        with driver.session() as session:
            session.run(query, projects=payload)
            print("Successfully populated Neo4j Knowledge Graph!")

if __name__ == "__main__":
    print("Harvesting projects from RDMO API...")
    projects = fetch_rdmo_projects()
    print(f"Harvested {len(projects)} RDMO Project(s).")
    
    try:
        print(f"Ingesting into Neo4j at {NEO4J_URI}...")
        ingest_to_neo4j(projects, NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD))
    except Exception as e:
        print(f"Neo4j Connection/Ingestion Note: {e}")
