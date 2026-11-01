from __future__ import annotations 
from datetime import (
    datetime,
    date
)
from decimal import Decimal 
from enum import Enum 
import re
import sys
from typing import (
    Any,
    List,
    Literal,
    Dict,
    Optional,
    Union
)
from pydantic.version import VERSION  as PYDANTIC_VERSION 
if int(PYDANTIC_VERSION[0])>=2:
    from pydantic import (
        BaseModel,
        ConfigDict,
        Field,
        field_validator
    )
else:
    from pydantic import (
        BaseModel,
        Field,
        validator
    )

metamodel_version = "None"
version = "0.3.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass


class ProjectSubmission(ConfiguredBaseModel):
    """
    Container for one or more measurement records.
    """
    project_id: str = Field(...)
    operator_name: str = Field(...)
    project_start_date: date = Field(...)
    records: Optional[List[MeasurementRecord]] = Field(default_factory=list, description="""List of all measurement records in this submission.""")

    @field_validator('project_id')
    def pattern_project_id(cls, v):
        pattern=re.compile(r"^REGIMO-\d{4}-\d{3}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid project_id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid project_id format: {v}")
        return v


class MeasurementRecord(ConfiguredBaseModel):
    """
    Single measurement event (Temperature or 3-Phase Power).
    """
    sample_unique_id: str = Field(...)
    measurement_time: datetime  = Field(...)
    instrument_calibration_date: date = Field(...)
    temperature_celsius: Optional[float] = Field(None, ge=10, le=40)
    temperature_kelvin: Optional[float] = Field(None, ge=283.15, le=313.15)
    voltage_l1: Optional[float] = Field(None, ge=200, le=250)
    voltage_l2: Optional[float] = Field(None, ge=200, le=250)
    voltage_l3: Optional[float] = Field(None, ge=200, le=250)
    current_l1: Optional[float] = Field(None, ge=0, le=16)
    current_l2: Optional[float] = Field(None, ge=0, le=16)
    current_l3: Optional[float] = Field(None, ge=0, le=16)

    @field_validator('sample_unique_id')
    def pattern_sample_unique_id(cls, v):
        pattern=re.compile(r"^SAMPLE-\d{3}$")
        if isinstance(v,list):
            for element in v:
                if not pattern.match(element):
                    raise ValueError(f"Invalid sample_unique_id format: {element}")
        elif isinstance(v,str):
            if not pattern.match(v):
                raise ValueError(f"Invalid sample_unique_id format: {v}")
        return v


class RDMOProject(ConfiguredBaseModel):
    """
    Entity representing an RDMO project imported into Regimo.
    """
    rdmo_id: int = Field(..., description="""Primary key ID of the RDMO project.""")
    title: str = Field(...)
    description: Optional[str] = Field(None)
    created: Optional[datetime ] = Field(None)
    updated: Optional[datetime ] = Field(None)
    answers: Optional[List[QuestionnaireAnswer]] = Field(default_factory=list, description="""Collection of attribute answers belonging to this project.""")
    linked_oep_datasets: Optional[List[str]] = Field(default_factory=list, description="""Identifiers linking this RDMO project to OEP research datasets in Neo4j.""")


class QuestionnaireAnswer(ConfiguredBaseModel):
    """
    Individual attribute-value response from an RDMO questionnaire.
    """
    attribute_path: str = Field(..., description="""RDMO attribute path (e.g., project/dataset/identifier).""")
    value_text: Optional[str] = Field(None, description="""Textual or URI answer provided in RDMO.""")
    value_datatype: Optional[str] = Field(None)
    unit: Optional[str] = Field(None)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ProjectSubmission.model_rebuild()
MeasurementRecord.model_rebuild()
RDMOProject.model_rebuild()
QuestionnaireAnswer.model_rebuild()

