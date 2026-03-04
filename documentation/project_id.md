

# Slot: project_id

URI: [regimo:project_id](https://example.org/regimo/project_id)



<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ProjectSubmission](ProjectSubmission.md) | Container for one or more measurement records |  no  |







## Properties

* Range: [String](String.md)

* Required: True

* Regex pattern: `^REGIMO-\d{4}-\d{3}$`





## Identifier and Mapping Information







### Schema Source


* from schema: https://example.org/regimo/metadata_integrity_schema




## LinkML Source

<details>
```yaml
name: project_id
from_schema: https://example.org/regimo/metadata_integrity_schema
rank: 1000
identifier: true
alias: project_id
domain_of:
- ProjectSubmission
range: string
required: true
pattern: ^REGIMO-\d{4}-\d{3}$

```
</details>