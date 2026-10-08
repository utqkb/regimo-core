import json
from pathlib import Path
import re
from collections import Counter
from sys import exit
import sys
from typing import Any

import matplotlib.pyplot as plt
import requests
from neo4j import Driver, GraphDatabase
from oep_analysis.oep_validation.linkml_validation_script import (
    LINKML_ERROR_COUNTER,
    save_linkml_report,
    validate_directory,
    plot_error_statistics as plot_linkml_statistics
)
from oep_client import OepClient

# === CONFIGURATION ===========================================================
SRC = Path(__file__).resolve().parents[1]   # .../graphon_ingestion/src
sys.path.insert(0, str(SRC))

from config.neo_config import PASSWORD, URI, USER
from config.oep_config import (
    METADATA_DIR,
    MODELS_DIR,
    OEP_API_BASE,
    RAW_METADATA_DIR,
    RESULT_DIR,
    SCHEMA,
)
from oep_ingestion.shared import get_logger

log = get_logger("neo_ingest_oep")

# === LINKML CONFIGURATION ================================================
LINKML_SCHEMA_NAME = "data-model-oep.yaml"
LINKML_SCHEMA_PATH = MODELS_DIR / LINKML_SCHEMA_NAME

# === Cypher Ingestion Logic ===============================================

def verify_neo4j_connection(neo_driver: Driver):
    """Verify Neo4j connection."""
    try:
        neo_driver.verify_connectivity()        # Test connection
        log.info(f"Successfully connected to Neo4j: {URI}")
    except Exception as e:
        print(f"Failed to connect or verify Neo4j connection. Ensure the database is running and credentials are correct: {e}")
        log.exception(f"Failed to connect to {URI}")
        raise

# =============================================================================
# Clear Neo4j Database
# =============================================================================
def clear_database(driver: Driver):
    """
    Deletes the complete Neo4j graph after user confirmation.
    """

    print("\n========================================")
    print("WARNING: This will DELETE the entire Neo4j database!")
    print("All nodes, relationships and properties will be lost.")
    print("========================================")

    confirmation = input("Do you really want to delete the database? (yes/no): ").strip().lower()

    if confirmation not in ("yes", "y"):
        print("Database deletion cancelled.")
        return False

    with driver.session() as session:
        session.run("""
            MATCH (n)
            DETACH DELETE n
        """)

    print("Database successfully cleared.\n")
    return True

