import sys
from linkml_runtime.loaders import yaml_loader
from my_linkmk_schema.datamodel.my_linkmk_schema import ProjectSubmission

filename = sys.argv[1] if len(sys.argv) > 1 else "examples/valid_submission.yaml"
print(f"Loading and validating: {filename}")

try:
    instance = yaml_loader.load(filename, target_class=ProjectSubmission)
    print("No validation errors")
    print(f"Successfully loaded {len(instance.records)} measurement records")
except Exception as e:
    print(f"Validation failed: {e}")
