import os
import time
from typing import Optional

from fastapi import APIRouter, Depends, Form
from starlette.responses import FileResponse

from scripts.config.description import Description
from scripts.core.handlers.template_handler import TemplateHandler
from scripts.core.schemas.template_model import HierarchyLevelEnum
from scripts.utils.security_utils.security import verify_cookie

UPLOAD_DIR = "assets"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
template_router = APIRouter()

current_file_path = os.path.abspath(__file__)
asset_path = current_file_path

for _ in range(3):
    asset_path = os.path.dirname(asset_path)
asset_path = os.path.join(asset_path, UPLOAD_DIR)

# ----------------------------------------------------------------------------------------------------------------------


@template_router.post("/generate_template", tags=["1. Automation Templates"],
                      description=Description.generate_template_desc)
async def automation_template(
        login_token: dict = Depends(verify_cookie),
        step_count: int = Form(1, description='Number of Steps in a Logbook'),
        step_creation: Optional[bool] = Form(False, description='Include Task Creation Step'),
        hierarchy_level: HierarchyLevelEnum = Form('Site', description='Hierarchy Level'),
):
    """
    :param encrypt_payload:
    :param login_token:
    :return:
    """
    try:
        ts = str(int(time.time()))
        template_handler = TemplateHandler(login_token=login_token,
                                           step_count=step_count,
                                           step_creation=step_creation,
                                           hierarchy_level=hierarchy_level,
                                           asset_path=asset_path,
                                           ts=ts)

        success_status, response = template_handler.generate_automation_template()

        file_path = os.path.join(asset_path, f'AutomationTemplate_{ts}.xlsx')
        if success_status and os.path.exists(file_path):
            return FileResponse(file_path,
                                headers={"Content-Disposition": f"attachment; filename=AutomationTemplate_{ts}.xlsx"},
                                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        return response
    except Exception as e:
        raise e