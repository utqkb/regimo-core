

# Slot: temperature_celsius


_Room temperature measured in degrees Celsius. Valid range: 10–40 °C._

__



URI: [regimo:temperature_celsius](https://example.org/regimo/temperature_celsius)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MeasurementRecord](MeasurementRecord.md) | Single temperature measurement with provenance |  no  |







## Properties

* Range: [Float](Float.md)

* Minimum Value: 10

* Maximum Value: 40





## Identifier and Mapping Information







### Schema Source


* from schema: https://example.org/regimo/metadata_integrity_schema




## LinkML Source

<details>
```yaml
name: temperature_celsius
description: 'Room temperature measured in degrees Celsius. Valid range: 10–40 °C.

  '
from_schema: https://example.org/regimo/metadata_integrity_schema
rank: 1000
alias: temperature_celsius
domain_of:
- MeasurementRecord
range: float
minimum_value: 10
maximum_value: 40

```
</details>