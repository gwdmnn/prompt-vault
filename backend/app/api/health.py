import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from app.api.deps import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(session: Session = Depends(get_db)):
    db_status = "up"
    try:
        session.exec(text("SELECT 1"))  # type: ignore[call-overload]
    except Exception:
        logger.exception("Database health check failed")
        db_status = "down"

    status = "healthy" if db_status == "up" else "unhealthy"
    status_code = 200 if status == "healthy" else 503

    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status,
            "checks": {"database": db_status},
            "version": settings.API_VERSION,
        },
    )
