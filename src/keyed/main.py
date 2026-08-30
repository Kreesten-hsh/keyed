from fastapi import FastAPI

from keyed.api.routes import create_router
from keyed.core.authenticator import SQLAlchemyAPIKeyAuthenticator
from keyed.core.config import Settings
from keyed.db.session import create_session_factory
from keyed.fastapi import Authenticator, KeyedAuth


def create_app(authenticator: Authenticator | None = None) -> FastAPI:
    if authenticator is None:
        settings = Settings()  # type: ignore[call-arg]
        session_factory = create_session_factory(settings.database_url)
        authenticator = SQLAlchemyAPIKeyAuthenticator(session_factory)

    app = FastAPI(title="keyed", version="0.1.0")
    app.include_router(create_router(KeyedAuth(authenticator)))
    return app