# =============================================================================
# Neo4j Metadata Ingestion
# =============================================================================
def ingest_oep_metadata(driver: Driver, record: dict[str, Any], success_count, failed_count, ingest_errors):
    """
    Transforms OEP metadata into a Neo4j graph based on the LinkML schema.
    """

    cypher_query = """
    CALL {
        WITH $dataset AS dataset
        WITH dataset 
        WHERE dataset.`@id` IS NOT NULL AND trim(toString(dataset.`@id`)) <> ""
        MERGE (d:Dataset {id: dataset.`@id`})
        RETURN d
      UNION
        WITH $dataset AS dataset
        WITH dataset 
        WHERE dataset.`@id` IS NULL OR trim(toString(dataset.`@id`)) = ""
        MERGE (d:Dataset {name: coalesce(dataset.name, "unknown_dataset")})
        RETURN d
    }
    WITH d, $dataset.metaMetadata AS mm
    SET d.id = coalesce($dataset.`@id`, null),
        d.name = $dataset.name,
        d.title = $dataset.title,
        d.description = $dataset.description,
        d.context = $dataset.`@context`,
        d.source = "OEP"

    FOREACH (_ IN CASE WHEN mm IS NOT NULL AND trim(coalesce(toString(mm.metadataVersion), "")) <> "" THEN [1] ELSE [] END |
        MERGE (m:MetaMetadata {version: trim(toString(mm.metadataVersion))})
        ON CREATE SET m.source = "OEP"

        MERGE (d)-[:HAS_METAMETADATA]->(m)

        FOREACH (__ IN CASE WHEN mm.metadataLicense IS NOT NULL AND trim(coalesce(toString(mm.metadataLicense.name), "")) <> "" THEN [1] ELSE [] END |
            MERGE (ml:License {name: trim(toString(mm.metadataLicense.name))})
            ON CREATE SET
                ml.title = mm.metadataLicense.title,
                ml.path = mm.metadataLicense.path, 
                ml.source = "OEP"
            MERGE (m)-[:HAS_METADATA_LICENSE]->(ml)
        )
    )

    // 2. Process resources
    WITH d
    UNWIND coalesce($dataset.resources, []) AS res
    WITH d, res
    WHERE res.path IS NOT NULL AND trim(toString(res.path)) <> ""
    MERGE (r:Resource {path: trim(toString(res.path))})
    SET r.id = coalesce(res.`@id`, "null"),
        r.name = res.name,
        r.topics = res.topics,
        r.title = res.title,
        r.type = res.type,
        r.format = coalesce(res.format, "null"),
        r.encoding = coalesce(res.encoding, "null"),
        r.publicationDate = res.publicationDate,
        r.description = res.description,
        r.review_badge = coalesce(res.review.badge, "null"),
        r.source = "OEP"

    MERGE (d)-[:HAS_RESOURCE]->(r)
    
    // Languages
    FOREACH (lang IN [l IN coalesce(res.languages, []) WHERE l IS NOT NULL AND trim(toString(l)) <> ""] |
        MERGE (l:Language {code: trim(toString(lang))})
        ON CREATE SET l.source = "OEP"
        MERGE (r)-[:HAS_LANGUAGE]->(l)
    )

    // Subject Ontology
    FOREACH (subj IN [s IN coalesce(res.subject, []) WHERE s.`@id` IS NOT NULL AND toString(s.`@id`) <> "null" AND trim(toString(s.`@id`)) <> ""] |
        MERGE (os:Subject {id: trim(toString(subj.`@id`))})
        ON CREATE SET 
            os.name = subj.name,
            os.source = "OEP"
        MERGE (r)-[:MENTIONS_SUBJECT]->(os)
    )

    // Keywords
    FOREACH (kw IN [k IN coalesce(res.keywords, []) WHERE k IS NOT NULL AND k <> "" AND k <> "null" AND trim(toString(k)) <> ""] |
        MERGE (key:Keyword {value: trim(toString(kw))})
        ON CREATE SET key.source = "OEP"
        MERGE (r)-[:HAS_KEYWORD]->(key)
    )

    // Embargo Period
    FOREACH (_ IN CASE
        WHEN res.embargoPeriod IS NOT NULL
            AND trim(coalesce(toString(res.embargoPeriod.start), "")) <> ""
            AND trim(coalesce(toString(res.embargoPeriod.end), "")) <> ""
        THEN [1]
        ELSE []
    END |
        MERGE (ep:EmbargoPeriod {
            start: trim(toString(res.embargoPeriod.start)),
            end: trim(toString(res.embargoPeriod.end))
        })
        ON CREATE SET ep.source = "OEP"
        SET ep.isActive = coalesce(res.embargoPeriod.isActive, false)
        
        MERGE (r)-[:HAS_EMBARGO_PERIOD]->(ep)
    )

    // Context
    FOREACH (_ IN CASE
        WHEN res.context IS NOT NULL
            AND (
                trim(coalesce(toString(res.context.title), "")) <> "" OR
                trim(coalesce(toString(res.context.contact), "")) <> "" OR
                trim(coalesce(toString(res.context.grantNo), "")) <> "" OR
                trim(coalesce(toString(res.context.homepage), "")) <> "" OR
                trim(coalesce(toString(res.context.publisher), "")) <> "" OR
                trim(coalesce(toString(res.context.sourceCode), "")) <> "" OR
                trim(coalesce(toString(res.context.documentation), "")) <> "" OR
                trim(coalesce(toString(res.context.fundingAgency), "")) <> "" OR
                res.context.publisherLogo IS NOT NULL OR
                trim(coalesce(toString(res.context.fundingAgencyLogo), "")) <> ""
            )
        THEN [1]
        ELSE []
    END |
        MERGE (c:Context {
            title: trim(coalesce(toString(res.context.title), "")),
            contact: trim(coalesce(toString(res.context.contact), "")),
            grantNo: trim(coalesce(toString(res.context.grantNo), "")),
            homepage: trim(coalesce(toString(res.context.homepage), "")),
            publisher: trim(coalesce(toString(res.context.publisher), "")),
            sourceCode: trim(coalesce(toString(res.context.sourceCode), "")),
            documentation: trim(coalesce(toString(res.context.documentation), "")),
            fundingAgency: trim(coalesce(toString(res.context.fundingAgency), "")),
            publisherLogo: trim(coalesce(toString(res.context.publisherLogo), "")),
            fundingAgencyLogo: trim(coalesce(toString(res.context.fundingAgencyLogo), ""))
        })
        ON CREATE SET c.source = "OEP"

        MERGE (r)-[:HAS_CONTEXT]->(c)
    )

    // Spatial Extent & Location
    FOREACH (_ IN CASE
        WHEN res.spatial IS NOT NULL
            AND (
                (
                    res.spatial.location IS NOT NULL
                    AND (
                        trim(coalesce(toString(res.spatial.location.address), "")) <> "" OR
                        trim(coalesce(toString(res.spatial.location.latitude), "")) <> "" OR
                        trim(coalesce(toString(res.spatial.location.longitude), "")) <> ""
                    )
                )
                OR
                (
                    res.spatial.extent IS NOT NULL
                    AND (
                        trim(coalesce(toString(res.spatial.extent.name), "")) <> "" OR
                        trim(coalesce(toString(res.spatial.extent.crs), "")) <> "" OR
                        trim(coalesce(toString(res.spatial.extent.resolutionUnit), "")) <> "" OR
                        trim(coalesce(toString(res.spatial.extent.resolutionValue), "")) <> "" OR
                        coalesce(res.spatial.extent.boundingBox, [0,0,0,0]) <> [0,0,0,0]
                    )
                )
            )
        THEN [1]
        ELSE []
    END |
        CREATE (s:Spatial)
        MERGE (r)-[:HAS_SPATIAL]->(s)
        SET s.source = "OEP"

        // Location
        FOREACH (__ IN CASE
            WHEN res.spatial.location IS NOT NULL
                AND res.spatial.location.address IS NOT NULL
                AND trim(toString(res.spatial.location.address)) <> ""
            THEN [1]
            ELSE []
        END |
            MERGE (loc:Location {address: trim(toString(res.spatial.location.address))})
            ON CREATE SET loc.source = "OEP"
            SET
                loc.id = coalesce(res.spatial.location.`@id`, "null"),
                loc.latitude = res.spatial.location.latitude,
                loc.longitude = res.spatial.location.longitude

            MERGE (s)-[:HAS_LOCATION]->(loc)
        )

        // Extent
        FOREACH (__ IN CASE
            WHEN res.spatial.extent IS NOT NULL
                AND res.spatial.extent.name IS NOT NULL
                AND trim(toString(res.spatial.extent.name)) <> ""
            THEN [1]
            ELSE []
        END |
            MERGE (ext:Extent {name: trim(toString(res.spatial.extent.name))})
            ON CREATE SET ext.source = "OEP"
            SET
                ext.id = coalesce(res.spatial.extent.`@id`, "null"),
                ext.crs = res.spatial.extent.crs,
                ext.boundingBox = res.spatial.extent.boundingBox,
                ext.resolutionUnit = res.spatial.extent.resolutionUnit,
                ext.resolutionValue = res.spatial.extent.resolutionValue

            MERGE (s)-[:HAS_EXTENT]->(ext)
        )
    )

    // Temporal
    FOREACH (_ IN CASE WHEN res.temporal IS NOT NULL THEN [1] ELSE [] END |
        CREATE (t:Temporal)
        SET 
            t.referenceDate = res.temporal.referenceDate,
            t.source = "OEP"

        MERGE (r)-[:HAS_TEMPORAL]->(t)

        // Time series
        FOREACH (ts IN coalesce(res.temporal.timeseries, []) |
            MERGE (time:TimeSeries {
                start: coalesce(ts.start, ""),
                end: coalesce(ts.end, ""),
                resolutionValue: coalesce(ts.resolutionValue, -1),
                resolutionUnit: coalesce(ts.resolutionUnit, ""),
                alignment: coalesce(ts.alignment, ""),
                aggregationType: coalesce(ts.aggregationType, "")
            })
            ON CREATE SET time.source = "OEP"
            MERGE (t)-[:HAS_TIMESERIES]->(time)
        )
    )

    // Sources
    FOREACH (src IN coalesce(res.sources, []) |
        MERGE (s:Source {path: coalesce(src.path, "null")})
        ON CREATE SET s.source = "OEP"

        SET
            s.title = src.title,
            s.description = src.description,
            s.publicationYear = src.publicationYear

        MERGE (r)-[:HAS_SOURCE]->(s)

        // Authors
        FOREACH (author IN [a IN coalesce(src.authors, []) WHERE a IS NOT NULL AND trim(toString(a)) <> ""] |
            MERGE (a:Author {name: trim(toString(author))})
            ON CREATE SET a.source = "OEP"

            MERGE (s)-[:HAS_AUTHOR]->(a)
        )

        // Source Licenses
        FOREACH (
            lic IN [
                l IN coalesce(src.sourceLicenses, [])
                WHERE
                    trim(coalesce(toString(l.name), "")) <> "" OR
                    trim(coalesce(toString(l.path), "")) <> "" OR
                    trim(coalesce(toString(l.title), "")) <> "" OR
                    trim(coalesce(toString(l.instruction), "")) <> "" OR
                    trim(coalesce(toString(l.attribution), "")) <> "" OR
                    trim(coalesce(toString(l.copyrightStatement), "")) <> ""
            ] |
            MERGE (sl:License {
                name: trim(coalesce(toString(lic.name), "")),
                title: trim(coalesce(toString(lic.title), "")),
                path: trim(coalesce(toString(lic.path), "")),
                instruction: trim(coalesce(toString(lic.instruction), "")),
                attribution: trim(coalesce(toString(lic.attribution), "")),
                copyrightStatement: trim(coalesce(toString(lic.copyrightStatement), ""))
            })
            ON CREATE SET sl.source = "OEP"

            MERGE (s)-[:HAS_SOURCE_LICENSE]->(sl)
        )
    )

    // Resource Licenses
    FOREACH (
        lic IN [
            l IN coalesce(res.licenses, [])
            WHERE
                trim(coalesce(toString(l.name), "")) <> "" OR
                trim(coalesce(toString(l.path), "")) <> "" OR
                trim(coalesce(toString(l.title), "")) <> "" OR
                trim(coalesce(toString(l.instruction), "")) <> "" OR
                trim(coalesce(toString(l.attribution), "")) <> "" OR
                trim(coalesce(toString(l.copyrightStatement), "")) <> ""
        ] |
        MERGE (rl:License {
            name: trim(coalesce(toString(lic.name), "")),
            title: trim(coalesce(toString(lic.title), "")),
            path: trim(coalesce(toString(lic.path), "")),
            instruction: trim(coalesce(toString(lic.instruction), "")),
            attribution: trim(coalesce(toString(lic.attribution), "")),
            copyrightStatement: trim(coalesce(toString(lic.copyrightStatement), ""))
        })
        ON CREATE SET rl.source = "OEP"

        MERGE (r)-[:HAS_LICENSE]->(rl)
    )

    // Resource Provenance - Contributors & Roles
    FOREACH (
        con IN [
            c IN coalesce(res.contributors, [])
            WHERE 
                trim(coalesce(toString(c.title), "")) <> "" OR
                trim(coalesce(toString(c.object), "")) <> "" OR
                trim(coalesce(toString(c.organization), "")) <> "" OR
                trim(coalesce(toString(c.date), "")) <> "" OR
                trim(coalesce(toString(c.path), "")) <> "" OR
                trim(coalesce(toString(c.comment), "")) <> ""
        ] |
        MERGE (p:Contributor {
            title: trim(coalesce(toString(con.title), "")),
            object: trim(coalesce(toString(con.object), "")),
            organization: trim(coalesce(toString(con.organization), "")),
            date: coalesce(con.date, ""),
            path: trim(coalesce(toString(con.path), "")),
            comment: trim(coalesce(toString(con.comment), ""))
        })
        ON CREATE SET p.source = "OEP"

        MERGE (r)-[:CONTRIBUTED_BY]->(p)

        FOREACH (
            roleName IN [
                rn IN (coalesce(con.roles, []) + coalesce(con.role, []))
                WHERE trim(coalesce(toString(rn), "")) <> ""
            ] |
            MERGE (role:Role {
                name: trim(toString(roleName))
            })
            ON CREATE SET role.source = "OEP"

            MERGE (p)-[:HAS_ROLE]->(role)
        )
    )

    // Resource Schema & Fields
    FOREACH (_ IN CASE
        WHEN res.schema IS NOT NULL
            AND (
                size(coalesce(res.schema.fields, [])) > 0 OR
                size(coalesce(res.schema.primaryKey, [])) > 0 OR
                size(coalesce(res.schema.foreignKeys, [])) > 0
            )
        THEN [1]
        ELSE []
    END |
        CREATE (schema:Schema)
        SET schema.source = "OEP"

        MERGE (r)-[:HAS_SCHEMA]->(schema)

        // Fields
        FOREACH (
            field IN [
                f IN coalesce(res.schema.fields, [])
                WHERE
                    trim(coalesce(toString(f.name), "")) <> "" OR
                    trim(coalesce(toString(f.type), "")) <> "" OR
                    trim(coalesce(toString(f.unit), "")) <> "" OR
                    trim(coalesce(toString(f.description), "")) <> "" OR
                    f.nullable IS NOT NULL
            ] |
            MERGE (fi:Field {
                name: trim(coalesce(toString(field.name), ""))
            })
            ON CREATE SET 
                fi.type = trim(coalesce(toString(field.type), "")),
                fi.unit = trim(coalesce(toString(field.unit), "")),
                fi.description = trim(coalesce(toString(field.description), "")),
                fi.nullable = coalesce(field.nullable, false),
                fi.source = "OEP"

            MERGE (schema)-[:HAS_FIELD]->(fi)

            // isAbout -> OntologyReference
            FOREACH (
                about IN [
                    a IN coalesce(field.isAbout, [])
                    WHERE 
                        trim(coalesce(toString(a.`@id`), "")) <> "" OR
                        trim(coalesce(toString(a.name), "")) <> ""
                ] |
                MERGE (ont:isAbout {
                    id: coalesce(nullif(trim(coalesce(toString(about.`@id`), "")), ""), trim(coalesce(toString(about.name), "")), "unknown_ontology")
                })
                ON CREATE SET 
                    ont.name = trim(coalesce(toString(about.name), "")),
                    ont.source = "OEP"

                MERGE (fi)-[:IS_ABOUT]->(ont)
            )

            // valueReference
            FOREACH (
                ref IN [
                    v IN coalesce(field.valueReference, [])
                    WHERE 
                        trim(coalesce(toString(v.`@id`), "")) <> "" OR
                        trim(coalesce(toString(v.name), "")) <> "" OR
                        trim(coalesce(toString(v.value), "")) <> ""
                ] |
                MERGE (vr:ValueReference {
                    id: coalesce(nullif(trim(coalesce(toString(ref.`@id`), "")), ""), trim(coalesce(toString(ref.name), "")), "unknown_val_ref")
                })
                ON CREATE SET 
                    vr.name = trim(coalesce(toString(ref.name), "")),
                    vr.value = trim(coalesce(toString(ref.value), "")),
                    vr.source = "OEP"

                MERGE (fi)-[:HAS_VALUE_REFERENCE]->(vr)
            )
        )

        // Primary Keys
        FOREACH (
            pk IN [
                p IN coalesce(res.schema.primaryKey, [])
                WHERE trim(coalesce(toString(p), "")) <> ""
            ] |
            MERGE (primaryKey:PrimaryKey {
                field: trim(toString(pk))
            })
            ON CREATE SET primaryKey.source = "OEP"

            MERGE (schema)-[:HAS_PRIMARY_KEY]->(primaryKey)
        )

        // Foreign Keys
        FOREACH (
            fk IN [
                f IN coalesce(res.schema.foreignKeys, [])
                WHERE
                    size(coalesce(f.fields, [])) > 0 OR
                    size(coalesce(f.reference.fields, [])) > 0 OR
                    trim(coalesce(toString(f.reference.resource), "")) <> ""
            ] |
            CREATE (foreignKey:ForeignKey {
                fields: coalesce(fk.fields, [])
            })
            SET foreignKey.source = "OEP"

            MERGE (schema)-[:HAS_FOREIGN_KEY]->(foreignKey)

            FOREACH (_ IN CASE
                WHEN
                    size(coalesce(fk.reference.fields, [])) > 0 OR
                    trim(coalesce(toString(fk.reference.resource), "")) <> ""
                THEN [1]
                ELSE []
            END |
                MERGE (ref:Reference {
                    resource: coalesce(nullif(trim(coalesce(toString(fk.reference.resource), "")), ""), "unknown_ref_resource")
                })
                ON CREATE SET 
                    ref.fields = coalesce(fk.reference.fields, []),
                    ref.source = "OEP"

                MERGE (foreignKey)-[:REFERENCES]->(ref)
            )
        )
    )

    // Dialect
    FOREACH (_ IN CASE
        WHEN res.dialect IS NOT NULL
            AND (
                trim(coalesce(toString(res.dialect.delimiter), "")) <> "" OR
                trim(coalesce(toString(res.dialect.decimalSeparator), "")) <> ""
            )
        THEN [1]
        ELSE []
    END |
        MERGE (di:Dialect {
            delimiter: trim(coalesce(toString(res.dialect.delimiter), "")),
            decimalSeparator: trim(coalesce(toString(res.dialect.decimalSeparator), ""))
        })
        ON CREATE SET di.source = "OEP"

        MERGE (r)-[:HAS_DIALECT]->(di)
    )

    // Review
    FOREACH (
        rev IN CASE
            WHEN res.review IS NOT NULL
                AND (
                    trim(coalesce(toString(res.review.path), "")) <> "" OR
                    trim(coalesce(toString(res.review.badge), "")) <> ""
                )
            THEN [res.review]
            ELSE []
        END |
        MERGE (review:Review {
            path: coalesce(nullif(trim(coalesce(toString(rev.path), "")), ""), "unknown_review_path")
        })
        ON CREATE SET 
            review.badge = trim(coalesce(toString(rev.badge), "")),
            review.source = "OEP"

        MERGE (r)-[:HAS_REVIEW]->(review)
    )
    """

    with driver.session() as session:
        dataset_name = record.get("name", "<unknown>")

        log.info(f"Processing Dataset: {dataset_name}...")

        try:
            session.execute_write(lambda tx: tx.run(cypher_query, dataset=record))
            success_count += 1
            log.info(f"-> Success: Dataset '{dataset_name}...' ingested.")
        except Exception as e:
            failed_count += 1
            error_type = categorize_neo4j_error(e)
            ingest_errors[error_type] += 1

            log.exception(f"-> FAILED ingestion for {dataset_name}: {e}")

    return success_count, failed_count, ingest_errors


