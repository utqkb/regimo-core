import json
import re

from pathlib import Path
import sys
from typing import List, Dict, Any

from collections import Counter
import matplotlib.pyplot as plt

from linkml.validator import validate


# =============================================================================
# Global Error Statistics
# =============================================================================
LINKML_ERROR_COUNTER = Counter()
LINKML_FAILED_FILES = []


# =============================================================================
# LinkML Error Categorization
# =============================================================================
def categorize_linkml_error(result) -> str:
    """
    Categorizes LinkML validation errors into broader error classes.
    This allows later statistical evaluation (Pareto charts).
    """

    message = str(result.message)
    #print(message)

    # -------------------------
    # Pflichtfeld fehlt / Missing required attribute
    # -------------------------
    if "required" in message.lower():
        return "Missing required attribute /\n Datensatz-Struktur unvollständig" # Incomplete dataset structure
    
    # -------------------------
    # Leerstring obwohl Inhalt erwartet z.B. name: "" / Empty strings (pattern validation)
    # -------------------------
    m = re.search(
        r"'' does not match '.*\\\\S\.\*' in (.+)",
        message
    )
    #print("M: ", m)

    if m:
        path = m.group(1)
        #print("PATH: ", path)

        if path == "/name":
            return "Dataset.name empty"

        if "/primaryKey/" in path:
            return "PrimaryKey empty"

        if "/resources/" in path and "/name" in path:
            return "Resource.name empty"

        if "/fields/" in path and "/name" in path:
            return "Field.name empty"
        
        if "/fields/" in path and "/type" in path:
            return "Field.type empty"
        
        return f"Empty value ({path})"
    
    # -------------------------
    # Datentyp falsch / Wrong datatype
    # -------------------------
    if "range" in message.lower():
        return "Wrong datatype"

    if "is not of type" in message.lower():
        return "Wrong datatype"
    
    # -------------------------
    # URI validation
    # -------------------------
    if "uri" in message.lower():
        return "Invalid URI"

    # -------------------------
    # Boolean validation
    # -------------------------
    if "boolean" in message.lower():
        return "Invalid boolean"

    # -------------------------
    # Patternfehler allgemein / Pattern mismatch
    # -------------------------
    if "does not match" in message.lower():
        return "Pattern mismatch"

    # -------------------------
    # Not Valid
    # -------------------------
    if "is not valid" in message.lower():
        return message #"Not Valid"
    
    # -------------------------
    # Additional properties
    # -------------------------
    if "additional properties are not allowed" in message.lower():
        return "Additional properties are not allowed -> WIP"

    return message # "Other LinkML validation error"


# =============================================================================
# Validation of a single dataset
# =============================================================================
# Validiert einen einzelnen Datensatz gegen das LinkMl-Schema
def validate_with_linkml(
        json_data: Dict[str, Any],
        schema_path: Path,
        filename: str
    ) -> bool:

    """
    Validiert OEMetadata JSON gegen LinkML Schema.
    Gibt True zurück, wenn valide.

    /
    
    Validates one metadata JSON against the LinkML schema.

    Parameters
    ----------
    json_data
        Loaded metadata JSON.

    schema_path
        Path to the LinkML YAML schema.

    filename
        Filename (only used for reporting).

    Returns
    -------
    bool
        True if validation succeeded,
        False otherwise.
    """

    try:
        #print("TRY VALIDATION: ")

        report = validate(
            json_data,
            schema=str(schema_path),
            target_class="Dataset"
        )
        #print("REPORT: ", report)

        # ------------------------------------------------------------------
        # Ignore "Additional properties are not allowed" -> Dadurch werden Additional Properties erlaubt
        # ------------------------------------------------------------------
        filtered_results = [
            result for result in report.results
            if "additional properties are not allowed"
            not in str(result.message).lower()
        ]

        # Ausgabe für Fehler in Console
        if filtered_results:                            #report.results: -> filtered_results:
            #Printausgabe für die Fehler in der Console
            print("\n" + "=" * 80)
            print(f"❌ LINKML VALIDATION FAILED: {filename} with {len(filtered_results)} errors:")  # report.results -> filtered_results
            print("=" * 80)

            for i, result in enumerate(filtered_results, start=1): # report.results -> filtered_results
                print(f"\nError {i}")
                print("-" * 40)
                print(f"Type:     {result.type}")
                print(f"Severity: {result.severity}")
                print(f"Message:  {result.message}")

                if result.context:
                    print("Context:")
                    for ctx in result.context:
                        print(f"  - {ctx}")

            print("\n" + "=" * 80 + "\n")

        #if report.results:  
            #Fehler in Liste schreiben für anschließende Statistik
            for result in filtered_results:                                 # filtered_results -> report.results:
                #print(f"Result Message: - {result.message}")
                error_type = categorize_linkml_error(result)
                LINKML_ERROR_COUNTER[error_type] += 1
            LINKML_FAILED_FILES.append(filename)
            
            return False

        print("✅ The file is valid!")
        return True

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
        
        '''
        LINKML_ERROR_COUNTER[
            f"LinkML Exception: {type(e).__name__}"
        ] += 1

        
        LINKML_FAILED_FILES.append(filename)

        return False
        '''


