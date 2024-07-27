from scripts.constants import EnvironmentConstants

class BaseURLPaths:
    step_module = '/workflow-mt/step'
    auth_endpoint = f'{EnvironmentConstants.base_path}{EnvironmentConstants.auth_endpoint}?project_id={EnvironmentConstants.project_id}'
    workflow = '/workflow-mt'
    workflow_module = f'{workflow}/workflow'
    ilens_module = '/ilens_api/ilens_config'
    hierarchy_module = '/hry/hierarchy'


class UTCoreStepsAPI:
    validate_step = f'{BaseURLPaths.step_module}/validate'
    create_step = f'{BaseURLPaths.step_module}/save'
    fetch_step = f'{BaseURLPaths.step_module}/fetch_step_data'


class UTCoreWorkflowAPI:
    fetch_workflow = f'{BaseURLPaths.workflow_module}/list_workflow_data'
    fetch_workflow_dropdowns = f'{BaseURLPaths.workflow_module}/load/options'
    save_workflow = f'{BaseURLPaths.workflow_module}/save'
    fetch_params = f'{BaseURLPaths.workflow_module}/get'


class UTCoreLogbooksAPI:
    fetch_logbooks = f'{BaseURLPaths.workflow}/list_logbook_data'
    fetch_specifications = f'{BaseURLPaths.workflow_module}/fetch'
    fetch_categories = f'{BaseURLPaths.workflow}/task/categories/get'
    fetch_templates = f'{BaseURLPaths.ilens_module}/project_templates'
    fetch_logbook_trigger = f'{BaseURLPaths.workflow}/load/logbook_options'
    fetch_hierarchy_dropdown = f'{BaseURLPaths.hierarchy_module}/dropdown'
    save_logbook = f'{BaseURLPaths.workflow}/logbook/save'
    fetch_logbook_details = f'{BaseURLPaths.workflow}/logbook/get'

