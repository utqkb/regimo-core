

# Slot: voltage_l1


_Voltage on Phase 1 (Target 230V)_



URI: [regimo:voltage_l1](https://example.org/regimo/voltage_l1)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MeasurementRecord](MeasurementRecord.md) | Single measurement event (Temperature or 3-Phase Power) |  no  |







## Properties

* Range: [Float](Float.md)

* Minimum Value: 200

* Maximum Value: 250





## Identifier and Mapping Information







### Schema Source


* from schema: https://example.org/regimo/metadata_integrity_schema




## LinkML Source

<details>
```yaml
name: voltage_l1
description: Voltage on Phase 1 (Target 230V)
from_schema: https://example.org/regimo/metadata_integrity_schema
rank: 1000
alias: voltage_l1
domain_of:
- MeasurementRecord
range: float
minimum_value: 200
maximum_value: 250

```
</details>