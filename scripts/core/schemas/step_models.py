from enum import Enum
from typing import Optional
from pydantic import BaseModel
from scripts.constants import EnvironmentConstants


class StepValidatePayloadModel(BaseModel):
    dateKeys: Optional[list]
    project_id: Optional[str] = EnvironmentConstants.project_id
    step_id: Optional[str]
    data: Optional[dict]
    field_props: Optional[dict]
    property_names: Optional[list]
    step_category: Optional[str]
    project_type: Optional[str]
    tz: Optional[str]
    language: Optional[str]


class StepUpdatePayloadModel(BaseModel):
    dateKeys: Optional[list]
    project_id: Optional[str] = EnvironmentConstants.project_id
    step_id: Optional[str]
    step_name: Optional[str]
    description: Optional[str]
    display_title: Optional[str]
    menu_placement: Optional[str]
    step_category: Optional[str]
    step_sub_category: Optional[str]
    form_factor: Optional[list]
    validate_form: Optional[bool]
    auto_save: Optional[bool]
    data: Optional[dict]
    field_props: Optional[dict]
    step_version: Optional[int]
    project_type: Optional[str]
    tz: Optional[str]
    language: Optional[str]


class StepCategoryDropdown(str, Enum):
    step_category_104 = "Batch Creation Step"
    step_category_100 = 'Non-Periodic Step'
    step_category_102 = 'Periodic Step'
    step_category_101 = 'Task Creation Step'
    step_category_103 = 'Trigger-based Step'


class MenuPlacementDropdown(str, Enum):
    left_navigation = "Left Navigation"
    top_navigation = 'Top Navigation'
