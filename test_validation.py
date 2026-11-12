from pydantic import ValidationError
from my_linkmk_schema.datamodel import QuestionnaireAnswer, RDMOProject

print("--- Testing QuestionnaireAnswer attribute_path validation ---")

# 1. Test VALID attribute_path
try:
    ans_valid = QuestionnaireAnswer(
        attribute_path="project/dataset/identifier",
        value_text="SAMPLE-001",
        value_datatype="string"
    )
    print("SUCCESS: Valid attribute_path passed validation:", ans_valid.attribute_path)
except ValidationError as e:
    print("FAILURE: Valid attribute_path failed unexpectedly:", e)

# 2. Test INVALID attribute_path (contains spaces or uppercase)
try:
    ans_invalid = QuestionnaireAnswer(
        attribute_path="Project Dataset/Identifier!",
        value_text="SAMPLE-001",
        value_datatype="string"
    )
    print("FAILURE: Invalid attribute_path incorrectly passed validation!")
except ValidationError as e:
    print("SUCCESS: Invalid attribute_path correctly caught by regex validation!")
    # print(e)


print("\n--- Testing RDMOProject linked_oep_datasets validation ---")

# 3. Test VALID linked_oep_datasets
try:
    proj_valid = RDMOProject(
        rdmo_id=1,
        title="Smart Lab Test",
        linked_oep_datasets=["OEP-12345"]
    )
    print("SUCCESS: Valid linked_oep_dataset passed validation:", proj_valid.linked_oep_datasets)
except ValidationError as e:
    print("FAILURE: Valid linked_oep_dataset failed unexpectedly:", e)

# 4. Test INVALID linked_oep_datasets (wrong format, e.g. missing digits or prefix)
try:
    proj_invalid = RDMOProject(
        rdmo_id=1,
        title="Smart Lab Test",
        linked_oep_datasets=["DATASET-999"]
    )
    print("FAILURE: Invalid linked_oep_dataset incorrectly passed validation!")
except ValidationError as e:
    print("SUCCESS: Invalid linked_oep_dataset correctly caught by regex validation!")
    # print(e)
