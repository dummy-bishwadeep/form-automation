import os
import time
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Request, Depends
from pathlib import Path
from starlette.responses import FileResponse, JSONResponse
from scripts.config.description import Description
from scripts.core.handlers.form_handler import FormHandler
from scripts.core.handlers.meta_data import MetaData
from scripts.core.schemas.step_models import MenuPlacementDropdown, StepCategoryDropdown
from scripts.logging.logger import logger
from scripts.constants.step_constants import StepConstants
from scripts.utils.security_utils.security import verify_cookie

UPLOAD_DIR = "assets"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
form_router = APIRouter(prefix="/json")


# ----------------------------------------------------------------------------------------------------------------------

@form_router.post("/generate_form", tags=["1. Generate Form"], description=Description.generate_form_desc)
async def generate_form(
        login_token: dict = Depends(verify_cookie),
        encrypt_payload: Optional[bool] = Form(False, description='Encrypt Payload'),
        file: UploadFile = File(...)
):
    """
    :param sheet_name:
    :param file:
    :return:
    """
    try:
        sheet_name = "MetaData"
        logger.info(f'service started in creating step form json {sheet_name}')
        file_content = await file.read()
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        current_ts = int(time.time())
        step_data = MetaData(file_path=file_path, sheet_name=sheet_name, current_ts=current_ts).automate_step()
        #
        # step_name = step_data["step_name"]
        # display_title = step_data["display_title"]
        # description = step_data["description"]
        # step_sub_categroy = step_data["step_sub_categroy"]
        # validate_form = step_data["validate_form"]
        # auto_save = step_data["auto_save"]
        sheet_name = step_data["sheet_name"]
        #
        # menu_placement = step_data["menu_placement"]
        # menu_placement = MenuPlacementDropdown(menu_placement)
        #
        # step_category = step_data["step_category"]
        # step_category = StepCategoryDropdown(step_category)
        #
        #
        # step_meta_data = {
        #     'step_name': step_name,
        #     'display_title': display_title,
        #     'description': description,
        #     'step_category': step_category.name,
        #     'step_sub_category': step_sub_categroy if step_sub_categroy else None,
        #     'menu_placement': menu_placement.name,
        #     'validate_form': validate_form,
        #     'auto_save': auto_save,
        #     'sheet_name': sheet_name,
        # }
        form_handler = FormHandler(login_token=login_token,
                                   encrypt_payload=encrypt_payload,
                                   file_path=file_path,
                                   sheet_name=sheet_name,
                                   current_ts=current_ts,
                                   step_data=step_data)
        response = form_handler.generate_form_json()
        # # sheet_name = f'{sheet_name}_{current_ts}'
        # # json_file = f'assets/{sheet_name}.json'
        return response
        # if response and os.path.exists(json_file):
        #     # return FileResponse(json_file,
        #     #                     headers={"Content-Disposition": f"attachment; filename={sheet_name}.json"},
        #     #                     media_type="application/json")
        #     return {'message': 'Step updated successfully'}
        # else:
        #     return {"message": "Failed to update step"}
    except Exception as e:
        logger.exception(f"exception from generate form json logic {e}")
