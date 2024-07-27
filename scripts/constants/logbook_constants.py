from scripts.constants import EnvironmentConstants
from scripts.constants.app_constants import AutomationConstants


class LogbookConstants:
    fetch_logbooks_payload = {
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
        "project_id": EnvironmentConstants.project_id,
        "project_type": AutomationConstants.project_type,
        "tz": EnvironmentConstants.tz,
        "language": AutomationConstants.language
    }

    logbook_filter_model = {
            "logbook_name": {
              "filterType": "text",
              "type": "equals",
              "filter": ""
            }
          }

    fetch_specifications_payload = {
        "template_category_id": "template_category_102",
        "project_id": EnvironmentConstants.project_id,
        "project_type": AutomationConstants.project_type,
        "tz": EnvironmentConstants.tz,
        "language": AutomationConstants.language
    }

    # categories and trigger payload same
    fetch_categories_payload = {
        "project_id": EnvironmentConstants.project_id,
        "project_type": AutomationConstants.project_type,
        "tz": EnvironmentConstants.tz,
        "language": AutomationConstants.language
    }

    fetch_project_templates_payload = {
        "project_id": EnvironmentConstants.project_id,
        "project_type": AutomationConstants.project_type,
        "tz": EnvironmentConstants.tz,
        "language": AutomationConstants.language,
        "pageType": "logbook"
    }

    logbook_mapping = {
        'logbook name': 'logbook_name',
        'description': 'description',
        'category': 'logbook_category',
        'business process tags': 'business_process_tags',
        'card color': 'card_color',
        'workflow': 'workflow',
        'task creation step': 'step_id',
        'associate hierarchy': 'associate_hierarchy',
        'hierarchy level': 'siteHierarchyLevel',
        'site': 'l1',
        'section': 'l2',
        'department': 'l3',
        'line': 'l4',
        'equipment': 'l5',
        'l1': 'l1',
        'l2': 'l2',
        'l3': 'l3',
        'l4': 'l4',
        'l5': 'l5',
        'assets': 'ast',
        'pre-approval reviewer': 'reviewers',
        'pre approval reviewer': 'reviewers',
        'reviewers': 'reviewers',
        'enable e-sign': 'e_sign',
        'enable e_sign': 'e_sign',
        'enable esign': 'e_sign',
        'e-sign': 'e_sign',
        'e_sign': 'e_sign',
        'esign': 'e_sign'
    }

    fetch_logbook_details_payload = {
        "logbook_id": "VNFV6mnV7QvWPZA2eg3gjQ",
        "logbook_name": "Sample Logbook",
        "logbook_version": 1,
        "status": "in_progress",
        "project_id": EnvironmentConstants.project_id,
        "project_type": AutomationConstants.project_type,
        "tz": EnvironmentConstants.tz,
        "language": AutomationConstants.language,
}
