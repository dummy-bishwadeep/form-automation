import os
import time
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form
from starlette.responses import FileResponse
from scripts.config.description import Description
from scripts.core.handlers.form_handler import FormHandler
from scripts.logging.logger import logger

UPLOAD_DIR = "assets"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
form_router = APIRouter(prefix="/json")


# ----------------------------------------------------------------------------------------------------------------------

@form_router.post("/generate_form", tags=["2. Generate Form"], description=Description.generate_form_desc)
async def generate_form(sheet_name: str = Form(...),
                        file: UploadFile = File(...)):
    """
    :param sheet_name:
    :param file:
    :return:
    """
    try:
        logger.info(f'service started in creating step form json {sheet_name}')
        file_content = await file.read()
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_content)

        current_ts = int(time.time())
        merge_obj = FormHandler(file_path=file_path,
                                sheet_name=sheet_name,
                                current_ts=current_ts)
        response = merge_obj.generate_form_json()
        sheet_name = f'{sheet_name}_{current_ts}'
        json_file = f'assets/{sheet_name}.json'
        if response and os.path.exists(json_file):
            return FileResponse(json_file,
                                headers={"Content-Disposition": f"attachment; filename={sheet_name}.json"},
                                media_type="application/json")
        else:
            return {"message": "Json error"}
    except Exception as e:
        logger.exception(f"exception from generate form json logic {e}")
