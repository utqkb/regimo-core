# Auto generated from my_linkmk_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-12-09T01:43:02
# Schema: regimo_metadata_schema
#
# id: https://example.org/regimo/metadata_integrity_schema
# description: Enforces data integrity, provenance and FAIR principles for temperature measurements.
# license: MIT

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)

from linkml_runtime.linkml_model.types import Date, Datetime, String
from linkml_runtime.utils.metamodelcore import XSDDate, XSDDateTime

metamodel_version = "1.7.0"
version = "0.1.0"

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
OEO = CurieNamespace('oeo', 'http://openenergy-platform.org/ontology/oeo/')
REGIMO = CurieNamespace('regimo', 'https://example.org/regimo/')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = REGIMO


# Types
class MeasurementValue(float):
    """ Temperature reading as a floating-point number """
    type_class_uri = XSD["float"]
    type_class_curie = "xsd:float"
    type_name = "MeasurementValue"
    type_model_uri = REGIMO.MeasurementValue


# Class references



@dataclass(repr=False)
class ProjectSubmission(YAMLRoot):
    """
    Container for one or more measurement records
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = REGIMO["ProjectSubmission"]
    class_class_curie: ClassVar[str] = "regimo:ProjectSubmission"
    class_name: ClassVar[str] = "ProjectSubmission"
    class_model_uri: ClassVar[URIRef] = REGIMO.ProjectSubmission

    project_id: Optional[str] = None
    operator_name: Optional[str] = None
    records: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.project_id is not None and not isinstance(self.project_id, str):
            self.project_id = str(self.project_id)

        if self.operator_name is not None and not isinstance(self.operator_name, str):
            self.operator_name = str(self.operator_name)

        if self.records is not None and not isinstance(self.records, str):
            self.records = str(self.records)

        super().__post_init__(**kwargs)


@dataclass(repr=False)
class MeasurementRecord(YAMLRoot):
    """
    Single temperature measurement with provenance
    """
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = REGIMO["MeasurementRecord"]
    class_class_curie: ClassVar[str] = "regimo:MeasurementRecord"
    class_name: ClassVar[str] = "MeasurementRecord"
    class_model_uri: ClassVar[URIRef] = REGIMO.MeasurementRecord

    sample_unique_id: Optional[str] = None
    measurement_time: Optional[str] = None
    temperature_value: Optional[str] = None
    temperature_unit: Optional[str] = None
    instrument_calibration_date: Optional[str] = None

    def __post_init__(self, *_: str, **kwargs: Any):
        if self.sample_unique_id is not None and not isinstance(self.sample_unique_id, str):
            self.sample_unique_id = str(self.sample_unique_id)

        if self.measurement_time is not None and not isinstance(self.measurement_time, str):
            self.measurement_time = str(self.measurement_time)

        if self.temperature_value is not None and not isinstance(self.temperature_value, str):
            self.temperature_value = str(self.temperature_value)

        if self.temperature_unit is not None and not isinstance(self.temperature_unit, str):
            self.temperature_unit = str(self.temperature_unit)

        if self.instrument_calibration_date is not None and not isinstance(self.instrument_calibration_date, str):
            self.instrument_calibration_date = str(self.instrument_calibration_date)

        super().__post_init__(**kwargs)


# Enumerations
class UnitOfTemperature(EnumDefinitionImpl):
    """
    Allowed temperature units
    """
    Kelvin = PermissibleValue(
        text="Kelvin",
        description="Kelvin scale",
        meaning=OEO["OEO_00020034"])
    Celsius = PermissibleValue(
        text="Celsius",
        description="Degrees Celsius",
        meaning=OEO["OEO_00020035"])

    _defn = EnumDefinition(
        name="UnitOfTemperature",
        description="Allowed temperature units",
    )

# Slots
class slots:
    pass

slots.project_id = Slot(uri=REGIMO.project_id, name="project_id", curie=REGIMO.curie('project_id'),
                   model_uri=REGIMO.project_id, domain=None, range=URIRef)

slots.operator_name = Slot(uri=REGIMO.operator_name, name="operator_name", curie=REGIMO.curie('operator_name'),
                   model_uri=REGIMO.operator_name, domain=None, range=str)

slots.sample_unique_id = Slot(uri=REGIMO.sample_unique_id, name="sample_unique_id", curie=REGIMO.curie('sample_unique_id'),
                   model_uri=REGIMO.sample_unique_id, domain=None, range=str)

slots.measurement_time = Slot(uri=REGIMO.measurement_time, name="measurement_time", curie=REGIMO.curie('measurement_time'),
                   model_uri=REGIMO.measurement_time, domain=None, range=Union[str, XSDDateTime])

slots.temperature_value = Slot(uri=REGIMO.temperature_value, name="temperature_value", curie=REGIMO.curie('temperature_value'),
                   model_uri=REGIMO.temperature_value, domain=None, range=float)

slots.temperature_unit = Slot(uri=OEO.OEO_00020035, name="temperature_unit", curie=OEO.curie('OEO_00020035'),
                   model_uri=REGIMO.temperature_unit, domain=None, range=Union[str, "UnitOfTemperature"])

slots.instrument_calibration_date = Slot(uri=REGIMO.instrument_calibration_date, name="instrument_calibration_date", curie=REGIMO.curie('instrument_calibration_date'),
                   model_uri=REGIMO.instrument_calibration_date, domain=None, range=Union[str, XSDDate])

slots.records = Slot(uri=REGIMO.records, name="records", curie=REGIMO.curie('records'),
                   model_uri=REGIMO.records, domain=None, range=Optional[Union[Union[dict, MeasurementRecord], list[Union[dict, MeasurementRecord]]]])

slots.projectSubmission__project_id = Slot(uri=REGIMO.project_id, name="projectSubmission__project_id", curie=REGIMO.curie('project_id'),
                   model_uri=REGIMO.projectSubmission__project_id, domain=None, range=Optional[str])

slots.projectSubmission__operator_name = Slot(uri=REGIMO.operator_name, name="projectSubmission__operator_name", curie=REGIMO.curie('operator_name'),
                   model_uri=REGIMO.projectSubmission__operator_name, domain=None, range=Optional[str])

slots.projectSubmission__records = Slot(uri=REGIMO.records, name="projectSubmission__records", curie=REGIMO.curie('records'),
                   model_uri=REGIMO.projectSubmission__records, domain=None, range=Optional[str])

slots.measurementRecord__sample_unique_id = Slot(uri=REGIMO.sample_unique_id, name="measurementRecord__sample_unique_id", curie=REGIMO.curie('sample_unique_id'),
                   model_uri=REGIMO.measurementRecord__sample_unique_id, domain=None, range=Optional[str])

slots.measurementRecord__measurement_time = Slot(uri=REGIMO.measurement_time, name="measurementRecord__measurement_time", curie=REGIMO.curie('measurement_time'),
                   model_uri=REGIMO.measurementRecord__measurement_time, domain=None, range=Optional[str])

slots.measurementRecord__temperature_value = Slot(uri=REGIMO.temperature_value, name="measurementRecord__temperature_value", curie=REGIMO.curie('temperature_value'),
                   model_uri=REGIMO.measurementRecord__temperature_value, domain=None, range=Optional[str])

slots.measurementRecord__temperature_unit = Slot(uri=REGIMO.temperature_unit, name="measurementRecord__temperature_unit", curie=REGIMO.curie('temperature_unit'),
                   model_uri=REGIMO.measurementRecord__temperature_unit, domain=None, range=Optional[str])

slots.measurementRecord__instrument_calibration_date = Slot(uri=REGIMO.instrument_calibration_date, name="measurementRecord__instrument_calibration_date", curie=REGIMO.curie('instrument_calibration_date'),
                   model_uri=REGIMO.measurementRecord__instrument_calibration_date, domain=None, range=Optional[str])
