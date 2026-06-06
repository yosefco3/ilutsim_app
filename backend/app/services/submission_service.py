"""
SubmissionService — business logic for weekly constraint submissions.
"""

import json
import logging
import uuid
from datetime import date
from typing import Optional

from app.constants import SubmissionStatus, WeekStatus
from app.exceptions import UserNotFoundException, WeekLockedException
from app.models.weekly_submission import WeeklySubmission
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.schedule_week_repository import ScheduleWeekRepository
from app.schemas.submission_schemas import SubmissionCreate, SubmissionResponse
from app.services.deviation_service import DeviationService

logger = logging.getLogger("ilutzim")


class SubmissionService:
    """Orchestrates weekly constraint submission flow."""

    def __init__(
        self,
        submission_repo: SubmissionRepository,
        user_repo: UserRepository,
        week_repo: ScheduleWeekRepository,
        deviation_service: DeviationService,
    ) -> None:
        self._submission_repo = submission_repo
        self._user_repo = user_repo
        self._week_repo = week_repo
        self._deviation_service = deviation_service

    async def create_submission(
        self, data: SubmissionCreate, *, override_lock: bool = False
    ) -> SubmissionResponse:
        """
        Submit constraints for a specific week.
        Validates week is open (unless override_lock=True).
        Detects deviations from thresholds.
        """
        # Validate user exists
        user = await self._user_repo.get_by_id(data.user_id)
        if user is None:
            raise UserNotFoundException()

        # Validate week is open
        week = await self._week_repo.get_by_id(data.week_id)
        if week is None:
            raise UserNotFoundException()

        if week.status != WeekStatus.OPEN and not override_lock:
            raise WeekLockedException()

        # Check deviations
        constraints_dict = data.constraints if isinstance(data.constraints, dict) else data.constraints
        has_deviation = self._deviation_service.check_deviations(
            user=user,
            constraints=constraints_dict,
        )

        # Determine status
        if has_deviation:
            status = SubmissionStatus.SUBMITTED_VARIANCE
        else:
            status = SubmissionStatus.SUBMITTED

        # Create or update submission
        existing = await self._submission_repo.get_submission(
            data.user_id, data.week_id
        )
        if existing:
            existing.constraints = json.dumps(constraints_dict) if not isinstance(constraints_dict, str) else constraints_dict
            existing.status = status
            updated = await self._submission_repo.update(existing)
            logger.info(f"Submission updated: user={data.user_id}, week={data.week_id}, status={status}")
            return SubmissionResponse.model_validate(updated)

        submission = WeeklySubmission(
            user_id=data.user_id,
            week_id=data.week_id,
            constraints=json.dumps(constraints_dict) if not isinstance(constraints_dict, str) else constraints_dict,
            status=status,
        )
        created = await self._submission_repo.create(submission)
        logger.info(f"Submission created: user={data.user_id}, week={data.week_id}, status={status}")
        return SubmissionResponse.model_validate(created)

    async def get_submissions_for_week(
        self, week_id: uuid.UUID
    ) -> list[SubmissionResponse]:
        """Return all submissions for a given week."""
        submissions = await self._submission_repo.get_submissions_for_week(week_id)
        return [SubmissionResponse.model_validate(s) for s in submissions]

    async def get_submission(
        self, user_id: uuid.UUID, week_id: uuid.UUID
    ) -> Optional[SubmissionResponse]:
        """Return a single submission by user + week."""
        sub = await self._submission_repo.get_submission(user_id, week_id)
        if sub is None:
            return None
        return SubmissionResponse.model_validate(sub)

    async def mark_auto_absence(self, week_id: uuid.UUID) -> int:
        """
        Mark all active users who haven't submitted as auto-absence.
        Returns count of marked users.
        """
        active_users = await self._user_repo.get_active_users()
        marked = 0
        for user in active_users:
            existing = await self._submission_repo.get_submission(
                user.id, week_id
            )
            if existing is None:
                sub = WeeklySubmission(
                    user_id=user.id,
                    week_id=week_id,
                    constraints="{}",
                    status=SubmissionStatus.AUTO_ABSENCE,
                )
                await self._submission_repo.create(sub)
                marked += 1
        logger.info(f"Auto-absence marked: {marked} users for week {week_id}")
        return marked