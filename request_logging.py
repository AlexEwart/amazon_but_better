import json
import logging as std_logging
from datetime import UTC, datetime
from typing import Any

from google.cloud import logging as cloud_logging

_cloud_logger = None


def log_request(
    *,
    user_id: str | None,
    cart: Any,
    endpoint: str,
    method: str,
    correlation_id: str,
) -> None:
    """Write the requested pipe-delimited fields to Cloud Logging and app logs."""
    global _cloud_logger

    cart_text = json.dumps(cart, separators=(",", ":"), default=str) if cart is not None else "-"
    entry = " | ".join(
        (
            datetime.now(UTC).isoformat(),
            user_id or "-",
            cart_text,
            endpoint,
            method,
            correlation_id,
        )
    )
    std_logging.getLogger("request_audit").info(entry)

    try:
        if _cloud_logger is None:
            _cloud_logger = cloud_logging.Client().logger("service-requests")
        _cloud_logger.log_text(entry)
    except Exception:
        # Keep local development and API responses working when ADC or Cloud
        # Logging is unavailable; the same entry remains in application logs.
        std_logging.getLogger("request_audit").exception("Cloud Logging write failed")
