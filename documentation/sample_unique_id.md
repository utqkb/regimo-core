

# Slot: sample_unique_id


_Unique identifier of the sample. Must follow the pattern SAMPLE-NNN (e.g. SAMPLE-001)._

__



URI: [regimo:sample_unique_id](https://example.org/regimo/sample_unique_id)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MeasurementRecord](MeasurementRecord.md) | Single temperature measurement with provenance |  no  |







## Properties

* Range: [String](String.md)

* Required: True

* Regex pattern: `^SAMPLE-\d{3}$`





## Identifier and Mapping Information







### Schema Source


* from schema: https://example.org/regimo/metadata_integrity_schema




## LinkML Source

<details>
```yaml
name: sample_unique_id
description: 'Unique identifier of the sample. Must follow the pattern SAMPLE-NNN
  (e.g. SAMPLE-001).

  '
from_schema: https://example.org/regimo/metadata_integrity_schema
rank: 1000
alias: sample_unique_id
domain_of:
- MeasurementRecord
range: string
required: true
pattern: ^SAMPLE-\d{3}$

```
</details>