import strawberry
from typing import Optional, List, cast
from lexilearn.database import Database
from lexilearn.graphql.types.object_types import Word, UserWordProgress

@strawberry.type
class MvpQuery:
    @strawberry.field
    def words(self, info: strawberry.Info, lemmas: List[str], pos: Optional[str] = None, search: Optional[str] = None, limit: Optional[int] = 50) -> List[Word]:
        db = cast(Database, info.context["db"])
        words_data = db.get_words(lemmas, pos, search, limit)
        return [Word(**word) for word in words_data]

    @strawberry.field
    def userProgress(self, info: strawberry.Info, user_id: strawberry.ID, status: Optional[str] = None, dueBefore: Optional[str] = None) -> List[UserWordProgress]:
        db = cast(Database, info.context["db"])
        progress_list = db.get_user_progress(str(user_id), status, dueBefore)
        result = []
        for progress_data in progress_list:
            word_lemma, word_pos = progress_data["word_id"].split(":")[1].split("#")
            word = db.get_words(lemmas=[word_lemma], pos=word_pos)
            progress_data["word"] = word[0]
            result.append(UserWordProgress(**progress_data))
        return result

    @strawberry.field
    def dueReviews(self, info: strawberry.Info, user_id: strawberry.ID, before: str) -> List[UserWordProgress]:
        db = cast(Database, info.context["db"])
        progress_list = db.get_due_reviews(str(user_id), before)
        result = []
        for progress_data in progress_list:
            word_lemma, word_pos = progress_data["word_id"].split(":")[1].split("#")
            word = db.get_words(lemmas=[word_lemma], pos=word_pos)
            progress_data["word"] = word[0]
            result.append(UserWordProgress(**progress_data))
        return result
