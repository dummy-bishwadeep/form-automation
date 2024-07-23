from scripts.constants import EnvironmentConstants
from scripts.constants.app_constants import AutomationConstants


class StepConstants:
    fetch_step_data_payload = {
        "startRow": 0,
        "endRow": 100,
        "page": 1,
        "records": 100,
        "filters": {
            "sortModel": [],
            "filterModel": {}
        },
        "global_filters": {},
        "metaData": {},
        "tag_fetch_type": "",
        "project_id": EnvironmentConstants.project_id,
        "project_type": AutomationConstants.project_type,
        "tz": EnvironmentConstants.tz,
        "language": AutomationConstants.language
    }

    fetch_step_data_filter_model = {
        "step_name": {
            "filterType": "text",
            "type": "contains",
            "filter": ""
        },
        "display_title": {
            "filterType": "text",
            "type": "contains",
            "filter": ""
        },
        "step_category": {
            "values": []
        },
    }

    MetaData = {
        "step_name": "",
        "display_title": "",
        "description": "",
        "step_category": "",
        "step_sub_categroy": "",
        "menu_placement": "",
        "validate_form": "",
        "auto_save": "",
        "sheet_name": ""
    }

    MenuPlacementDropdown = {
        "left_navigation": "Left Navigation",
        "top_navigation": "Top Navigation"
    }

    StepCategoryDropdown = {
        "batch_creation_step": "Batch Creation Step",
        "non_periodic_step": "Non-Periodic Step",
        "periodic_step": "Periodic Step",
        "task_creation_step": "Task Creation Step",
        "trigger_based_step": "Trigger-based Step"
    }
