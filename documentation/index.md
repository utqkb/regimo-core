# Regimo Metadata Integrity Schema

Enforces data integrity, provenance and FAIR principles for temperature measurements.

URI: https://example.org/regimo/metadata_integrity_schema

Name: regimo_metadata_schema



## Classes

| Class | Description |
| --- | --- |
| [MeasurementRecord](MeasurementRecord.md) | Single temperature measurement with provenance |
| [ProjectSubmission](ProjectSubmission.md) | Container for one or more measurement records |



## Slots

| Slot | Description |
| --- | --- |
| [instrument_calibration_date](instrument_calibration_date.md) | Date the instrument was last calibrated |
| [measurement_time](measurement_time.md) | Date and time of the measurement |
| [operator_name](operator_name.md) | Person responsible for the measurement |
| [project_id](project_id.md) | Unique project identifier |
| [project_start_date](project_start_date.md) | Date when the project officially started |
| [records](records.md) | List of all measurement records in this submission |
| [sample_unique_id](sample_unique_id.md) | Unique identifier of the sample |
| [temperature_celsius](temperature_celsius.md) | Room temperature measured in degrees Celsius |
| [temperature_kelvin](temperature_kelvin.md) | Room temperature measured in Kelvin |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [UnitOfTemperature](UnitOfTemperature.md) | Allowed units for temperature measurements |


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
| [MeasurementValue](MeasurementValue.md) | Temperature reading as a floating-point number |
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
