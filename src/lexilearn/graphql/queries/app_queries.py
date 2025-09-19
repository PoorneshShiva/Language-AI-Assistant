import strawberry
from typing import Optional, List
from lexilearn.database import Database
from lexilearn.graphql.types.object_types import (
    AppUser, UserSettings, WordIndex, UserWord, PracticeSession, PracticeEvent,
    Prompt, PromptWord, UserStatsDaily, TotalStatsType, NounHintType
)
from lexilearn.graphql.types.enums import ItemType, Level

@strawberry.type
class AppQuery:
    @strawberry.field
    def get_user(self, info: strawberry.Info, user_id: strawberry.ID) -> Optional[AppUser]:
        db = Database(info.context["conn"])
        user_data = db.get_app_user(str(user_id))
        if user_data:
            return AppUser(**user_data)
        return None

    @strawberry.field
    def get_user_settings(self, info: strawberry.Info, user_id: strawberry.ID) -> Optional[UserSettings]:
        db = Database(info.context["conn"])
        settings_data = db.get_user_settings(str(user_id))
        if settings_data:
            return UserSettings(**settings_data)
        return None

    @strawberry.field
    def list_words(self, info: strawberry.Info, item_type: Optional[ItemType] = None, item_ids: Optional[List[str]] = None) -> List[WordIndex]:
        db = Database(info.context["conn"])
        words_data = db.list_words(item_type.value if item_type else None, item_ids)
        return [WordIndex(**word) for word in words_data]

    @strawberry.field
    def get_prompts(
        self,
        info: strawberry.Info,
        item_type: Optional[ItemType] = None,
        item_id: Optional[str] = None,
        level: Optional[Level] = None,
        count: Optional[int] = None
    ) -> List[Prompt]:
        db = Database(info.context["conn"])
        prompts_data = db.get_prompts(
            item_type.value if item_type else None,
            item_id,
            level.value if level else None,
            count
        )
        return [Prompt(**prompt) for prompt in prompts_data]

    @strawberry.field
    def practice_queue(self, info: strawberry.Info, user_id: strawberry.ID, limit: Optional[int] = None) -> List[UserWord]:
        db = Database(info.context["conn"])
        queue_data = db.practice_queue(str(user_id), limit)
        return [UserWord(**item) for item in queue_data]

    @strawberry.field
    def completed_list(self, info: strawberry.Info, user_id: strawberry.ID) -> List[UserWord]:
        db = Database(info.context["conn"])
        completed_data = db.completed_list(str(user_id))
        return [UserWord(**item) for item in completed_data]

    @strawberry.field
    def get_stats_today(self, info: strawberry.Info, user_id: strawberry.ID) -> Optional[UserStatsDaily]:
        db = Database(info.context["conn"])
        stats_data = db.get_stats_today(str(user_id))
        if stats_data:
            return UserStatsDaily(**stats_data)
        return None

    @strawberry.field
    def get_total_stats(self, info: strawberry.Info, user_id: strawberry.ID) -> TotalStatsType:
        db = Database(info.context["conn"])
        stats_data = db.get_total_stats(str(user_id))
        return TotalStatsType(**stats_data)

    @strawberry.field
    def noun_hints(self, info: strawberry.Info, user_id: strawberry.ID, limit: Optional[int] = None) -> List[NounHintType]:
        db = Database(info.context["conn"])
        hints_data = db.noun_hints(str(user_id), limit)
        result_hints = []
        for hint in hints_data:
            # Derive fallback, label, insert as per the schema description
            gender_prefix = ""
            if hint['gender'] == 'der':
                gender_prefix = "Der"
            elif hint['gender'] == 'die':
                gender_prefix = "Die"
            elif hint['gender'] == 'das':
                gender_prefix = "Das"

            fallback = f"{gender_prefix}"
            label = f"{gender_prefix} {hint['noun']} (acc: {hint['case_forms'].get('accusative', '')})"
            insert = hint['noun']
            result_hints.append(NounHintType(
                gender=hint['gender'],
                noun=hint['noun'],
                case_forms=hint['case_forms'],
                english_translation=hint['english_translation'],
                fallback=fallback,
                label=label,
                insert=insert
            ))
        return result_hints
