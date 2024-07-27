import logging
import os
from fastapi import APIRouter, UploadFile, File, Form
from starlette.responses import FileResponse
from scripts.config import Services
from scripts.core.handlers.new_datagrid_handler import CreateJson

logger = logging.getLogger(Services.PROJECT_NAME)
UPLOAD_DIR = "assets"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
datagrid = APIRouter(prefix="/json")

create_json = CreateJson()


@datagrid.post("/new_datagrid", tags=["1.Datagrid"])
async def datagrid_logbook(sheet_name: str = Form(...),
                           output_filename: str = Form(...), file: UploadFile = File(...)):
    """


    :param file: Excel file of logbook
    :param sheet_name: name of sheet
    :param output_filename: name of json file
    :return: json for the given step
    """
    logger.info(f'service started in creating json for datagrid {sheet_name}')
    try:
        logger.info("writing the excel file")
        # type_row = type_row - 1
        file_content = await file.read()
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        response = create_json.get_datagrid(file_path, sheet_name, output_filename)
        json_file = f'assets/{output_filename}.json'
        if response and os.path.exists(json_file):
            return FileResponse(json_file,
                                headers={"Content-Disposition": f"attachment; filename={output_filename}.json"},
                                media_type="application/json")
        else:
            return {"message": "Json error"}

    except Exception as e:
        logger.error(f'error while reading excel file {e}')
        return "error"
