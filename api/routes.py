import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime

from schemas.response import StackStatsResponse
from application.services.stackexchange import StackExchangeService
from api.dependencies import get_service


router = APIRouter()

logger = logging.getLogger("stackexchange_api")


@router.get(
        "/stackstats", 
        summary="Get StackExchange statistics within a datetime range"
)
async def stackstats(
    since: datetime = Query(..., description="Start datetime YYYY-MM-DD HH:MM:SS", examples="2016-03-09T10:00:00"),
    until: datetime = Query(..., description="End datetime YYYY-MM-DD HH:MM:SS", examples="2016-03-09T11:00:00"),
    service: StackExchangeService = Depends(get_service),
) -> StackStatsResponse:
    """
    Retrieve StackExchange statistics for a given time range.

    Args:
        since (datetime): Start of the range.
        until (datetime): End of the range.
        service: Injected StackExchangeService.

    Returns:
        dict: Statistics including accepted answers, average scores, and top comments.
    """
    logger.info("Received request for stackstats: since=%s, until=%s", since, until)

    if since > until:
        logger.warning("Invalid date range: 'since' is after 'until'")
        raise HTTPException(status_code=400, detail="'since' must be before 'until'")

    # Convert datetime to Unix timestamps
    since_ts = int(since.timestamp())
    until_ts = int(until.timestamp())

    result = await service.stackstats(since_ts, until_ts)
    logger.info("Statistics were computed successfully for range %s - %s", since, until)
    
    return StackStatsResponse(**result)