# === 2.1. Error Detection -> Pareto Logic ===============================================

# =============================================================================
# Neo4j Error Categorization
# =============================================================================
def categorize_neo4j_error(exception: Exception) -> str:
    """
    Categorizes Neo4j/Cypher ingestion errors.
    """

    message = str(exception)

    pattern = (
        r"Cannot merge the following node because of null property value for "
        r"'([^']+)':\s*\(:([A-Za-z0-9_]+)"
    )

    match = re.search(pattern, message)

    if match:
        property_name = match.group(1)
        label = match.group(2)

        return f"{label}.{property_name} = null"

    # Other common Neo4j errors
    if "Type mismatch" in message:
        return "Type mismatch"

    if "Invalid input" in message:
        return "Cypher syntax"

    if "ConstraintValidationFailed" in message:
        return "Constraint violation"

    if "Variable" in message and "not defined" in message:
        return "Undefined variable"

    return "Other Neo4j Error"

# =============================================================================
# Plot Neo4j ingestion errors
# =============================================================================
def plot_error_statistics(
        error_counter: Counter,
        title: str = "Error Statistics",
        filename: str = "error_statistics.png",
        show: bool = False,
        color="steelblue",
        reason_prefix: str = "N"
        ):
    """
    Creates a sorted bar chart of error types and saves it as an image file.
    """

    if not error_counter:
        print("No errors present - no graphic generated.")
        return {}

    sorted_items = sorted(
        error_counter.items(),
        key=lambda x: x[1],
        reverse=True
    )

    error_types, values = zip(*sorted_items)

    reason_mapping = {
        f"{reason_prefix}{i}": error_type
        for i, (error_type, _) in enumerate(
            sorted_items,
            start=1
        )
    }

    reason_codes = list(reason_mapping.keys())

    plt.figure(figsize=(10, 6))

    plt.bar(
        reason_codes,
        values,
        color=color
    )

    plt.xlabel("Reason")
    plt.ylabel("Count")
    plt.title(title)

    for i, value in enumerate(values):
        plt.text(
            i,
            value,
            str(value),
            ha="center",
            va="bottom",
            fontsize=8
        )

    plt.tight_layout()

    plt.savefig(
        filename,
        dpi=600,
        bbox_inches="tight"
    )

    print(f"Error statistics saved as: {filename}")

    if show:
        plt.show()

    plt.close()

    return reason_mapping

