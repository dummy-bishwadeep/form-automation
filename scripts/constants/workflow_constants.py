from scripts.constants import EnvironmentConstants
from scripts.constants.app_constants import AutomationConstants


class WorkflowConstants:
    fetch_workflow_data_payload = {
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

    fetch_workflow_filter_model = {
        "workflow_name": {
            "filterType": "text",
            "type": "equals",
            "filter": ""
        }
    }

    workflow_mapping = {
        'workflow name': 'workflow_name',
        'description': 'description',
        'categories': 'tags',
        'steps': 'steps',
        'roles': 'roles',
        'enable shifts': 'shift_enabled'
    }

    workflow_dropdown_payload = {
        "project_id": EnvironmentConstants.project_id,
        "project_type": AutomationConstants.project_type,
        "tz": EnvironmentConstants.tz,
        "language": AutomationConstants.language
    }