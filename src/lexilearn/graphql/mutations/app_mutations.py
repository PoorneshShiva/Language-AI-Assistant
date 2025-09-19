import strawberry
from typing import Optional, List, cast
import datetime
from strawberry.scalars import JSON

from lexilearn.database import Database
from lexilearn.graphql.types.object_types import (
    AppUser, UserSettings, WordIndex, UserWord, PracticeEvent
)
from lexilearn.graphql.types.enums import Level, ItemType, LearnStyle, Confidence, LearnStatus

@strawberry.input
class UserSettingsInput:
    level: Optional[Level] = None
    daily_goal: Optional[int] = None
    style: Optional[LearnStyle] = None
    review_enabled: Optional[bool] = None

@strawberry.input
class PracticeEventInput:
    session_id: Optional[strawberry.ID] = None
    user_id: strawberry.ID
    word_uid: strawberry.ID
    prompt_id: Optional[str] = None
    level_at_time: Level
    confidence: Optional[Confidence] = None
    expected: Optional[str] = None
    answer: Optional[str] = None
    correct: Optional[bool] = None
    issues: Optional[JSON] = None
    normalized: Optional[JSON] = None

@strawberry.type
class AppMutation:
    @strawberry.mutation
    def create_user(self, info: strawberry.Info, email: str, display_name: Optional[str] = None) -> AppUser:
        db = cast(Database, info.context["db"])
        user_id = db.add_app_user({"email": email, "display_name": display_name})
        user_data = db.get_app_user(user_id)
        return AppUser(**user_data)

    @strawberry.mutation
    def update_user_settings(self, info: strawberry.Info, user_id: strawberry.ID, settings: UserSettingsInput) -> UserSettings:
        db = cast(Database, info.context["db"])
        updated_settings = db.update_user_settings(
            str(user_id),
            level=settings.level.value if settings.level else None,
            daily_goal=settings.daily_goal,
            style=settings.style.value if settings.style else None,
            review_enabled=settings.review_enabled
        )
        return UserSettings(**updated_settings)

    @strawberry.mutation
    def detect_words(self, info: strawberry.Info, tokens: List[str]) -> List[WordIndex]:
        db = cast(Database, info.context["db"])
        detected_words = db.detect_words(tokens)
        return [WordIndex(**word) for word in detected_words]

    @strawberry.mutation
    def random_word(self, info: strawberry.Info, user_id: strawberry.ID) -> Optional[WordIndex]:
        db = cast(Database, info.context["db"])
        random_word_data = db.random_word(str(user_id))
        if random_word_data:
            return WordIndex(**random_word_data)
        return None

    @strawberry.mutation
    def evaluate_practice_event(self, info: strawberry.Info, event_data: PracticeEventInput) -> PracticeEvent:
        db = cast(Database, info.context["db"])
        event_id = db.evaluate_practice_event({
            "session_id": str(event_data.session_id) if event_data.session_id else None,
            "user_id": str(event_data.user_id),
            "word_uid": str(event_data.word_uid),
            "prompt_id": event_data.prompt_id,
            "level_at_time": event_data.level_at_time.value,
            "confidence": event_data.confidence.value if event_data.confidence else None,
            "expected": event_data.expected,
            "answer": event_data.answer,
            "correct": event_data.correct,
            "issues": event_data.issues,
            "normalized": event_data.normalized
        })
        retrieved_event = db.get_practice_event(event_id)
        return PracticeEvent(**retrieved_event)

    @strawberry.mutation
    def update_confidence(self, info: strawberry.Info, user_id: strawberry.ID, word_uid: strawberry.ID, confidence: Confidence) -> UserWord:
        db = cast(Database, info.context["db"])
        # This is a simplified SRS logic. In a real app, interval_days, stability would be calculated.
        # For now, just update status and last_result.
        status = LearnStatus.LEARNING.value
        if confidence == Confidence.EASY:
            status = LearnStatus.COMPLETED.value

        updated_user_word = db.update_user_word_status(
            str(user_id),
            str(word_uid),
            status=status,
            last_result=confidence.value
        )
        return UserWord(**updated_user_word)

    @strawberry.mutation
    def complete_word(self, info: strawberry.Info, user_id: strawberry.ID, word_uid: strawberry.ID) -> UserWord:
        db = cast(Database, info.context["db"])
        updated_user_word = db.update_user_word_status(
            str(user_id),
            str(word_uid),
            status=LearnStatus.COMPLETED.value,
            due_at=None
        )
        return UserWord(**updated_user_word)

    @strawberry.mutation
    def review_again(self, info: strawberry.Info, user_id: strawberry.ID, word_uid: strawberry.ID) -> UserWord:
        db = cast(Database, info.context["db"])
        updated_user_word = db.update_user_word_status(
            str(user_id),
            str(word_uid),
            status=LearnStatus.QUEUED.value,
            due_at=datetime.datetime.now().isoformat() # Set due_at to now for immediate review
        )
        return UserWord(**updated_user_word)

    @strawberry.mutation
    def ignore_word(self, info: strawberry.Info, user_id: strawberry.ID, word_uid: strawberry.ID) -> UserWord:
        db = cast(Database, info.context["db"])
        updated_user_word = db.update_user_word_status(
            str(user_id),
            str(word_uid),
            status=LearnStatus.IGNORED.value,
            due_at=None
        )
        return UserWord(**updated_user_word)

    @strawberry.mutation
    def unignore_word(self, info: strawberry.Info, user_id: strawberry.ID, word_uid: strawberry.ID) -> UserWord:
        db = cast(Database, info.context["db"])
        updated_user_word = db.update_user_word_status(
            str(user_id),
            str(word_uid),
            status=LearnStatus.NEW.value,
            due_at=None
        )
        return UserWord(**updated_user_word)
