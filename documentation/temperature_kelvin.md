

# Slot: temperature_kelvin


_Room temperature measured in Kelvin. Valid range: 283.15–313.15 K._

__



URI: [regimo:temperature_kelvin](https://example.org/regimo/temperature_kelvin)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MeasurementRecord](MeasurementRecord.md) | Single temperature measurement with provenance |  no  |







## Properties

* Range: [Float](Float.md)

* Minimum Value: 283

* Maximum Value: 313





## Identifier and Mapping Information







### Schema Source


* from schema: https://example.org/regimo/metadata_integrity_schema




## LinkML Source

<details>
```yaml
name: temperature_kelvin
description: 'Room temperature measured in Kelvin. Valid range: 283.15–313.15 K.

  '
from_schema: https://example.org/regimo/metadata_integrity_schema
rank: 1000
alias: temperature_kelvin
domain_of:
- MeasurementRecord
range: float
minimum_value: 283.15
maximum_value: 313.15

```
</details>