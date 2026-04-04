# Auto generated from my_linkmk_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2026-03-04T16:08:07
# Schema: regimo_metadata_schema
#
# id: https://example.org/regimo/metadata_integrity_schema
# description: Enforces data integrity for temperature and 3-phase electrical measurements.
# license: MIT

import dataclasses
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from datetime import date, datetime
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import Date, Datetime, Float, String
from linkml_runtime.utils.metamodelcore import XSDDate, XSDDateTime

metamodel_version = "1.7.0"
version = "0.2.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
OEO = CurieNamespace('oeo', 'http://openenergy-platform.org/ontology/oeo/')
REGIMO = CurieNamespace('regimo', 'https://example.org/regimo/')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = REGIMO


# Types

# Class references
class ProjectSubmissionProjectId(extended_str):
    pass


@dataclass
class ProjectSubmission(YAMLRoot):
    """
    Container for one or more measurement records.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = REGIMO["ProjectSubmission"]
    class_class_curie: ClassVar[str] = "regimo:ProjectSubmission"
    class_name: ClassVar[str] = "ProjectSubmission"
    class_model_uri: ClassVar[URIRef] = REGIMO.ProjectSubmission

    project_id: Union[str, ProjectSubmissionProjectId] = None
    operator_name: str = None
    project_start_date: Union[str, XSDDate] = None
    records: Optional[Union[Union[dict, "MeasurementRecord"], List[Union[dict, "MeasurementRecord"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.project_id):
            self.MissingRequiredField("project_id")
        if not isinstance(self.project_id, ProjectSubmissionProjectId):
            self.project_id = ProjectSubmissionProjectId(self.project_id)

        if self._is_empty(self.operator_name):
            self.MissingRequiredField("operator_name")
        if not isinstance(self.operator_name, str):
            self.operator_name = str(self.operator_name)

        if self._is_empty(self.project_start_date):
            self.MissingRequiredField("project_start_date")
        if not isinstance(self.project_start_date, XSDDate):
            self.project_start_date = XSDDate(self.project_start_date)

        if not isinstance(self.records, list):
            self.records = [self.records] if self.records is not None else []
        self.records = [v if isinstance(v, MeasurementRecord) else MeasurementRecord(**as_dict(v)) for v in self.records]

        super().__post_init__(**kwargs)


@dataclass
class MeasurementRecord(YAMLRoot):
    """
    Single measurement event (Temperature or 3-Phase Power).
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = REGIMO["MeasurementRecord"]
    class_class_curie: ClassVar[str] = "regimo:MeasurementRecord"
    class_name: ClassVar[str] = "MeasurementRecord"
    class_model_uri: ClassVar[URIRef] = REGIMO.MeasurementRecord

    sample_unique_id: str = None
    measurement_time: Union[str, XSDDateTime] = None
    instrument_calibration_date: Union[str, XSDDate] = None
    temperature_celsius: Optional[float] = None
    temperature_kelvin: Optional[float] = None
    voltage_l1: Optional[float] = None
    voltage_l2: Optional[float] = None
    voltage_l3: Optional[float] = None
    current_l1: Optional[float] = None
    current_l2: Optional[float] = None
    current_l3: Optional[float] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.sample_unique_id):
            self.MissingRequiredField("sample_unique_id")
        if not isinstance(self.sample_unique_id, str):
            self.sample_unique_id = str(self.sample_unique_id)

        if self._is_empty(self.measurement_time):
            self.MissingRequiredField("measurement_time")
        if not isinstance(self.measurement_time, XSDDateTime):
            self.measurement_time = XSDDateTime(self.measurement_time)

        if self._is_empty(self.instrument_calibration_date):
            self.MissingRequiredField("instrument_calibration_date")
        if not isinstance(self.instrument_calibration_date, XSDDate):
            self.instrument_calibration_date = XSDDate(self.instrument_calibration_date)

        if self.temperature_celsius is not None and not isinstance(self.temperature_celsius, float):
            self.temperature_celsius = float(self.temperature_celsius)

        if self.temperature_kelvin is not None and not isinstance(self.temperature_kelvin, float):
            self.temperature_kelvin = float(self.temperature_kelvin)

        if self.voltage_l1 is not None and not isinstance(self.voltage_l1, float):
            self.voltage_l1 = float(self.voltage_l1)

        if self.voltage_l2 is not None and not isinstance(self.voltage_l2, float):
            self.voltage_l2 = float(self.voltage_l2)

        if self.voltage_l3 is not None and not isinstance(self.voltage_l3, float):
            self.voltage_l3 = float(self.voltage_l3)

        if self.current_l1 is not None and not isinstance(self.current_l1, float):
            self.current_l1 = float(self.current_l1)

        if self.current_l2 is not None and not isinstance(self.current_l2, float):
            self.current_l2 = float(self.current_l2)

        if self.current_l3 is not None and not isinstance(self.current_l3, float):
            self.current_l3 = float(self.current_l3)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.project_id = Slot(uri=REGIMO.project_id, name="project_id", curie=REGIMO.curie('project_id'),
                   model_uri=REGIMO.project_id, domain=None, range=URIRef,
                   pattern=re.compile(r'^REGIMO-\d{4}-\d{3}$'))

