import os
from fastapi import APIRouter, UploadFile, File, Form
from starlette.responses import FileResponse
from scripts.config.description import Description
from scripts.core.handlers.table_merge import TableMergeHandler
from scripts.logging.logger import logger

UPLOAD_DIR = "assets"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
table = APIRouter(prefix="/json")


# ----------------------------------------------------------------------------------------------------------------------
# new API
merge_obj = TableMergeHandler()


@table.post("/merged_table", tags=["4. Merging Table"], description=Description.step_with_logic)
async def merge_table(sheet_name: str = Form(...), file: UploadFile = File(...)):
    """
    :param sheet_name:
    :param file:
    :return:
    """
    try:
        logger.info(f'service started in creating steps for table with calculation {sheet_name}')
        file_content = await file.read()
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        response = merge_obj.merge_table(file_path, sheet_name)
        json_file = f'assets/{sheet_name}.json'
        if response and os.path.exists(json_file):
            return FileResponse(json_file,
                                headers={"Content-Disposition": f"attachment; filename={sheet_name}.json"},
                                media_type="application/json")
        else:
            return {"message": "Json error"}
    except Exception as e:
        logger.exception(f"exception from table with logic {e}")
