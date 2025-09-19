"""MongoDB persistence layer for LexiLearn."""
from __future__ import annotations

import os
import uuid
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database as _MongoDatabase

_MONGO_CLIENT: Optional[MongoClient] = None
_INDEXES_READY = False


def _get_client() -> MongoClient:
    """Return a module-level MongoClient instance, creating it on demand."""
    global _MONGO_CLIENT
    if _MONGO_CLIENT is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        _MONGO_CLIENT = MongoClient(uri, tz_aware=False)
    return _MONGO_CLIENT


def reset_client_for_tests() -> None:
    """Reset the cached MongoDB client (used in tests)."""
    global _MONGO_CLIENT, _INDEXES_READY
    if _MONGO_CLIENT is not None:
        _MONGO_CLIENT.close()
    _MONGO_CLIENT = None
    _INDEXES_READY = False


def get_db_connection() -> _MongoDatabase:
    """Return the configured MongoDB database handle."""
    client = _get_client()
    db_name = os.getenv("MONGODB_DB", "lexilearn")
    return client[db_name]


def _coerce_datetime(value: Optional[Any], *, default: Optional[datetime] = None) -> Optional[datetime]:
    if value is None:
        return default
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return default
    return default


def _iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if isinstance(value, datetime) else value


def _word_uid(item_type: str, item_id: str) -> str:
    return f"{item_type}:{item_id}"