slots.project_start_date = Slot(uri=REGIMO.project_start_date, name="project_start_date", curie=REGIMO.curie('project_start_date'),
                   model_uri=REGIMO.project_start_date, domain=None, range=Union[str, XSDDate])

slots.operator_name = Slot(uri=REGIMO.operator_name, name="operator_name", curie=REGIMO.curie('operator_name'),
                   model_uri=REGIMO.operator_name, domain=None, range=str)

slots.sample_unique_id = Slot(uri=REGIMO.sample_unique_id, name="sample_unique_id", curie=REGIMO.curie('sample_unique_id'),
                   model_uri=REGIMO.sample_unique_id, domain=None, range=str,
                   pattern=re.compile(r'^SAMPLE-\d{3}$'))

slots.measurement_time = Slot(uri=REGIMO.measurement_time, name="measurement_time", curie=REGIMO.curie('measurement_time'),
                   model_uri=REGIMO.measurement_time, domain=None, range=Union[str, XSDDateTime])

slots.instrument_calibration_date = Slot(uri=REGIMO.instrument_calibration_date, name="instrument_calibration_date", curie=REGIMO.curie('instrument_calibration_date'),
                   model_uri=REGIMO.instrument_calibration_date, domain=None, range=Union[str, XSDDate])

slots.temperature_celsius = Slot(uri=REGIMO.temperature_celsius, name="temperature_celsius", curie=REGIMO.curie('temperature_celsius'),
                   model_uri=REGIMO.temperature_celsius, domain=None, range=Optional[float])

slots.temperature_kelvin = Slot(uri=REGIMO.temperature_kelvin, name="temperature_kelvin", curie=REGIMO.curie('temperature_kelvin'),
                   model_uri=REGIMO.temperature_kelvin, domain=None, range=Optional[float])

slots.voltage_l1 = Slot(uri=REGIMO.voltage_l1, name="voltage_l1", curie=REGIMO.curie('voltage_l1'),
                   model_uri=REGIMO.voltage_l1, domain=None, range=Optional[float])

slots.voltage_l2 = Slot(uri=REGIMO.voltage_l2, name="voltage_l2", curie=REGIMO.curie('voltage_l2'),
                   model_uri=REGIMO.voltage_l2, domain=None, range=Optional[float])

slots.voltage_l3 = Slot(uri=REGIMO.voltage_l3, name="voltage_l3", curie=REGIMO.curie('voltage_l3'),
                   model_uri=REGIMO.voltage_l3, domain=None, range=Optional[float])

slots.current_l1 = Slot(uri=REGIMO.current_l1, name="current_l1", curie=REGIMO.curie('current_l1'),
                   model_uri=REGIMO.current_l1, domain=None, range=Optional[float])

slots.current_l2 = Slot(uri=REGIMO.current_l2, name="current_l2", curie=REGIMO.curie('current_l2'),
                   model_uri=REGIMO.current_l2, domain=None, range=Optional[float])

slots.current_l3 = Slot(uri=REGIMO.current_l3, name="current_l3", curie=REGIMO.curie('current_l3'),
                   model_uri=REGIMO.current_l3, domain=None, range=Optional[float])

slots.records = Slot(uri=REGIMO.records, name="records", curie=REGIMO.curie('records'),
                   model_uri=REGIMO.records, domain=None, range=Optional[Union[Union[dict, MeasurementRecord], List[Union[dict, MeasurementRecord]]]])
