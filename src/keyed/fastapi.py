from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol

from fastapi import Depends, HTTPException, Request, Response, status

from keyed.core.errors import InvalidAPIKeyError, RateLimitExceededError
from keyed.core.models import AuthenticatedAPIKey
from keyed.core.rate_limit import RateLimitDecision
from keyed.core.scopes import has_required_scopes


class Authenticator(Protocol):
    async def authenticate(
        self,
        plaintext: str,
    ) -> tuple[AuthenticatedAPIKey, RateLimitDecision]: ...


class KeyedAuth:
    def __init__(self, authenticator: Authenticator, *, header_name: str = "X-API-Key") -> None:
        self._authenticator = authenticator
        self._header_name = header_name

    async def __call__(self, request: Request, response: Response) -> AuthenticatedAPIKey:
        plaintext = request.headers.get(self._header_name)
        if plaintext is None:
            raise _invalid_key_response()

        try:
            principal, decision = await self._authenticator.authenticate(plaintext)
        except InvalidAPIKeyError as exc:
            raise _invalid_key_response() from exc
        except RateLimitExceededError as exc:
            decision = exc.decision
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API key rate limit exceeded",
                headers={
                    "Retry-After": str(decision.retry_after),
                    "X-RateLimit-Limit": str(decision.limit),
                    "X-RateLimit-Remaining": str(decision.remaining),
                },
            ) from exc

        response.headers["X-RateLimit-Limit"] = str(decision.limit)
        response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
        return principal

    def require_scopes(
        self,
        *required_scopes: str,
    ) -> Callable[..., Awaitable[AuthenticatedAPIKey]]:
        async def dependency(
            principal: AuthenticatedAPIKey = Depends(self),
        ) -> AuthenticatedAPIKey:
            if not has_required_scopes(principal.scopes, required_scopes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient API key scope",
                )
            return principal

        return dependency


def _invalid_key_response() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "ApiKey"},
    )
