import strawberry
from typing import List, cast
from lexilearn.database import Database
from lexilearn.graphql.types.object_types import Word, UserWordProgress
from lexilearn.graphql.inputs import UpsertWordInput, UpdateProgressInput

@strawberry.type
class MvpMutation:
    @strawberry.mutation
    def upsert_word(self, info: strawberry.Info, input: UpsertWordInput) -> Word:
        db = cast(Database, info.context["db"])
        word_data = db.upsert_word(input.__dict__)
        return Word(**word_data)

    @strawberry.mutation
    def upsert_user_word_progress(self, info: strawberry.Info, input: UpdateProgressInput) -> UserWordProgress:
        db = cast(Database, info.context["db"])
        progress_data = db.upsert_user_word_progress(input.__dict__)
        word_lemma, word_pos = progress_data["word_id"].split(":")[1].split("#")
        word = db.get_words(lemmas=[word_lemma], pos=word_pos)
        progress_data["word"] = word[0]
        return UserWordProgress(**progress_data)

    @strawberry.mutation
    def record_quiz_result(self, info: strawberry.Info, user_id: strawberry.ID, word_id: strawberry.ID, correct: bool, score: float) -> UserWordProgress:
        db = cast(Database, info.context["db"])
        progress_data = db.record_quiz_result(str(user_id), str(word_id), correct, score)
        word_lemma, word_pos = progress_data["word_id"].split(":")[1].split("#")
        word = db.get_words(lemmas=[word_lemma], pos=word_pos)
        progress_data["word"] = word[0]
        return UserWordProgress(**progress_data)

    @strawberry.mutation
    def schedule_reviews(self, info: strawberry.Info, user_id: strawberry.ID) -> List[UserWordProgress]:
        db = cast(Database, info.context["db"])
        progress_list = db.schedule_reviews(str(user_id))
        result = []
        for progress_data in progress_list:
            word_lemma, word_pos = progress_data["word_id"].split(":")[1].split("#")
            word = db.get_words(lemmas=[word_lemma], pos=word_pos)
            progress_data["word"] = word[0]
            result.append(UserWordProgress(**progress_data))
        return result
