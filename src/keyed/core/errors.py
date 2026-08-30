from keyed.core.rate_limit import RateLimitDecision


class InvalidAPIKeyError(Exception):
    """Raised when a credential cannot be authenticated."""


class RateLimitExceededError(Exception):
    """Raised when an authenticated key has exhausted its current window."""

    def __init__(self, decision: RateLimitDecision) -> None:
        super().__init__("API key rate limit exceeded")
        self.decision = decision
