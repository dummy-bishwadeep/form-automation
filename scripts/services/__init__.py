from fastapi import APIRouter

from scripts.services import logbooks, table, new_datagrid, form_services, template_services

router = APIRouter()
router.include_router(template_services.template_router)
router.include_router(form_services.form_router)
# router.include_router(logbooks.router)
# router.include_router(form_services.form_router)
# router.include_router(table.table)
# router.include_router(new_datagrid.datagrid)
