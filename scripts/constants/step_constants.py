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
            "type": "equals",
            "filter": ""
        },
        "display_title": {
            "filterType": "text",
            "type": "equals",
            "filter": ""
        },
        "step_category": {
            "values": []
        },
    }

    step_metadata_mapping = {
        'step name': 'step_name',
        'display title': 'display_title',
        'description': 'description',
        'step category': 'step_category',
        'step sub category': 'step_sub_category',
        'menu placement': 'menu_placement',
        'validate form': 'validate_form',
        'auto save': 'auto_save',
        'sheet': 'sheet'
    }

    menu_placement_mapping = {
        "left navigation": "left_navigation",
        "top navigation": "top_navigation"
    }

    step_category_mapping = {
        "batch creation step": "step_category_104",
        "non-periodic step": "step_category_100",
        "non periodic step": "step_category_100",
        "periodic step": "step_category_102",
        "task creation step": "step_category_101",
        "trigger-based step": "step_category_103",
        "trigger based step": "step_category_103"
    }