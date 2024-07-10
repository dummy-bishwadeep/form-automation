from fastapi import APIRouter

from scripts.services import logbooks, table, new_datagrid

router = APIRouter()
router.include_router(logbooks.router)
router.include_router(table.table)
router.include_router(new_datagrid.datagrid)
