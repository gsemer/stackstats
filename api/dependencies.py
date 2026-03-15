from fastapi import Request

from application.services.stackexchange import StackExchangeService


def get_service(request: Request) -> StackExchangeService:
    """
    Dependency to retrieve the StackExchangeService instance.

    Args:
        request: The incoming FastAPI request containing the app state.

    Returns:
        The StackExchangeService instance initialized during app startup.
    """
    return request.app.state.stack_service