def save_reason_mapping(
    reason_mapping: dict[str, str],
    filename: str,
    title: str = "Neo4j Ingestion Error Reason Mapping"
):
    """
    Saves the reason-code mapping to a text file.
    """

    with open(filename, "w", encoding="utf-8") as f:

        f.write(title + "\n")
        f.write("=" * 60 + "\n\n")

        for reason_code, error_type in reason_mapping.items():
            f.write(f"{reason_code} = {error_type}\n")

    print(f"Reason mapping saved as: {filename}")


def get_all_table_names_from_oep():
    log.info("Get all table names")
    list_url = f"{OEP_API_BASE}/advanced/get_table_names"
    response = requests.post(list_url, json={"schema": SCHEMA})

    if response.status_code != 200:
        print(f"Failed to fetch table list: {response.text}")
        return

    data = response.json()

    if isinstance(data, dict):
        tables = data.get("content", list(data.keys()))
    else:
        tables = data

    log.info(f"Table names count: {len(tables)}")
    return tables

# =============================================================================
# Load metadata from existing files
# =============================================================================
def load_existing_metadata():
    """
    Loads all existing OEP metadata from the local metadata folder.
    """

    table_names = get_all_table_names_from_oep()
    records_to_ingest = []

    for table_name in table_names:
        print(f"Loading local metadata: {table_name}")

        filename = f"{table_name}_metadata.json"
        filepath = RAW_METADATA_DIR / filename

        if not filepath.exists():
            print(f"  -> File not found: {filepath}")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                json_content = f.read()
                raw_data: list[dict[str, Any]] = json.loads(json_content)
            records_to_ingest.append(raw_data)

        except Exception as e:
            print(f"  -> Error reading {filename}: {e}")

    return records_to_ingest

