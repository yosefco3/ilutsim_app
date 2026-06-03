"""
DeviationService — pure-logic threshold deviation detection.
No I/O — operates on in-memory data only.
"""

import logging
from typing import Any

from app.models.user import User

logger = logging.getLogger("ilutzim")


class DeviationService:
    """
    Detects whether a constraint submission deviates from a user's thresholds.
    Pure business logic — no DB access.
    """

    def check_deviations(self, user: User, constraints: Any) -> bool:
        """
        Return True if the submission deviates from the user's minimum thresholds.

        Constraints is expected to be a dict (or JSON string) mapping shift types
        to counts, e.g. {"total": 5, "night": 2, "evening": 1}.

        A deviation occurs when the user's offered count is *less than* their
        configured minimum threshold for any shift category.
        """
        if isinstance(constraints, str):
            import json
            try:
                constraints = json.loads(constraints)
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Invalid constraints JSON for user {user.id}")
                return False

        if not isinstance(constraints, dict):
            logger.warning(f"Constraints not a dict for user {user.id}")
            return False

        deviations: list[str] = []

        if user.min_total_shifts > 0:
            offered = constraints.get("total", 0)
            if offered < user.min_total_shifts:
                deviations.append(
                    f"total: offered={offered}, min={user.min_total_shifts}"
                )

        if user.min_night_shifts > 0:
            offered = constraints.get("night", 0)
            if offered < user.min_night_shifts:
                deviations.append(
                    f"night: offered={offered}, min={user.min_night_shifts}"
                )

        if user.min_evening_shifts > 0:
            offered = constraints.get("evening", 0)
            if offered < user.min_evening_shifts:
                deviations.append(
                    f"evening: offered={offered}, min={user.min_evening_shifts}"
                )

        if deviations:
            logger.info(
                f"Deviation detected for user {user.id}: {'; '.join(deviations)}"
            )
            return True

        return False