class Database:
    """High level helper around MongoDB collections."""

    def __init__(self, conn: Optional[Any] = None):
        if isinstance(conn, Database):
            self._client = conn._client
            self._db = conn._db
            self._owns_client = False
        elif isinstance(conn, MongoClient):
            self._client = conn
            db_name = os.getenv("MONGODB_DB", "lexilearn")
            self._db = conn[db_name]
            self._owns_client = False
        elif isinstance(conn, _MongoDatabase):
            self._client = conn.client
            self._db = conn
            self._owns_client = False
        elif hasattr(conn, "client") and hasattr(conn, "name"):
            self._client = conn.client
            self._db = conn
            self._owns_client = False
        elif conn is None:
            self._client = _get_client()
            db_name = os.getenv("MONGODB_DB", "lexilearn")
            self._db = self._client[db_name]
            self._owns_client = False
        else:
            raise TypeError(f"Unsupported connection type: {type(conn)!r}")

        self._ensure_indexes()

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def close(self) -> None:
        if getattr(self, "_owns_client", False) and self._client:
            self._client.close()

    def create_tables(self) -> None:  # Backwards compatibility for tests
        self._ensure_indexes()

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _ensure_indexes(self) -> None:
        global _INDEXES_READY
        if _INDEXES_READY:
            return
        # Lexical collections
        self._db.verbs.create_index("infinitive", unique=True)
        self._db.nouns.create_index("noun", unique=True)
        self._db.adjectives.create_index("adjective", unique=True)
        self._db.adverbs.create_index("adverb", unique=True)
        self._db.prepositions.create_index("preposition", unique=True)
        self._db.conjunctions.create_index("conjunction", unique=True)

        # Users and settings
        self._db.users.create_index("email", unique=True)
        self._db.user_settings.create_index("user_id", unique=True)
        self._db.user_stats_daily.create_index([("user_id", ASCENDING), ("day", ASCENDING)], unique=True)

        # Word catalogue & practice data
        self._db.word_index.create_index("word_uid", unique=True)
        self._db.word_index.create_index([("item_type", ASCENDING), ("item_id", ASCENDING)], unique=True)
        self._db.user_words.create_index([("user_id", ASCENDING), ("word_uid", ASCENDING)], unique=True)
        self._db.user_words.create_index([("user_id", ASCENDING), ("status", ASCENDING), ("due_at", ASCENDING)])
        self._db.practice_events.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        self._db.prompts.create_index([("level", ASCENDING), ("created_at", DESCENDING)])
        self._db.sentence_analyses.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        self._db.assignments.create_index([("assignment_uid", ASCENDING)], unique=True)
        self._db.assignments.create_index([("user_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)])
        self._db.real_world_scenarios.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

        # MVP collections
        self._db.words.create_index([("lemma", ASCENDING), ("pos", ASCENDING)], unique=True)
        self._db.user_word_progress.create_index([("user_id", ASCENDING), ("word_id", ASCENDING)], unique=True)
        self._db.user_word_progress.create_index([("next_review_at", ASCENDING)])
        self._db.user_submissions.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        self._db.words.create_index([("lemma", "text"), ("translations_en", "text")])

        _INDEXES_READY = True

    # ------------------------------------------------------------------
    # MVP Methods
    # ------------------------------------------------------------------

    def save_submission(self, user_id: str, text: str) -> str:
        sub_id = f"sub:{uuid.uuid4()}"
        now = datetime.utcnow()
        doc = {
            "_id": sub_id,
            "user_id": user_id,
            "text": text,
            "created_at": now,
        }
        self._db.user_submissions.insert_one(doc)
        return sub_id

    def upsert_word(self, word_data: Dict[str, Any]) -> Dict[str, Any]:
        lemma = word_data["lemma"]
        pos = word_data["pos"]
        now = datetime.utcnow()
        word_id = f"word:{lemma}#{pos}"

        update_data = {
            "lemma": lemma,
            "pos": pos,
            "translations_en": word_data.get("translations_en", []),
            "grammar": word_data.get("grammar", {}),
            "examples": word_data.get("examples", []),
            "surface_forms": word_data.get("surface_forms", []),
            "updated_at": now,
        }

        result = self._db.words.update_one(
            {"_id": word_id},
            {
                "$set": update_data,
                "$setOnInsert": {"created_at": now, "_id": word_id},
            },
            upsert=True,
        )
        
        if result.upserted_id:
            return self._db.words.find_one({"_id": result.upserted_id})
        else:
            return self._db.words.find_one({"_id": word_id})


    def get_words(
        self,
        lemmas: List[str],
        pos: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if lemmas:
            query["lemma"] = {"$in": lemmas}
        if pos:
            query["pos"] = pos
        if search:
            query["$text"] = {"$search": search}  # Requires a text index

        cursor = self._db.words.find(query).limit(limit)
        
        #Pymongo cursor is not a list, so we need to iterate over it
        word_list = []
        for word in cursor:
            word_list.append(word)
        return word_list

    def upsert_user_word_progress(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = progress_data["user_id"]
        word_id = progress_data["word_id"]
        now = datetime.utcnow()
        progress_id = f"uwp:{user_id}#{word_id}"

        update_data = {
            "user_id": user_id,
            "word_id": word_id,
            "status": progress_data.get("status", "new"),
            "confidence": progress_data.get("confidence", 0.0),
            "srs_stage": progress_data.get("srs_stage", 0),
            "next_review_at": progress_data.get("next_review_at"),
            "learned_at": progress_data.get("learned_at"),
            "updated_at": now,
        }

        update_query = {"$set": update_data}
        if "event" in progress_data:
            update_query["$push"] = {"history": progress_data["event"]}

        result = self._db.user_word_progress.update_one(
            {"_id": progress_id},
            {
                **update_query,
                "$setOnInsert": {"created_at": now, "_id": progress_id, "history": []},
            },
            upsert=True,
        )

        if result.upserted_id:
            return self._db.user_word_progress.find_one({"_id": result.upserted_id})
        else:
            return self._db.user_word_progress.find_one({"_id": progress_id})

    def get_user_progress(
        self,
        user_id: str,
        status: Optional[str] = None,
        due_before: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id}
        if status:
            query["status"] = status
        if due_before:
            query["next_review_at"] = {"$lte": datetime.fromisoformat(due_before)}

        cursor = self._db.user_word_progress.find(query)
        return list(cursor)

    def get_due_reviews(self, user_id: str, before: str) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {
            "user_id": user_id,
            "next_review_at": {"$lte": datetime.fromisoformat(before)},
        }
        cursor = self._db.user_word_progress.find(query)
        return list(cursor)

    def record_quiz_result(
        self, user_id: str, word_id: str, correct: bool, score: float
    ) -> Dict[str, Any]:
        from datetime import timedelta
        now = datetime.utcnow()
        progress = self._db.user_word_progress.find_one({"user_id": user_id, "word_id": word_id})

        if not progress:
            raise ValueError(f"No progress found for user {user_id} and word {word_id}")

        srs_stage = progress.get("srs_stage", 0)
        if correct:
            srs_stage += 1
        else:
            srs_stage = max(0, srs_stage - 1)

        # Spaced Review Policy from prompt
        srs_intervals = [0, 1, 3, 7, 16, 35]
        interval_days = srs_intervals[min(srs_stage, len(srs_intervals) - 1)]
        next_review_at = now + timedelta(days=interval_days)

        status = progress.get("status")
        if correct and score > 0.9: # Assuming 0.9 is the threshold for "learned"
            status = "learned"
            learned_at = now
        else:
            learned_at = progress.get("learned_at")


        event = {"event": "quiz_result", "score": score, "correct": correct, "at": now.isoformat()}

        return self.upsert_user_word_progress({
            "user_id": user_id,
            "word_id": word_id,
            "status": status,
            "confidence": score,
            "srs_stage": srs_stage,
            "next_review_at": next_review_at.isoformat(),
            "learned_at": learned_at.isoformat() if learned_at else None,
            "event": event,
        })

    def schedule_reviews(self, user_id: str) -> List[Dict[str, Any]]:
        # This method is underspecified in the prompt.
        # It could be interpreted in a few ways.
        # 1. It could be a no-op, as record_quiz_result already schedules the next review.
        # 2. It could be a batch job that goes through all user_word_progress and updates schedules.
        # For now, I will assume it's a no-op and just returns the due reviews.
        return self.get_due_reviews(user_id, datetime.utcnow().isoformat())

    # Serialisers -------------------------------------------------------
    def _normalise_word_index(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        return {
            "word_uid": doc["word_uid"],
            "item_type": doc["item_type"],
            "item_id": doc["item_id"],
        }

    def _normalise_user_word(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        return {
            "user_id": doc["user_id"],
            "word_uid": doc["word_uid"],
            "item_type": doc.get("item_type"),
            "item_id": doc.get("item_id"),
            "status": doc.get("status", "new"),
            "due_at": doc.get("due_at"),
            "interval_days": doc.get("interval_days", 0.0),
            "stability": doc.get("stability", 0.0),
            "difficulty": doc.get("difficulty", 0.0),
            "lapses": doc.get("lapses", 0),
            "last_result": doc.get("last_result"),
            "last_prompt_id": doc.get("last_prompt_id"),
            "added_at": doc.get("added_at"),
            "updated_at": doc.get("updated_at"),
        }

    def _normalise_user_settings(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        return {
            "user_id": doc["user_id"],
            "level": doc.get("level", "beginner"),
            "daily_goal": doc.get("daily_goal", 10),
            "style": doc.get("style", "mixed"),
            "review_enabled": bool(doc.get("review_enabled", True)),
            "updated_at": doc.get("updated_at", datetime.utcnow()),
        }

    def _ensure_word_index(self, item_type: str, item_id: str, word_uid: Optional[str] = None) -> str:
        uid = word_uid or _word_uid(item_type, item_id)
        now = datetime.utcnow()
        self._db.word_index.update_one(
            {"word_uid": uid},
            {
                "$set": {
                    "word_uid": uid,
                    "item_type": item_type,
                    "item_id": item_id,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        return uid

    # ------------------------------------------------------------------
    # Lexical data
    # ------------------------------------------------------------------
    def add_verb(self, verb_data: Dict[str, Any]) -> str:
        infinitive = verb_data["infinitive"]
        doc = {
            "infinitive": infinitive,
            "present": verb_data.get("present", {}),
            "present_perfect": verb_data.get("present_perfect", []),
            "singular_present_tense": verb_data.get("singular_present_tense", []),
            "simple_past": verb_data.get("simple_past", []),
            "is_separable": verb_data.get("is_separable", False),
            "is_regular": verb_data.get("is_regular", True),
            "english_alternative": verb_data.get("english_alternative", []),
            "notes": verb_data.get("notes", []),
        }
        self._db.verbs.replace_one({"infinitive": infinitive}, doc, upsert=True)
        self._ensure_word_index("verb", infinitive, verb_data.get("word_uid"))
        return infinitive

    def get_verb(self, infinitive: str) -> Optional[Dict[str, Any]]:
        doc = self._db.verbs.find_one({"infinitive": infinitive})
        if not doc:
            return None
        return {
            "infinitive": doc["infinitive"],
            "present": doc.get("present", {}),
            "present_perfect": doc.get("present_perfect", []),
            "singular_present_tense": doc.get("singular_present_tense", []),
            "simple_past": doc.get("simple_past", []),
            "is_separable": bool(doc.get("is_separable", False)),
            "is_regular": bool(doc.get("is_regular", True)),
            "english_alternative": doc.get("english_alternative", []),
            "notes": doc.get("notes", []),
        }

    def add_noun(self, noun_data: Dict[str, Any]) -> str:
        noun = noun_data["noun"]
        doc = {
            "noun": noun,
            "plural": noun_data.get("plural"),
            "gender": noun_data.get("gender"),
            "case_forms": noun_data.get("case_forms", {}),
            "english_translation": noun_data.get("english_translation"),
            "is_irregular": noun_data.get("is_irregular", False),
        }
        self._db.nouns.replace_one({"noun": noun}, doc, upsert=True)
        self._ensure_word_index("noun", noun, noun_data.get("word_uid"))
        return noun

    def get_noun(self, noun: str) -> Optional[Dict[str, Any]]:
        doc = self._db.nouns.find_one({"noun": noun})
        if not doc:
            return None
        return {
            "noun": doc["noun"],
            "plural": doc.get("plural"),
            "gender": doc.get("gender"),
            "case_forms": doc.get("case_forms", {}),
            "english_translation": doc.get("english_translation"),
            "is_irregular": bool(doc.get("is_irregular", False)),
        }

    def add_adjective(self, adjective_data: Dict[str, Any]) -> str:
        adjective = adjective_data["adjective"]
        doc = {
            "adjective": adjective,
            "comparative": adjective_data.get("comparative"),
            "superlative": adjective_data.get("superlative"),
            "english_translation": adjective_data.get("english_translation"),
            "is_regular": adjective_data.get("is_regular", True),
            "is_comparable": adjective_data.get("is_comparable", True),
        }
        self._db.adjectives.replace_one({"adjective": adjective}, doc, upsert=True)
        return adjective

    def get_adjective(self, adjective: str) -> Optional[Dict[str, Any]]:
        doc = self._db.adjectives.find_one({"adjective": adjective})
        if not doc:
            return None
        return {
            "adjective": doc["adjective"],
            "comparative": doc.get("comparative"),
            "superlative": doc.get("superlative"),
            "english_translation": doc.get("english_translation"),
            "is_regular": bool(doc.get("is_regular", True)),
            "is_comparable": bool(doc.get("is_comparable", True)),
        }

    def add_adverb(self, adverb_data: Dict[str, Any]) -> str:
        adverb = adverb_data["adverb"]
        doc = {
            "adverb": adverb,
            "english_translation": adverb_data.get("english_translation"),
            "adverb_type": adverb_data.get("adverb_type"),
            "is_comparable": adverb_data.get("is_comparable", False),
        }
        self._db.adverbs.replace_one({"adverb": adverb}, doc, upsert=True)
        return adverb

    def get_adverb(self, adverb: str) -> Optional[Dict[str, Any]]:
        doc = self._db.adverbs.find_one({"adverb": adverb})
        if not doc:
            return None
        return {
            "adverb": doc["adverb"],
            "english_translation": doc.get("english_translation"),
            "adverb_type": doc.get("adverb_type"),
            "is_comparable": bool(doc.get("is_comparable", False)),
        }

    def add_preposition(self, preposition_data: Dict[str, Any]) -> str:
        preposition = preposition_data["preposition"]
        doc = {
            "preposition": preposition,
            "english_translation": preposition_data.get("english_translation"),
            "case_governed": preposition_data.get("case_governed"),
            "preposition_type": preposition_data.get("preposition_type"),
        }
        self._db.prepositions.replace_one({"preposition": preposition}, doc, upsert=True)
        return preposition

    def get_preposition(self, preposition: str) -> Optional[Dict[str, Any]]:
        doc = self._db.prepositions.find_one({"preposition": preposition})
        if not doc:
            return None
        return {
            "preposition": doc["preposition"],
            "english_translation": doc.get("english_translation"),
            "case_governed": doc.get("case_governed"),
            "preposition_type": doc.get("preposition_type"),
        }

    def add_conjunction(self, conjunction_data: Dict[str, Any]) -> str:
        conjunction = conjunction_data["conjunction"]
        doc = {
            "conjunction": conjunction,
            "english_translation": conjunction_data.get("english_translation"),
            "conjunction_type": conjunction_data.get("conjunction_type"),
        }
        self._db.conjunctions.replace_one({"conjunction": conjunction}, doc, upsert=True)
        return conjunction

    def get_conjunction(self, conjunction: str) -> Optional[Dict[str, Any]]:
        doc = self._db.conjunctions.find_one({"conjunction": conjunction})
        if not doc:
            return None
        return {
            "conjunction": doc["conjunction"],
            "english_translation": doc.get("english_translation"),
            "conjunction_type": doc.get("conjunction_type"),
        }

    # ------------------------------------------------------------------
    # Word index helpers
    # ------------------------------------------------------------------
    def add_word_index(self, word_index_data: Dict[str, Any]) -> str:
        item_type = word_index_data["item_type"]
        item_id = word_index_data["item_id"]
        word_uid = self._ensure_word_index(item_type, item_id, word_index_data.get("word_uid"))
        return word_uid

    def get_word_index(self, word_uid: str) -> Optional[Dict[str, Any]]:
        doc = self._db.word_index.find_one({"word_uid": word_uid})
        return self._normalise_word_index(doc)

    def list_words(
        self,
        item_type: Optional[str] = None,
        item_ids: Optional[Sequence[str]] = None,
        *,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if item_type:
            query["item_type"] = item_type
        if item_ids:
            query["item_id"] = {"$in": list(item_ids)}
        cursor = (
            self._db.word_index.find(query)
            .sort("item_id", ASCENDING)
            .skip(max(skip, 0))
            .limit(max(limit, 0))
        )
        return [self._normalise_word_index(doc) for doc in cursor]

    def detect_words(self, tokens: Sequence[str]) -> List[Dict[str, Any]]:
        if not tokens:
            return []
        unique_tokens = list({token.lower() for token in tokens})
        cursor = self._db.word_index.find({"item_id": {"$in": unique_tokens}})
        return [self._normalise_word_index(doc) for doc in cursor]

    def random_word(
        self,
        user_id: str,
        *,
        preferred_types: Optional[Sequence[str]] = None,
        exclude_ids: Optional[Sequence[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        preferred = list(preferred_types or ["verb", "noun"])
        excluded = set(exclude_ids or [])
        for item_type in preferred:
            query: Dict[str, Any] = {"item_type": item_type}
            if excluded:
                query["item_id"] = {"$nin": list(excluded)}
            sample = list(
                self._db.word_index.aggregate(
                    [{"$match": query}, {"$sample": {"size": 1}}]
                )
            )
            if sample:
                return self._normalise_word_index(sample[0])
        return None

    # ------------------------------------------------------------------
    # Sentence analyses & adaptive assignments
    # ------------------------------------------------------------------
    def _normalise_assignment(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        return {
            "assignment_id": doc.get("assignment_uid"),
            "user_id": doc.get("user_id"),
            "sentence": doc.get("sentence"),
            "level": doc.get("level"),
            "goals": doc.get("goals", []),
            "focus": doc.get("focus", {}),
            "activities": doc.get("activities", []),
            "reflection": doc.get("reflection", []),
            "real_world_bridge": doc.get("real_world_bridge", []),
            "language_bank": doc.get("language_bank", []),
            "status": doc.get("status", "draft"),
            "iteration": doc.get("iteration", 1),
            "analysis_id": doc.get("analysis_id"),
            "analysis_snapshot": doc.get("analysis_snapshot"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            "history": doc.get("history", []),
        }

    def save_sentence_analysis(
        self,
        user_id: str,
        sentence: str,
        analysis: Dict[str, Any],
        *,
        focus: Optional[List[str]] = None,
    ) -> str:
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "sentence": sentence,
            "analysis": analysis,
            "focus": focus or [],
            "created_at": now,
        }
        self._db.sentence_analyses.insert_one(doc)
        return analysis_id

    def get_sentence_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        doc = self._db.sentence_analyses.find_one({"analysis_id": analysis_id})
        if not doc:
            return None
        return {
            "analysis_id": doc["analysis_id"],
            "user_id": doc["user_id"],
            "sentence": doc.get("sentence"),
            "analysis": doc.get("analysis", {}),
            "focus": doc.get("focus", []),
            "created_at": doc.get("created_at"),
        }

    def list_sentence_analyses(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = (
            self._db.sentence_analyses.find({"user_id": user_id})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        summaries: List[Dict[str, Any]] = []
        for doc in cursor:
            summaries.append(
                {
                    "analysis_id": doc.get("analysis_id"),
                    "sentence": doc.get("sentence"),
                    "focus": doc.get("focus", []),
                    "created_at": doc.get("created_at"),
                }
            )
        return summaries

    def create_assignment(self, assignment_data: Dict[str, Any]) -> str:
        assignment_id = assignment_data.get("assignment_id") or str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {
            "assignment_uid": assignment_id,
            "user_id": assignment_data.get("user_id", "test_user"),
            "sentence": assignment_data.get("sentence"),
            "level": assignment_data.get("level"),
            "goals": assignment_data.get("goals", []),
            "focus": assignment_data.get("focus", {}),
            "activities": assignment_data.get("activities", []),
            "reflection": assignment_data.get("reflection", []),
            "real_world_bridge": assignment_data.get("real_world_bridge", []),
            "language_bank": assignment_data.get("language_bank", []),
            "status": assignment_data.get("status", "draft"),
            "iteration": assignment_data.get("iteration", 1),
            "analysis_id": assignment_data.get("analysis_id"),
            "analysis_snapshot": assignment_data.get("analysis_snapshot"),
            "history": assignment_data.get("history", []),
            "created_at": assignment_data.get("created_at", now),
            "updated_at": now,
        }
        self._db.assignments.replace_one({"assignment_uid": assignment_id}, doc, upsert=True)
        return assignment_id

    def get_assignment(self, assignment_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {"assignment_uid": assignment_id}
        if user_id:
            query["user_id"] = user_id
        doc = self._db.assignments.find_one(query)
        return self._normalise_assignment(doc)

    def list_assignments(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id}
        if status:
            query["status"] = status
        cursor = self._db.assignments.find(query).sort("created_at", DESCENDING)
        return [self._normalise_assignment(doc) for doc in cursor if doc]

    def update_assignment(self, assignment_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        mutation: Dict[str, Any] = {"updated_at": datetime.utcnow()}
        for key, value in updates.items():
            if key in {"created_at", "assignment_uid"}:
                continue
            if key in {"due_at"}:
                mutation[key] = _coerce_datetime(value)
            else:
                mutation[key] = value
        doc = self._db.assignments.find_one_and_update(
            {"assignment_uid": assignment_id},
            {"$set": mutation},
            return_document=True,
        )
        if not doc:
            raise ValueError(f"assignment not found for {assignment_id}")
        return self._normalise_assignment(doc)  # type: ignore

    def append_assignment_history(self, assignment_id: str, entry: Dict[str, Any]) -> None:
        payload = {
            "$push": {
                "history": {
                    **entry,
                    "created_at": _coerce_datetime(entry.get("created_at"), default=datetime.utcnow()),
                }
            },
            "$set": {"updated_at": datetime.utcnow()},
        }
        self._db.assignments.update_one({"assignment_uid": assignment_id}, payload)

    def add_real_life_scenario(self, scenario_data: Dict[str, Any]) -> str:
        scenario_id = scenario_data.get("scenario_id") or str(uuid.uuid4())
        doc = {
            "scenario_id": scenario_id,
            "user_id": scenario_data.get("user_id", "test_user"),
            "level": scenario_data.get("level"),
            "theme": scenario_data.get("theme"),
            "situation": scenario_data.get("situation"),
            "role_play": scenario_data.get("role_play", {}),
            "checklist": scenario_data.get("checklist", []),
            "language_bank": scenario_data.get("language_bank", []),
            "created_at": scenario_data.get("created_at", datetime.utcnow()),
        }
        self._db.real_world_scenarios.replace_one(
            {"scenario_id": scenario_id},
            doc,
            upsert=True,
        )
        return scenario_id

    def list_real_life_scenarios(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = (
            self._db.real_world_scenarios.find({"user_id": user_id})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        scenarios: List[Dict[str, Any]] = []
        for doc in cursor:
            scenarios.append(
                {
                    "scenario_id": doc.get("scenario_id"),
                    "level": doc.get("level"),
                    "theme": doc.get("theme"),
                    "situation": doc.get("situation"),
                    "role_play": doc.get("role_play", {}),
                    "checklist": doc.get("checklist", []),
                    "language_bank": doc.get("language_bank", []),
                    "created_at": doc.get("created_at"),
                }
            )
        return scenarios

    # ------------------------------------------------------------------
    # Users & settings
    # ------------------------------------------------------------------
    def add_app_user(self, user_data: Dict[str, Any]) -> str:
        user_id = user_data.get("id") or str(uuid.uuid4())
        created_at = _coerce_datetime(user_data.get("created_at"), default=datetime.utcnow()) or datetime.utcnow()
        doc = {
            "_id": user_id,
            "email": user_data["email"],
            "display_name": user_data.get("display_name"),
            "created_at": created_at,
        }
        self._db.users.replace_one({"_id": user_id}, doc, upsert=True)
        return user_id

    def get_app_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self._db.users.find_one({"_id": user_id})
        if not doc:
            return None
        return {
            "id": doc["_id"],
            "email": doc["email"],
            "display_name": doc.get("display_name"),
            "created_at": doc.get("created_at", datetime.utcnow()),
        }

    def add_user_settings(self, settings_data: Dict[str, Any]) -> None:
        user_id = settings_data["user_id"]
        updated_at = _coerce_datetime(settings_data.get("updated_at"), default=datetime.utcnow()) or datetime.utcnow()
        doc = {
            "_id": user_id,
            "user_id": user_id,
            "level": settings_data.get("level", "beginner"),
            "daily_goal": settings_data.get("daily_goal", 10),
            "style": settings_data.get("style", "mixed"),
            "review_enabled": settings_data.get("review_enabled", True),
            "updated_at": updated_at,
        }
        self._db.user_settings.replace_one({"_id": user_id}, doc, upsert=True)

    def get_user_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = self._db.user_settings.find_one({"_id": user_id})
        return self._normalise_user_settings(doc)

    def update_user_settings(
        self,
        user_id: str,
        *,
        level: Optional[str] = None,
        daily_goal: Optional[int] = None,
        style: Optional[str] = None,
        review_enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        update: Dict[str, Any] = {}
        if level is not None:
            update["level"] = level
        if daily_goal is not None:
            update["daily_goal"] = daily_goal
        if style is not None:
            update["style"] = style
        if review_enabled is not None:
            update["review_enabled"] = review_enabled
        update["updated_at"] = datetime.utcnow()
        self._db.user_settings.update_one(
            {"_id": user_id},
            {"$set": update},
            upsert=True,
        )
        doc = self._db.user_settings.find_one({"_id": user_id})
        assert doc is not None
        return self._normalise_user_settings(doc)  # type: ignore

    def add_user_stats_daily(self, stats_data: Dict[str, Any]) -> None:
        user_id = stats_data["user_id"]
        day = stats_data["day"]
        doc = {
            "_id": f"{user_id}:{day}",
            "user_id": user_id,
            "day": day,
            "learned": stats_data.get("learned", 0),
            "practiced": stats_data.get("practiced", 0),
            "completed": stats_data.get("completed", 0),
        }
        self._db.user_stats_daily.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    def get_user_stats_daily(self, user_id: str, day: str) -> Optional[Dict[str, Any]]:
        doc = self._db.user_stats_daily.find_one({"_id": f"{user_id}:{day}"})
        if not doc:
            return None
        parsed_day = day
        try:
            parsed_day = datetime.fromisoformat(day).date()
        except ValueError:
            parsed_day = day
        return {
            "user_id": user_id,
            "day": parsed_day,
            "learned": doc.get("learned", 0),
            "practiced": doc.get("practiced", 0),
            "completed": doc.get("completed", 0),
        }

    # ------------------------------------------------------------------
    # Practice data
    # ------------------------------------------------------------------
    def add_user_word(self, user_word_data: Dict[str, Any]) -> str:
        user_id = user_word_data["user_id"]
        word_uid = user_word_data.get("word_uid")
        item_type = user_word_data.get("item_type")
        item_id = user_word_data.get("item_id")
        if not word_uid:
            if item_type and item_id:
                word_uid = self._ensure_word_index(item_type, item_id)
            else:
                raise ValueError("word_uid or (item_type, item_id) must be provided")
        if (item_type is None or item_id is None) and word_uid and ":" in word_uid:
            item_type, item_id = word_uid.split(":", 1)
        now = datetime.utcnow()
        doc = {
            "user_id": user_id,
            "word_uid": word_uid,
            "item_type": item_type,
            "item_id": item_id,
            "status": user_word_data.get("status", "new"),
            "due_at": _coerce_datetime(user_word_data.get("due_at")),
            "interval_days": user_word_data.get("interval_days", 0.0),
            "stability": user_word_data.get("stability", 0.0),
            "difficulty": user_word_data.get("difficulty", 0.0),
            "lapses": user_word_data.get("lapses", 0),
            "last_result": user_word_data.get("last_result"),
            "last_prompt_id": user_word_data.get("last_prompt_id"),
            "added_at": _coerce_datetime(user_word_data.get("added_at"), default=now) or now,
            "updated_at": _coerce_datetime(user_word_data.get("updated_at"), default=now) or now,
        }
        self._db.user_words.replace_one({"user_id": user_id, "word_uid": word_uid}, doc, upsert=True)
        return word_uid

    def get_user_word(self, user_id: str, word_uid: str) -> Optional[Dict[str, Any]]:
        doc = self._db.user_words.find_one({"user_id": user_id, "word_uid": word_uid})
        return self._normalise_user_word(doc)

    def update_user_word_status(
        self,
        user_id: str,
        word_uid: str,
        *,
        status: Optional[str] = None,
        last_result: Optional[str] = None,
        due_at: Optional[Any] = None,
    ) -> Dict[str, Any]:
        update: Dict[str, Any] = {"updated_at": datetime.utcnow()}
        if status is not None:
            update["status"] = status
        if last_result is not None:
            update["last_result"] = last_result
        if due_at is not None:
            update["due_at"] = _coerce_datetime(due_at)
        doc = self._db.user_words.find_one_and_update(
            {"user_id": user_id, "word_uid": word_uid},
            {"$set": update},
            return_document=True,
        )
        if not doc:
            raise ValueError(f"user_word not found for {user_id=} {word_uid=}")
        return self._normalise_user_word(doc)  # type: ignore

    def update_user_word(self, user_id: str, word_uid: str, **fields: Any) -> Dict[str, Any]:
        """Update arbitrary user word fields and return the refreshed document."""
        if not fields:
            return self.get_user_word(user_id, word_uid) or {}
        update: Dict[str, Any] = {}
        for key, value in fields.items():
            if key in {"due_at", "added_at", "updated_at"}:
                update[key] = _coerce_datetime(value)
            else:
                update[key] = value
        update["updated_at"] = datetime.utcnow()
        doc = self._db.user_words.find_one_and_update(
            {"user_id": user_id, "word_uid": word_uid},
            {"$set": update},
            return_document=True,
        )
        if not doc:
            raise ValueError(f"user_word not found for {user_id=} {word_uid=}")
        return self._normalise_user_word(doc)  # type: ignore

    def get_practice_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        doc = self._db.practice_sessions.find_one({"id": session_id})
        if not doc:
            return None
        return {
            "id": doc["id"],
            "user_id": doc["user_id"],
            "started_at": doc.get("started_at"),
            "ended_at": doc.get("ended_at"),
        }

    def add_practice_session(self, session_data: Dict[str, Any]) -> str:
        session_id = session_data.get("id") or str(uuid.uuid4())
        doc = {
            "id": session_id,
            "user_id": session_data["user_id"],
            "started_at": _coerce_datetime(session_data.get("started_at"), default=datetime.utcnow()),
            "ended_at": _coerce_datetime(session_data.get("ended_at")),
        }
        self._db.practice_sessions.replace_one({"id": session_id}, doc, upsert=True)
        return session_id

    def get_practice_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        doc = self._db.practice_events.find_one({"id": event_id})
        if not doc:
            return None
        return {
            "id": doc["id"],
            "session_id": doc.get("session_id"),
            "user_id": doc["user_id"],
            "word_uid": doc["word_uid"],
            "prompt_id": doc.get("prompt_id"),
            "level_at_time": doc.get("level_at_time"),
            "confidence": doc.get("confidence"),
            "expected": doc.get("expected"),
            "answer": doc.get("answer"),
            "correct": doc.get("correct"),
            "issues": doc.get("issues"),
            "normalized": doc.get("normalized"),
            "created_at": doc.get("created_at"),
        }

    def add_practice_event(self, event_data: Dict[str, Any]) -> str:
        event_id = event_data.get("id") or str(uuid.uuid4())
        doc = {
            "id": event_id,
            "session_id": event_data.get("session_id"),
            "user_id": event_data["user_id"],
            "word_uid": event_data["word_uid"],
            "prompt_id": event_data.get("prompt_id"),
            "level_at_time": event_data.get("level_at_time"),
            "confidence": event_data.get("confidence"),
            "expected": event_data.get("expected"),
            "answer": event_data.get("answer"),
            "correct": event_data.get("correct"),
            "issues": event_data.get("issues"),
            "normalized": event_data.get("normalized"),
            "created_at": _coerce_datetime(event_data.get("created_at"), default=datetime.utcnow()),
        }
        self._db.practice_events.replace_one({"id": event_id}, doc, upsert=True)
        return event_id

    def evaluate_practice_event(self, event_data: Dict[str, Any]) -> str:
        return self.add_practice_event(event_data)

    def practice_queue(self, user_id: str, *, limit: int = 50) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        query = {
            "user_id": user_id,
            "status": {"$in": ["queued", "learning"]},
            "$or": [
                {"due_at": {"$exists": False}},
                {"due_at": None},
                {"due_at": {"$lte": now}},
            ],
        }
        cursor = (
            self._db.user_words.find(query)
            .sort("due_at", ASCENDING)
            .limit(limit)
        )
        return [self._normalise_user_word(doc) for doc in cursor]

    def completed_list(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self._db.user_words.find({"user_id": user_id, "status": "completed"}).sort(
            "updated_at", DESCENDING
        )
        return [self._normalise_user_word(doc) for doc in cursor]

    def get_stats_today(self, user_id: str) -> Optional[Dict[str, Any]]:
        today = date.today().isoformat()
        return self.get_user_stats_daily(user_id, today)

    def get_total_stats(self, user_id: str) -> Dict[str, int]:
        aggregation = list(
            self._db.user_words.aggregate(
                [
                    {"$match": {"user_id": user_id}},
                    {
                        "$group": {
                            "_id": "$status",
                            "count": {"$sum": 1},
                        }
                    },
                ]
            )
        )
        counts = {row["_id"]: row["count"] for row in aggregation}
        return {
            "learned": counts.get("new", 0) + counts.get("learning", 0) + counts.get("queued", 0) + counts.get("completed", 0),
            "completed": counts.get("completed", 0),
            "in_queue": counts.get("queued", 0) + counts.get("learning", 0),
        }

    def noun_hints(self, user_id: str, *, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        cursor = self._db.user_words.find({"user_id": user_id, "item_type": "noun"}).sort("updated_at", DESCENDING)
        hints: List[Dict[str, Any]] = []
        for doc in cursor:
            noun = doc.get("item_id")
            noun_doc = self.get_noun(noun) if noun else None
            if noun_doc:
                enriched = dict(noun_doc)
                enriched["added_at"] = doc.get("added_at")
                enriched["updated_at"] = doc.get("updated_at")
                hints.append(enriched)
            if limit and len(hints) >= limit:
                break
        return hints

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------
    def add_prompt(self, prompt_data: Dict[str, Any]) -> str:
        prompt_id = prompt_data.get("id") or str(uuid.uuid4())
        doc = {
            "_id": prompt_id,
            "id": prompt_id,
            "level": prompt_data["level"],
            "en": prompt_data["en"],
            "de": prompt_data["de"],
            "tags": prompt_data.get("tags", []),
            "word_uids": prompt_data.get("word_uids", []),
            "created_at": _coerce_datetime(prompt_data.get("created_at"), default=datetime.utcnow()),
        }
        self._db.prompts.replace_one({"_id": prompt_id}, doc, upsert=True)
        return prompt_id

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        doc = self._db.prompts.find_one({"_id": prompt_id})
        if not doc:
            return None
        return {
            "id": doc["id"],
            "level": doc.get("level"),
            "en": doc.get("en"),
            "de": doc.get("de"),
            "tags": doc.get("tags", []),
            "word_uids": doc.get("word_uids", []),
            "created_at": doc.get("created_at"),
        }

    def add_prompt_word(self, prompt_word_data: Dict[str, Any]) -> None:
        prompt_id = prompt_word_data["prompt_id"]
        word_uid = prompt_word_data.get("word_uid")
        if not word_uid:
            word_uid = self._ensure_word_index(prompt_word_data["item_type"], prompt_word_data["item_id"])
        self._db.prompts.update_one({"_id": prompt_id}, {"$addToSet": {"word_uids": word_uid}})

    def get_prompt_word(self, prompt_id: str, word_uid: str) -> Optional[Dict[str, Any]]:
        doc = self._db.prompts.find_one({"_id": prompt_id, "word_uids": word_uid})
        if not doc:
            return None
        return {"prompt_id": prompt_id, "word_uid": word_uid}

    def get_prompts(
        self,
        item_type: Optional[str] = None,
        item_id: Optional[str] = None,
        level: Optional[str] = None,
        count: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if item_type and item_id:
            query["word_uids"] = self._ensure_word_index(item_type, item_id)
        if level:
            query["level"] = level
        cursor = self._db.prompts.find(query).sort("created_at", DESCENDING)
        if count:
            cursor = cursor.limit(count)
        prompts: List[Dict[str, Any]] = []
        for doc in cursor:
            prompts.append(
                {
                    "id": doc.get("id"),
                    "level": doc.get("level"),
                    "en": doc.get("en"),
                    "de": doc.get("de"),
                    "tags": doc.get("tags", []),
                    "word_uids": doc.get("word_uids", []),
                    "created_at": doc.get("created_at"),
                }
            )
        return prompts