# =============================================================================
# Validate complete metadata directory
# =============================================================================
# Validiert alle Dateien direkt
def validate_directory(
    metadata_dir: Path,
    schema_path: Path
    ) -> List[Dict[str, Any]]:
    """
    Validates all metadata JSON files inside a directory.

    Only valid datasets are returned for later Neo4j ingestion.

    Parameters
    ----------
    metadata_dir
        Directory containing *_metadata.json files.

    schema_path
        LinkML schema path.

    Returns
    -------
    List[Dict[str, Any]]
        Validated metadata records.
    """

    LINKML_ERROR_COUNTER.clear()
    LINKML_FAILED_FILES.clear()

    valid_records = []

    for filepath in metadata_dir.glob("*.json"):
        print(f"\nLade {filepath.name}") # Loading

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if validate_with_linkml(
                raw_data,
                schema_path,
                filepath.name
                ):

                valid_records.append(raw_data)

                print(f"LinkML validation erfolgreich: {filepath.name}") # successful

            else:
                print(f"LinkML validation fehlgeschlagen: {filepath.name}") # failed


        except FileNotFoundError:
            print(f"{filepath.name}: Datei nicht gefunden") # File not found
            LINKML_ERROR_COUNTER["FileNotFoundError"] += 1


        except json.JSONDecodeError:
            print(f"{filepath.name}: Ungültiges JSON") # Invalid JSON
            LINKML_ERROR_COUNTER["JSONDecodeError"] += 1


        except PermissionError:
            print(f"{filepath.name}: Keine Berechtigung") # Permission denied
            LINKML_ERROR_COUNTER["PermissionError"] += 1


        except Exception as e:
            print(f"{filepath.name}: {type(e).__name__}: {e}")
            LINKML_ERROR_COUNTER[type(e).__name__] += 1


    print("\n========================================")
    print("LINKML VALIDATION SUMMARY")
    print("========================================")
    print(f"Valid datasets:   {len(valid_records)}")
    print(f"Failed datasets:  {len(LINKML_FAILED_FILES)}")
    print(f"Total errors:     {sum(LINKML_ERROR_COUNTER.values())}")
    print("========================================\n")

    return valid_records


# =============================================================================
# Save validation report
# =============================================================================
def save_linkml_report(filename: str = "linkml_validation_report.json"):
    """
    Saves all validation errors into a JSON report.
    """

    report = {
        "failed_files": LINKML_FAILED_FILES,
        "errors": dict(LINKML_ERROR_COUNTER)
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            report,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"LinkML report saved: {filename}")


# =============================================================================
# Plot validation statistics
# =============================================================================
def plot_error_statistics(
    error_counter: Counter,
    title: str = "LinkML Validation Errors",
    filename: str = "linkml_validation_errors.png",
    show: bool = False
):
    """
    Erstellt eine sortierte Säulengrafik der Fehlertypen/klassen
    und speichert sie als Bilddatei.
    
    x-Achse: Fehlertyp/klasse
    y-Achse: Anzahl
    
    /

    Creates a bar plot of validation errors.
    """

    if not error_counter:
        print("No validation errors - no plot generated.")
        return

    # Daten vorbereiten: nach Häufigkeit sortieren (absteigend)
    sorted_items = sorted(error_counter.items(), key=lambda x: x[1], reverse=True)
    labels, values = zip(*sorted_items)


    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color="darkorange")

    plt.xlabel("Fehlertyp/klasse") # Error type
    plt.ylabel("Anzahl")    # Number of occurrences
    plt.title(title)
    plt.xticks(rotation=45, ha="right", fontsize=3)

    # Werte über Balken schreiben
    for i, value in enumerate(values):
        plt.text(i, value, str(value), ha="center", va="bottom", fontsize=3)

    plt.tight_layout()

    # speichern
    plt.savefig(filename, dpi=600, bbox_inches="tight")
    print(f"Fehlerstatistik gespeichert als: {filename}")   # Validation statistics saved:

    # optional anzeigen
    if show:
        plt.show()

    plt.close()


# Sonderfunktionen -> noch WIP 
#from linkml.generators.jsonschemagen import JsonSchemaGenerator
#schema = JsonSchemaGenerator(
#    str(LINKML_SCHEMA_PATH)
#).serialize()
#print(schema)

#from linkml_runtime.utils.schemaview import SchemaView
#sv = SchemaView(str(LINKML_SCHEMA_PATH))
#print(sv.all_classes().keys())
#print("\nOntologyReference:")
#print(sv.get_class("OntologyReference"))
#print("\nField.isAbout:")
#print(sv.get_slot("isAbout"))

#from linkml_runtime.utils.schemaview import SchemaView
#sv = SchemaView(str(LINKML_SCHEMA_PATH))
#for slot_name in sv.get_class("Dataset").attributes:
#    slot = sv.get_slot(slot_name)
#
#    print(
#        slot_name,
#        "required:",
#        slot.required,
#        "min:",
#        slot.minimum_cardinality,
#        "multi:",
#        slot.multivalued
#    )


# =============================================================================
# Standalone Main execution
# =============================================================================
if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # Adapt these paths to your project structure
    # -------------------------------------------------------------------------
    root = next(p for p in Path(__file__).resolve().parents if p.name == "graphon_bach")
    sys.path.append(str(root))

    BASE_DIR = Path("Workflow/B0_Ingestion/graphon_ingestion/metadata/preprocessed") # Pfade anpassen!!!
    LINKML_SCHEMA_PATH = Path("Workflow/B0_Ingestion/graphon_ingestion/models/data-model-oep.yaml") # Pfade anpassen!!!
 
    RESULTS_DIR = Path("Workflow/B0_Ingestion/graphon_ingestion/results")
    RESULTS_DIR.mkdir(exist_ok=True)

    records = validate_directory(BASE_DIR, LINKML_SCHEMA_PATH)

    save_linkml_report(filename= RESULTS_DIR / "linkml_validation_report.json")

    plot_error_statistics(
        LINKML_ERROR_COUNTER,
        title="LinkML Validation Errors",
        filename= RESULTS_DIR / "linkml_validation_errors.png"
    )

    print(f"\n{len(records)} datasets ready for ingestion.")