# === 3. Main Execution =======================================================

if __name__ == "__main__":
    log.info("Main started")

    cli = OepClient()
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    verify_neo4j_connection(driver)

    if not clear_database(driver):
        log.info("Import aborted.")
        driver.close()
        exit()

    print("\n========================================")
    print("OEP Metadata Import/Ingestion")
    print("========================================")
    print("1 - Download/Ingest metadata from OEP & store them")
    print("2 - Use existing local metadata files (from previous Downloads)")
    print("3 - Use existing local metadata files (from previous Downloads) and compare them to the actual OEP Metadata")
    print("4 - Download/Ingest metadata from OEP without local store")
    print("========================================")

    choice = input("Select option (1/2/3/4): ").strip()

    if choice == "1":
        print("\nDownloading metadata from OEP...")

    elif choice == "2":
        print("\nUsing existing local metadata from directory...")
        print("\nStarting LinkML validation...")

        records_to_ingest = []
        for json_file in METADATA_DIR.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    records_to_ingest.append(json.load(f))
            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")

        if not records_to_ingest:
            print("No valid datasets available. Import aborted.")
            exit()

        print(f"{len(records_to_ingest)} datasets passed LinkML validation.")

        success_count = 0
        failed_count = 0
        ingest_errors = Counter()
        for record in records_to_ingest:
            success_count, failed_count, ingest_errors = ingest_oep_metadata(driver, record, success_count, failed_count, ingest_errors)

        print("\n==============================")
        print(f"Successfully ingested: {success_count}")
        print(f"Failed ingestions:     {failed_count}")
        print(f"Total datasets:        {len(records_to_ingest)}")
        print("==============================\n")

    elif choice == "3":
        print("\nUsing existing local metadata comparing to actual OEP Metadata ...")
        records_to_ingest = load_existing_metadata()

    elif choice == "4":
        table_names = get_all_table_names_from_oep()
        tables_downloaded = 0
        log.info(f"Table names count: {len(table_names)}")

        for table_name in table_names:
            try:
                log.info(f"Downloading Metadata for table: {table_name}, "
                            f"{int(tables_downloaded/len(table_names)*100)}%")
                metadata_rec = cli.get_metadata(table_name)
                tables_downloaded += 1
                try:
                    ingest_oep_metadata(driver, metadata_rec, 0, 0, Counter())
                except Exception as e:
                    log.exception("An error occurred during ingesting: %s", e)

            except Exception as e:
                log.exception("An error occurred during downloading: %s", e)

        log.info(f"Ingestion Metadata finished {tables_downloaded}")

    else:
        print("Invalid selection.")
        exit()

    # Save LinkML report
    save_linkml_report(filename=RESULT_DIR / "linkml_validation_report.json")

    plot_linkml_statistics(
        LINKML_ERROR_COUNTER,
        title="LinkML Validation Errors",
        filename=RESULT_DIR / "linkml_validation_errors.png"
    )

    # Save Neo4j ingestion errors
    neo4j_reason_mapping = plot_error_statistics(
        ingest_errors,
        title="Neo4j Ingest Error Statistics",
        filename=RESULT_DIR / "neo4j_ingest_errors.png",
        color="forestgreen",
        reason_prefix="N"
    )

    save_reason_mapping(
        neo4j_reason_mapping,
        filename=RESULT_DIR / "neo4j_ingest_reason_mapping.txt",
        title="Neo4j Ingestion Error Reason Mapping"
    )

    # Combined statistics
    all_errors = (
        Counter()
        + LINKML_ERROR_COUNTER
        + ingest_errors
    )

    plot_error_statistics(
        all_errors, 
        title="Total Error Statistics (Load + Ingest)", 
        filename=RESULT_DIR / "neo4j_load_ingest_errors.png"
    )

    if 'driver' in locals():
        driver.close()