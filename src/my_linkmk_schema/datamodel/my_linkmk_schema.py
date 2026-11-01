# Auto generated from my_linkmk_schema.yaml by pythongen.py version: 0.0.1
# Generation date: 2026-11-01T20:44:42
# Schema: my_linkmk_schema
#
# id: https://example.org/regimo/metadata_integrity_schema
# description: Enforces data integrity for temperature, 3-phase electrical measurements, and RDMO project metadata.
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
from linkml_runtime.linkml_model.types import Date, Datetime, Float, Integer, String
from linkml_runtime.utils.metamodelcore import XSDDate, XSDDateTime

metamodel_version = "1.7.0"
version = "0.3.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
OEO = CurieNamespace('oeo', 'http://openenergy-platform.org/ontology/oeo/')
RDMO = CurieNamespace('rdmo', 'https://rdmorganiser.github.io/terms/')
REGIMO = CurieNamespace('regimo', 'https://example.org/regimo/')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = REGIMO


# Types

# Class references
class ProjectSubmissionProjectId(extended_str):
    pass


class RDMOProjectRdmoId(extended_int):
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


@dataclass
class RDMOProject(YAMLRoot):
    """
    Entity representing an RDMO project imported into Regimo.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = REGIMO["RDMOProject"]
    class_class_curie: ClassVar[str] = "regimo:RDMOProject"
    class_name: ClassVar[str] = "RDMOProject"
    class_model_uri: ClassVar[URIRef] = REGIMO.RDMOProject

    rdmo_id: Union[int, RDMOProjectRdmoId] = None
    title: str = None
    description: Optional[str] = None
    created: Optional[Union[str, XSDDateTime]] = None
    updated: Optional[Union[str, XSDDateTime]] = None
    answers: Optional[Union[Union[dict, "QuestionnaireAnswer"], List[Union[dict, "QuestionnaireAnswer"]]]] = empty_list()
    linked_oep_datasets: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.rdmo_id):
            self.MissingRequiredField("rdmo_id")
        if not isinstance(self.rdmo_id, RDMOProjectRdmoId):
            self.rdmo_id = RDMOProjectRdmoId(self.rdmo_id)

        if self._is_empty(self.title):
            self.MissingRequiredField("title")
        if not isinstance(self.title, str):
            self.title = str(self.title)

        if self.description is not None and not isinstance(self.description, str):
            self.description = str(self.description)

        if self.created is not None and not isinstance(self.created, XSDDateTime):
            self.created = XSDDateTime(self.created)

        if self.updated is not None and not isinstance(self.updated, XSDDateTime):
            self.updated = XSDDateTime(self.updated)

        if not isinstance(self.answers, list):
            self.answers = [self.answers] if self.answers is not None else []
        self.answers = [v if isinstance(v, QuestionnaireAnswer) else QuestionnaireAnswer(**as_dict(v)) for v in self.answers]

        if not isinstance(self.linked_oep_datasets, list):
            self.linked_oep_datasets = [self.linked_oep_datasets] if self.linked_oep_datasets is not None else []
        self.linked_oep_datasets = [v if isinstance(v, str) else str(v) for v in self.linked_oep_datasets]

        super().__post_init__(**kwargs)


@dataclass
class QuestionnaireAnswer(YAMLRoot):
    """
    Individual attribute-value response from an RDMO questionnaire.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = REGIMO["QuestionnaireAnswer"]
    class_class_curie: ClassVar[str] = "regimo:QuestionnaireAnswer"
    class_name: ClassVar[str] = "QuestionnaireAnswer"
    class_model_uri: ClassVar[URIRef] = REGIMO.QuestionnaireAnswer

    attribute_path: str = None
    value_text: Optional[str] = None
    value_datatype: Optional[str] = None
    unit: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.attribute_path):
            self.MissingRequiredField("attribute_path")
        if not isinstance(self.attribute_path, str):
            self.attribute_path = str(self.attribute_path)

        if self.value_text is not None and not isinstance(self.value_text, str):
            self.value_text = str(self.value_text)

        if self.value_datatype is not None and not isinstance(self.value_datatype, str):
            self.value_datatype = str(self.value_datatype)

        if self.unit is not None and not isinstance(self.unit, str):
            self.unit = str(self.unit)

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

slots.rdmo_id = Slot(uri=REGIMO.rdmo_id, name="rdmo_id", curie=REGIMO.curie('rdmo_id'),
                   model_uri=REGIMO.rdmo_id, domain=None, range=URIRef)

slots.title = Slot(uri=REGIMO.title, name="title", curie=REGIMO.curie('title'),
                   model_uri=REGIMO.title, domain=None, range=str)

slots.description = Slot(uri=REGIMO.description, name="description", curie=REGIMO.curie('description'),
                   model_uri=REGIMO.description, domain=None, range=Optional[str])

slots.created = Slot(uri=REGIMO.created, name="created", curie=REGIMO.curie('created'),
                   model_uri=REGIMO.created, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.updated = Slot(uri=REGIMO.updated, name="updated", curie=REGIMO.curie('updated'),
                   model_uri=REGIMO.updated, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.attribute_path = Slot(uri=REGIMO.attribute_path, name="attribute_path", curie=REGIMO.curie('attribute_path'),
                   model_uri=REGIMO.attribute_path, domain=None, range=str)

slots.value_text = Slot(uri=REGIMO.value_text, name="value_text", curie=REGIMO.curie('value_text'),
                   model_uri=REGIMO.value_text, domain=None, range=Optional[str])

slots.value_datatype = Slot(uri=REGIMO.value_datatype, name="value_datatype", curie=REGIMO.curie('value_datatype'),
                   model_uri=REGIMO.value_datatype, domain=None, range=Optional[str])

slots.unit = Slot(uri=REGIMO.unit, name="unit", curie=REGIMO.curie('unit'),
                   model_uri=REGIMO.unit, domain=None, range=Optional[str])

slots.answers = Slot(uri=REGIMO.answers, name="answers", curie=REGIMO.curie('answers'),
                   model_uri=REGIMO.answers, domain=None, range=Optional[Union[Union[dict, QuestionnaireAnswer], List[Union[dict, QuestionnaireAnswer]]]])

slots.linked_oep_datasets = Slot(uri=REGIMO.linked_oep_datasets, name="linked_oep_datasets", curie=REGIMO.curie('linked_oep_datasets'),
                   model_uri=REGIMO.linked_oep_datasets, domain=None, range=Optional[Union[str, List[str]]])