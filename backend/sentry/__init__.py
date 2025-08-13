import sentry_sdk

from backend.core.logger import get_logger


logger = get_logger(__name__)


def init_sentry() -> None:
    """Инициализирует Sentry"""
    sentry_sdk.init(
        dsn="https://6bf46ea00cee3e9aa2503e6dc9791206@o4509836240289792.ingest.de.sentry.io/4509836249792592",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )
    logger.info("Sentry initialized")


__all__ = ["init_sentry"]
