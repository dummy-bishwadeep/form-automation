from scripts.constants import EnvironmentConstants


class BaseURLPaths:
    step_module = '/workflow-mt/step'
    auth_endpoint = f'{EnvironmentConstants.base_path}{EnvironmentConstants.auth_endpoint}?project_id={EnvironmentConstants.project_id}'
    # form_module = "/form-mt/render/form"
    # ilens_config_module = '/ilens_api/ilens_config'
    # form_stage_list = '/form-mt/stage/list'


class UTCoreStepsAPI:
    validate_step = f'{BaseURLPaths.step_module}/validate'
    create_step = f'{BaseURLPaths.step_module}/save'
    fetch_step = f'{BaseURLPaths.step_module}/fetch_step_data'
    validate_step = f'{BaseURLPaths.step_module}/validate'



