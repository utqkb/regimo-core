from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "None"
version = "0.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )

    @model_serializer(mode='wrap', when_used='unless-none')
    def treat_empty_lists_as_none(
            self, handler: SerializerFunctionWrapHandler,
            info: SerializationInfo) -> dict[str, Any]:
        if info.exclude_none:
            _instance = self.model_copy()
            for field, field_info in type(_instance).model_fields.items():
                if getattr(_instance, field) == [] and not(
                        field_info.is_required()):
                    setattr(_instance, field, None)
        else:
            _instance = self
        return handler(_instance, info)



class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'regimo',
     'default_range': 'string',
     'description': 'Enforces data integrity, provenance and FAIR principles for '
                    'temperature measurements in energy research.',
     'id': 'https://example.org/regimo/metadata_integrity_schema',
     'imports': ['linkml:types'],
     'license': 'MIT',
     'name': 'regimo_metadata_schema',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'oeo': {'prefix_prefix': 'oeo',
                          'prefix_reference': 'http://openenergy-platform.org/ontology/oeo/'},
                  'regimo': {'prefix_prefix': 'regimo',
                             'prefix_reference': 'https://example.org/regimo/'},
                  'xsd': {'prefix_prefix': 'xsd',
                          'prefix_reference': 'http://www.w3.org/2001/XMLSchema#'}},
     'source_file': 'src/my_linkmk_schema/schema/my_linkmk_schema.yaml',
     'title': 'Regimo Metadata Integrity Schema',
     'types': {'MeasurementValue': {'base': 'float',
                                    'description': 'Temperature reading as a '
                                                   'floating-point number',
                                    'from_schema': 'https://example.org/regimo/metadata_integrity_schema',
                                    'name': 'MeasurementValue',
                                    'uri': 'xsd:float'}}} )

class UnitOfTemperature(str, Enum):
    """
    Allowed temperature units
    """
    Kelvin = "Kelvin"
    """
    Kelvin scale
    """
    Celsius = "Celsius"
    """
    Degrees Celsius
    """



class ProjectSubmission(ConfiguredBaseModel):
    """
    Container for one or more measurement records
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/regimo/metadata_integrity_schema',
         'tree_root': True})

    project_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['ProjectSubmission']} })
    operator_name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['ProjectSubmission']} })
    records: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['ProjectSubmission']} })


class MeasurementRecord(ConfiguredBaseModel):
    """
    Single temperature measurement with provenance
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/regimo/metadata_integrity_schema'})

    sample_unique_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['MeasurementRecord']} })
    measurement_time: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['MeasurementRecord']} })
    temperature_value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['MeasurementRecord']} })
    temperature_unit: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['MeasurementRecord']} })
    instrument_calibration_date: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['MeasurementRecord']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ProjectSubmission.model_rebuild()
MeasurementRecord.model_rebuild()
