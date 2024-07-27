import os
import time
from typing import Optional

import openpyxl
from fastapi import APIRouter, UploadFile, File, Form, Depends
from scripts.config.description import Description
from scripts.core.handlers.form_handler import FormHandler
from scripts.core.handlers.logbook_handler import LogbookHandler
from scripts.core.handlers.meta_data import MetaData
from scripts.core.handlers.workflow_handler import WorkflowHandler
from scripts.logging.logger import logger
from scripts.utils.security_utils.security import verify_cookie

UPLOAD_DIR = "assets"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
form_router = APIRouter()


# ----------------------------------------------------------------------------------------------------------------------

@form_router.post("/automate_logbook", tags=["2. Automation Services"], description=Description.generate_form_desc)
async def initiate_automation(
        login_token: dict = Depends(verify_cookie),
        encrypt_payload: Optional[bool] = Form(False, description='Encrypt Payload'),
        file: UploadFile = File(...)
):
    """
    :param encrypt_payload:
    :param login_token:
    :param file:
    :return:
    """
    try:
        sheet_name = "Metadata"
        logger.info(f'service started in creating step form json {sheet_name}')
        file_content = await file.read()
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        current_ts = int(time.time())

        # go one step back -> services
        current_file_path = os.path.abspath(__file__)
        project_parent_path = os.path.dirname(current_file_path)
        # go one step back -> scripts
        project_parent_path = os.path.dirname(project_parent_path)
        component_json_path = os.path.join(project_parent_path, 'utils/component.json')

        step_data_list = MetaData(file_path=file_path, component_json_path=component_json_path).automate_step()
        response_messages = ''
        updated_step_data = []

        # automate steps
        task_creation_step = ''
        selected_step_version = 1
        for step_data in step_data_list:
            sheet_name = step_data["sheet"]
            form_handler = FormHandler(login_token=login_token,
                                       encrypt_payload=encrypt_payload,
                                       file_path=file_path,
                                       component_json_path=component_json_path,
                                       sheet_name=sheet_name,
                                       current_ts=current_ts,
                                       step_data=step_data,
                                       response_messages=response_messages)
            response, response_messages = form_handler.generate_form_json()
            step_category = response.get('step_category', '')
            if step_category in ['step_category_101', 'task creation step', 'Task Creation Step']:
                task_creation_step = response.get('step_id', '')
                selected_step_version = response.get('step_version', 1)
            updated_step_data.append(response)

        # automate workflow
        workflow_obj = WorkflowHandler(workbook=openpyxl.load_workbook(file_path, data_only=True),
                                       encrypt_payload=encrypt_payload,
                                       login_token=login_token,
                                       step_data=updated_step_data,
                                       response_message=response_messages)
        workflow_data, response_messages = workflow_obj.automate_workflow()

        # automate logbook
        workflow_data.update({'step_id': task_creation_step,
                              'step_version': selected_step_version})
        logbook_obj = LogbookHandler(workbook=openpyxl.load_workbook(file_path, data_only=True),
                                     encrypt_payload=encrypt_payload,
                                     login_token=login_token,
                                     workflow_data=workflow_data,
                                     response_message=response_messages)
        response_messages = logbook_obj.automate_logbook()
        return {'logs': [each for each in response_messages.strip().split('\n')]}

        # # sheet_name = f'{sheet_name}_{current_ts}'
        # # json_file = f'assets/{sheet_name}.json'
        # if response and os.path.exists(json_file):
        #     # return FileResponse(json_file,
        #     #                     headers={"Content-Disposition": f"attachment; filename={sheet_name}.json"},
        #     #                     media_type="application/json")
        #     return {'message': 'Step updated successfully'}
        # else:
        #     return {"message": "Failed to update step"}
    except Exception as e:
        logger.exception(f"exception from generate form json logic {e}")
