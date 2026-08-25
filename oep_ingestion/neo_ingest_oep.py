import json
import re
from collections import Counter
from sys import exit
from typing import Any

import matplotlib.pyplot as plt
import requests
from neo4j import Driver, GraphDatabase
from oep_analysis.oep_validation.linkml_validation_script import (
    LINKML_ERROR_COUNTER,
    save_linkml_report,
    validate_directory,
)
from oep_client import OepClient

# === CONFIGURATION ===========================================================
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
    /
    Imports a validated OEP metadata JSON file into Neo4j.

    LinkML validation is executed before this function.
    Therefore, only valid datasets are processed here.
    """

    cypher_query = """
    CALL {
        WITH $dataset AS dataset
        WITH dataset 
        WHERE dataset.`@id` IS NOT NULL AND trim(dataset.`@id`) <> ""
        MERGE (d:Dataset {id: dataset.`@id`})
        RETURN d
      UNION
        WITH $dataset AS dataset
        WITH dataset 
        WHERE dataset.`@id` IS NULL OR trim(dataset.`@id`) = ""
        MERGE (d:Dataset {name: dataset.name})
        RETURN d
    }
    WITH d, $dataset.metaMetadata AS mm
    SET d.id = coalesce($dataset.`@id`, null),
        d.name = $dataset.name,
        d.title = $dataset.title,
        d.description = $dataset.description,
        d.context = $dataset.`@context`,
        d.source = "OEP"

    FOREACH (_ IN CASE WHEN mm IS NOT NULL THEN [1] ELSE [] END |
        MERGE (m:MetaMetadata {version: mm.metadataVersion})
        ON CREATE SET m.source = "OEP"

        MERGE (d)-[:HAS_METAMETADATA]->(m)

        MERGE (ml:License {name: mm.metadataLicense.name})
        ON CREATE SET
            ml.title = mm.metadataLicense.title,
            ml.path = mm.metadataLicense.path, 
            ml.source = "OEP"
        MERGE (m)-[:HAS_METADATA_LICENSE]->(ml)
    )

    // 2. Process resources
    WITH d
    UNWIND $dataset.resources AS res
    MERGE (r:Resource {path: res.path})
    SET r.id = coalesce(res.`@id`, "null"),
        r.name = res.name,
        r.topics = res.topics,
        r.title = res.title,
        r.type = res.type,
        r.format = coalesce(res.format, "null"),
        r.encoding = coalesce(res.encoding, "null"),
        r.publicationDate = res.publicationDate,
        r.description = res.description,
        r.review_badge = res.review.badge,
        r.source = "OEP"

    MERGE (d)-[:HAS_RESOURCE]->(r)
    
    // Languages
    FOREACH (lang IN coalesce(res.languages, []) |
        MERGE (l:Language {code: lang})
        ON CREATE SET l.source = "OEP"
        MERGE (r)-[:HAS_LANGUAGE]->(l)
    )

    // Subject Ontology
    FOREACH (subj IN [s IN coalesce(res.subject, []) WHERE s.`@id` IS NOT NULL AND s.`@id` <> "null"] |
        MERGE (os:Subject {id: subj.`@id`})  //Subject =^ OntologyReference
        ON CREATE SET 
            os.name = subj.name,
            os.source = "OEP"
        MERGE (r)-[:MENTIONS_SUBJECT]->(os)
    )

    // Keywords
    FOREACH (kw IN [k IN coalesce(res.keywords, []) WHERE k <> "" AND k <> "null" AND k IS NOT NULL] |
        MERGE (key:Keyword {value: kw})
        ON CREATE SET key.source = "OEP"
        MERGE (r)-[:HAS_KEYWORD]->(key)
    )

    // Embargo Period
    FOREACH (_ IN CASE
        WHEN res.embargoPeriod IS NOT NULL
            AND trim(coalesce(res.embargoPeriod.start, "")) <> ""
            AND trim(coalesce(res.embargoPeriod.end, "")) <> ""
        THEN [1]
        ELSE []
    END |

        MERGE (ep:EmbargoPeriod {
            start: res.embargoPeriod.start,
            end: res.embargoPeriod.end
        })
        ON CREATE SET ep.source = "OEP"

        SET ep.isActive = coalesce(res.embargoPeriod.isActive, false)
        
        MERGE (r)-[:HAS_EMBARGO_PERIOD]->(ep)
    )

    // Context
    FOREACH (_ IN CASE
        WHEN res.context IS NOT NULL
            AND (
                trim(coalesce(res.context.title, "")) <> "" OR
                trim(coalesce(res.context.contact, "")) <> "" OR
                trim(coalesce(res.context.grantNo, "")) <> "" OR
                trim(coalesce(res.context.homepage, "")) <> "" OR
                trim(coalesce(res.context.publisher, "")) <> "" OR
                trim(coalesce(res.context.sourceCode, "")) <> "" OR
                trim(coalesce(res.context.documentation, "")) <> "" OR
                trim(coalesce(res.context.fundingAgency, "")) <> "" OR
                res.context.publisherLogo IS NOT NULL OR
                trim(coalesce(res.context.fundingAgencyLogo, "")) <> ""
            )
        THEN [1]
        ELSE []
    END |

        MERGE (c:Context {
            title: trim(coalesce(res.context.title, "")),
            contact: trim(coalesce(res.context.contact, "")),
            grantNo: trim(coalesce(res.context.grantNo, "")),
            homepage: trim(coalesce(res.context.homepage, "")),
            publisher: trim(coalesce(res.context.publisher, "")),
            sourceCode: trim(coalesce(res.context.sourceCode, "")),
            documentation: trim(coalesce(res.context.documentation, "")),
            fundingAgency: trim(coalesce(res.context.fundingAgency, "")),
            publisherLogo: trim(coalesce(res.context.publisherLogo, "")),
            fundingAgencyLogo: trim(coalesce(res.context.fundingAgencyLogo, ""))
        })
        ON CREATE SET c.source = "OEP"

        MERGE (r)-[:HAS_CONTEXT]->(c)
    )

    // Spatial Extent & Location
    // Spatial
    FOREACH (_ IN CASE
        WHEN res.spatial IS NOT NULL
            AND (
                (
                    res.spatial.location IS NOT NULL
                    AND (
                        trim(coalesce(res.spatial.location.address, "")) <> "" OR
                        trim(coalesce(res.spatial.location.latitude, "")) <> "" OR
                        trim(coalesce(res.spatial.location.longitude, "")) <> ""
                    )
                )
                OR
                (
                    res.spatial.extent IS NOT NULL
                    AND (
                        trim(coalesce(res.spatial.extent.name, "")) <> "" OR
                        trim(coalesce(res.spatial.extent.crs, "")) <> "" OR
                        trim(coalesce(res.spatial.extent.resolutionUnit, "")) <> "" OR
                        trim(coalesce(res.spatial.extent.resolutionValue, "")) <> "" OR
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
        // Optional: Use MERGE (r)-[:HAS_SPATIAL]->(s:Spatial) instead of CREATE and MERGE if you want to ensure only one Spatial per Resource exists

        // Location
        FOREACH (__ IN CASE
            WHEN res.spatial.location IS NOT NULL
                AND res.spatial.location.address IS NOT NULL
                AND trim(res.spatial.location.address) <> ""
            THEN [1]
            ELSE []
        END |

            MERGE (loc:Location {address: res.spatial.location.address})
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
                AND trim(res.spatial.extent.name) <> ""
            THEN [1]
            ELSE []
        END |

            MERGE (ext:Extent {name: res.spatial.extent.name})
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
        FOREACH (author IN coalesce(src.authors, []) |

            MERGE (a:Author {name: author})
            ON CREATE SET a.source = "OEP"

            MERGE (s)-[:HAS_AUTHOR]->(a)
        )

        // Source Licenses
        FOREACH (
            lic IN [
                l IN coalesce(src.sourceLicenses, [])
                WHERE
                    trim(coalesce(l.name, "")) <> "" OR
                    trim(coalesce(l.path, "")) <> "" OR
                    trim(coalesce(l.title, "")) <> "" OR
                    trim(coalesce(l.instruction, "")) <> "" OR
                    trim(coalesce(l.attribution, "")) <> "" OR
                    trim(coalesce(l.copyrightStatement, "")) <> ""
            ] |

            MERGE (sl:License {
                name: trim(coalesce(lic.name, "")),
                title: trim(coalesce(lic.title, "")),
                path: trim(coalesce(lic.path, "")),
                instruction: trim(coalesce(lic.instruction, "")),
                attribution: trim(coalesce(lic.attribution, "")),
                copyrightStatement: trim(coalesce(lic.copyrightStatement, ""))
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
                trim(coalesce(l.name, "")) <> "" OR
                trim(coalesce(l.path, "")) <> "" OR
                trim(coalesce(l.title, "")) <> "" OR
                trim(coalesce(l.instruction, "")) <> "" OR
                trim(coalesce(l.attribution, "")) <> "" OR
                trim(coalesce(l.copyrightStatement, "")) <> ""
        ] |

        MERGE (rl:License {
            name: trim(coalesce(lic.name, "")),
            title: trim(coalesce(lic.title, "")),
            path: trim(coalesce(lic.path, "")),
            instruction: trim(coalesce(lic.instruction, "")),
            attribution: trim(coalesce(lic.attribution, "")),
            copyrightStatement: trim(coalesce(lic.copyrightStatement, ""))
        })
        ON CREATE SET rl.source = "OEP"

        MERGE (r)-[:HAS_LICENSE]->(rl)
    )

    // Resource Provenance - Contributors & Roles
    FOREACH (
        con IN [
            c IN coalesce(res.contributors, [])
            WHERE 
                trim(coalesce(c.title, "")) <> "" OR
                trim(coalesce(c.object, "")) <> "" OR
                trim(coalesce(c.organization, "")) <> "" OR
                trim(coalesce(c.date, "")) <> "" OR
                trim(coalesce(c.path, "")) <> "" OR
                trim(coalesce(c.comment, "")) <> ""
        ] |

        MERGE (p:Contributor {
            title: trim(coalesce(con.title, "")),
            object: trim(coalesce(con.object, "")),
            organization: trim(coalesce(con.organization, "")),
            date: coalesce(con.date, ""),
            path: trim(coalesce(con.path, "")),
            comment: trim(coalesce(con.comment, ""))
        })
        ON CREATE SET p.source = "OEP"

        MERGE (r)-[:CONTRIBUTED_BY]->(p)

        FOREACH (
            roleName IN [
                rn IN (coalesce(con.roles, []) + coalesce(con.role, []))
                WHERE trim(coalesce(rn, "")) <> ""
            ] |

            MERGE (role:Role {
                name: trim(roleName)
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

        //SET
        //    schema.primaryKeyCount = size(coalesce(res.schema.primaryKey, [])),
        //    schema.foreignKeyCount = size(coalesce(res.schema.foreignKeys, []))

        // Fields
        FOREACH (
            field IN [
                f IN coalesce(res.schema.fields, [])
                WHERE
                    trim(f.name) <> "" OR
                    trim(f.type) <> "" OR
                    trim(coalesce(f.unit, "")) <> "" OR
                    trim(coalesce(f.description, "")) <> "" OR
                    f.nullable IS NOT NULL
            ] |

            MERGE (fi:Field {
                name: trim(coalesce(field.name, "")),
                type: trim(coalesce(field.type, "")),
                unit: trim(coalesce(field.unit, "")),
                description: trim(coalesce(field.description, "")),
                nullable: coalesce(field.nullable, false)
            })
            ON CREATE SET fi.source = "OEP"

            MERGE (schema)-[:HAS_FIELD]->(fi)

            // isAbout -> OntologyReference
            FOREACH (
                about IN [
                    a IN coalesce(field.isAbout, [])
                    WHERE 
                        trim(coalesce(a.`@id`, "")) <> "" OR
                        trim(coalesce(a.name, "")) <> ""
                ] |

                MERGE (ont:isAbout {
                    id: trim(coalesce(about.`@id`, "")),
                    name: trim(coalesce(about.name, "")) 
                })
                ON CREATE SET ont.source = "OEP"

                MERGE (fi)-[:IS_ABOUT]->(ont)
            )

            // valueReference
            FOREACH (
                ref IN [
                    v IN coalesce(field.valueReference, [])
                    WHERE 
                        trim(coalesce(v.`@id`, "")) <> "" OR
                        trim(coalesce(v.name, "")) <> "" OR
                        trim(coalesce(v.value, "")) <> ""
                ] |

                MERGE (vr:ValueReference {
                    id: trim(coalesce(ref.`@id`, "")),
                    name: trim(coalesce(ref.name, "")),
                    value: trim(coalesce(ref.value, ""))
                })
                ON CREATE SET vr.source = "OEP"

                MERGE (fi)-[:HAS_VALUE_REFERENCE]->(vr)
            )
        )

        // Primary Keys
        FOREACH (
            pk IN [
                p IN coalesce(res.schema.primaryKey, [])
                WHERE 
                    trim(coalesce(p, "")) <> ""
            ] |

            MERGE (primaryKey:PrimaryKey {
                field: trim(pk)
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
                    trim(coalesce(f.reference.resource, "")) <> ""
            ] |

            CREATE (foreignKey:ForeignKey {
                fields: coalesce(fk.fields, [])
            })
            SET foreignKey.source = "OEP"

            MERGE (schema)-[:HAS_FOREIGN_KEY]->(foreignKey)

            FOREACH (_ IN CASE
                WHEN
                    size(coalesce(fk.reference.fields, [])) > 0 OR
                    trim(coalesce(fk.reference.resource, "")) <> ""
                THEN [1]
                ELSE []
            END |

                MERGE (ref:Reference {
                    fields: coalesce(fk.reference.fields, []),
                    resource: trim(coalesce(fk.reference.resource, ""))
                })
                ON CREATE SET ref.source = "OEP"

                MERGE (foreignKey)-[:REFERENCES]->(ref)
            )
        )
    )

    // Dialect
    FOREACH (_ IN CASE
        WHEN res.dialect IS NOT NULL
            AND (
                trim(coalesce(res.dialect.delimiter, "")) <> "" OR
                trim(coalesce(res.dialect.decimalSeparator, "")) <> ""
            )
        THEN [1]
        ELSE []
    END |

        MERGE (di:Dialect {
            delimiter: trim(coalesce(res.dialect.delimiter, "")),
            decimalSeparator: trim(coalesce(res.dialect.decimalSeparator, ""))
        })
        ON CREATE SET di.source = "OEP"

        MERGE (r)-[:HAS_DIALECT]->(di)
    )

    // Review
    FOREACH (
        rev IN CASE
            WHEN res.review IS NOT NULL
                AND (
                    trim(coalesce(res.review.path, "")) <> "" OR
                    trim(coalesce(res.review.badge, "")) <> ""
                )
            THEN [res.review]
            ELSE []
        END |

        MERGE (review:Review {
            path: trim(coalesce(rev.path, "")),
            badge: trim(coalesce(rev.badge, ""))
        })
        ON CREATE SET review.source = "OEP"

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
        color = "steelblue"
        ):
    """
    Creates a sorted bar chart of error types and saves it as an image file.
    
    x-axis: Error type/class
    y-axis: Count
    """

    if not error_counter:
        print("No errors present - no graphic generated.")
        return

    # Prepare data: sort by frequency (descending)
    sorted_items = sorted(error_counter.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_items)

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color=color)  # darkorange

    plt.xlabel("Error type/class")
    plt.ylabel("Count")
    plt.title(title)
    plt.xticks(rotation=45, ha="right", fontsize=3)

    # Write values above bars
    for i, value in enumerate(values):
        plt.text(i, value, str(value), ha="center", va="bottom", fontsize=3)

    plt.tight_layout()

    # Save
    plt.savefig(filename, dpi=600, bbox_inches="tight")
    print(f"Error statistics saved as: {filename}")

    plt.close()


def get_all_table_names_from_oep():
    # 1. Create list of all table names
    log.info("Get all table names")
    # Note: Using the 'advanced' search/info endpoint is often the most reliable way to list tables
    list_url = f"{OEP_API_BASE}/advanced/get_table_names"
    response = requests.post(list_url, json={"schema": SCHEMA})

    if response.status_code != 200:
        print(f"Failed to fetch table list: {response.text}")
        return

    data = response.json()

    # If data is a list, use it directly.
    # If data is a dict, extract the values:
    if isinstance(data, dict):
        # Replace "tables" with the actual key from your API
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

    # 1. Get all table names from OEP
    table_names = get_all_table_names_from_oep()

    records_to_ingest = []

    # 2. Retrieve corresponding metadata records using all table names
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
                raw_data: list[dict[str, Any]] = json.loads(json_content)     # Converts e.g. "@id": null to "@id": None -> converts everything to Python syntax so Python can work with it (since null would cause errors, as it's called none in Python, not null)
                #raw_data = json.load(f)  # Use this if the two lines above no longer work

            records_to_ingest.append(raw_data)

        except Exception as e:
            print(f"  -> Error reading {filename}: {e}")

    return records_to_ingest

# === 3. Main Execution =======================================================

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    log.info("Main started")

    # -------------------------------------------------------------------------
    # 1. Connect Neo4j
    # -------------------------------------------------------------------------
    cli = OepClient()                                           # Initialize Open Energy Platform Client
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))   # Initialize driver connection to Neo4j
    verify_neo4j_connection(driver)

    # ---------------------------------------------------------------------
    # 2. Clear database
    # ---------------------------------------------------------------------
    # Delete existing database
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
        # 1. Download all metadata via get_meta.py to local machine
        # 2. Validate all files via LinkML validation
        # 3. Ingest all valid files


    elif choice == "2":
        print("\nUsing existing local metadata from directory...")
        print("\nStarting LinkML validation...")

        # 1. Validate existing data via LinkML validation
        # 2. Ingest all valid files

        # -------------------------------------------------------------------------
        # 1. LinkML validation
        # -------------------------------------------------------------------------
        # validates all datasets in a folder
        records_to_ingest = []
        for json_file in METADATA_DIR.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    records_to_ingest.append(json.load(f))
            except Exception as e:
                print(f"Error loading {json_file.name}: {e}")

        #print("DEBUG LinkML counter:", LINKML_ERROR_COUNTER)

        if not records_to_ingest:
            print("No valid datasets available. Import aborted.")
            exit()

        print(f"{len(records_to_ingest)} datasets passed LinkML validation.")

        # ---------------------------------------------------------------------
        # 2. Ingest validated metadata
        # ---------------------------------------------------------------------
        # Start ingestion
        success_count=0
        failed_count = 0
        ingest_errors = Counter()
        for record in records_to_ingest:
            success_count, failed_count, ingest_errors = ingest_oep_metadata(driver, record, success_count, failed_count, ingest_errors)

        print("\n==============================")
        print("Valid datasets: WIP")
        print("Failed datasets: WIP")
        print("\n")
        print(f"Successfully ingested: {success_count}")
        print(f"Failed ingestions:     {failed_count}")
        print(f"Total datasets:        {len(records_to_ingest)}")
        print("==============================\n")

    elif choice == "3":
        print("\nUsing existing local metadata comparing to actual OEP Metadata ...")

        # Compare existing data with current OEP data
        # Or ingest via list of names
        records_to_ingest = load_existing_metadata()

    elif choice == "4":
        # Download metadata and validate directly, then
        # ingest into Neo4j DB as KG without storing locally

        # 1. Get list of table names from OEP (to know what data is on OEP)
        # 2. Validate this data
        # 3. Ingest data
        # Best to do this sequentially for each dataset (Download -> Validate -> Ingest)
        pass
        # Start ingestion
        table_names = get_all_table_names_from_oep()  # 1.
        tables_downloaded = 0
        log.info(f"Table names count: {len(table_names)}")

        for table_name in table_names:
            try:
                log.info(f"Downloading Metadata for table: {table_name}, "
                            f"{int(tables_downloaded/len(table_names)*100)}%")
                metadata_rec = cli.get_metadata(table_name)
                tables_downloaded += 1
                try:
                    # 2. Validate here with validate...
                    # 3. Ingest data
                    ingest_oep_metadata(driver, metadata_rec)
                except Exception as e:
                    log.exception("An error occurred during ingesting: %s", e)

            except Exception as e:
                log.exception("An error occurred during downloading: %s", e)

        log.info(f"Ingestion Metadata finished {tables_downloaded}")

    else:
        print("Invalid selection.")
        exit()


    # ---------------------------------------------------------------------
    # 5. Save LinkML report
    # ---------------------------------------------------------------------
    save_linkml_report(filename= RESULT_DIR / "linkml_validation_report.json")

    plot_error_statistics(
        LINKML_ERROR_COUNTER,
        title="LinkML Validation Errors",
        filename= RESULT_DIR / "linkml_validation_errors.png"
    )

    # ---------------------------------------------------------------------
    # 6. Save Neo4j ingestion errors
    # ---------------------------------------------------------------------

    plot_error_statistics(
        ingest_errors,
        title="Neo4j Ingest Error Statistics",
        filename= RESULT_DIR / "neo4j_ingest_errors.png", 
        color="forestgreen"
    )

    # ---------------------------------------------------------------------
    # 7. Combined statistics
    # ---------------------------------------------------------------------

    # All error sources:
    #all_errors = error_counter + ingest_errors
    all_errors = (
        Counter()
        + LINKML_ERROR_COUNTER
        + ingest_errors
    )

    plot_error_statistics(
        all_errors, 
        title="Total Error Statistics (Load + Ingest)", 
        filename= RESULT_DIR / "neo4j_load_ingest_errors.png"
    )

    if 'driver' in locals():
        driver.close()