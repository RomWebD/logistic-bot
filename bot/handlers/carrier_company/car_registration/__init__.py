# bot/handlers/carrier_company/car_registration/__init__.py

from .entry_point import router as entry_router
from .steps import router as steps_router
from .choose_loading import router as loading_router
from .summary import router as summary_router
from .edit import router as edit_router

routers = [
    entry_router,
    steps_router,
    loading_router,
    summary_router,
    edit_router,
]
