# Regimo Metadata Integrity Schema

Enforces data integrity for temperature and 3-phase electrical measurements.

URI: https://example.org/regimo/metadata_integrity_schema

Name: regimo_metadata_schema



## Classes

| Class | Description |
| --- | --- |
| [MeasurementRecord](MeasurementRecord.md) | Single measurement event (Temperature or 3-Phase Power). |
| [ProjectSubmission](ProjectSubmission.md) | Container for one or more measurement records. |



## Slots

| Slot | Description |
| --- | --- |
| [current_l1](current_l1.md) | Current on Phase 1 (Max 16A for standard lab socket) |
| [current_l2](current_l2.md) |  |
| [current_l3](current_l3.md) |  |
| [instrument_calibration_date](instrument_calibration_date.md) |  |
| [measurement_time](measurement_time.md) |  |
| [operator_name](operator_name.md) |  |
| [project_id](project_id.md) |  |
| [project_start_date](project_start_date.md) |  |
| [records](records.md) | List of all measurement records in this submission |
| [sample_unique_id](sample_unique_id.md) |  |
| [temperature_celsius](temperature_celsius.md) |  |
| [temperature_kelvin](temperature_kelvin.md) |  |
| [voltage_l1](voltage_l1.md) | Voltage on Phase 1 (Target 230V) |
| [voltage_l2](voltage_l2.md) |  |
| [voltage_l3](voltage_l3.md) |  |


## Enumerations

| Enumeration | Description |
| --- | --- |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |
