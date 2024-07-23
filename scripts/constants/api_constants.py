from scripts.constants import EnvironmentConstants


class BaseURLPaths:
    step_module = '/workflow-mt/step'
    auth_endpoint = f'{EnvironmentConstants.base_path}{EnvironmentConstants.auth_endpoint}?project_id={EnvironmentConstants.project_id}'
    workflow_module = '/workflow-mt/workflow'


class UTCoreStepsAPI:
    validate_step = f'{BaseURLPaths.step_module}/validate'
    create_step = f'{BaseURLPaths.step_module}/save'
    fetch_step = f'{BaseURLPaths.step_module}/fetch_step_data'


class UTCoreWorkflowAPI:
    fetch_workflow = f'{BaseURLPaths.workflow_module}/list_workflow_data'
    fetch_workflow_dropdowns = f'{BaseURLPaths.workflow_module}/load/options'
    save_workflow = f'{BaseURLPaths.workflow_module}/save'
    fetch_params = f'{BaseURLPaths.workflow_module}/get'



