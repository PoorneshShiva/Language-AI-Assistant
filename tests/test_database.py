import os
import sqlite3
import unittest
from src.lexilearn.database import Database, get_db_connection

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_name = "test_lexilearn.db"
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        self.conn = get_db_connection(self.db_name)
        self.db = Database(self.conn)
        self.db.create_tables()

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_verb_operations(self):
        verb_data = {
            "infinitive": "essen",
            "present": {"ich": "esse", "du": "isst", "er/sie/es": "isst", "wir": "essen", "ihr": "esst", "sie/Sie": "essen"},
            "present_perfect": ["hat gegessen"],
            "singular_present_tense": ["isst"],
            "simple_past": ["aß"],
            "is_separable": False,
            "is_regular": False,
            "english_alternative": ["to eat"]
        }
        self.db.add_verb(verb_data)
        retrieved_verb = self.db.get_verb("essen")
        self.assertIsNotNone(retrieved_verb)
        self.assertEqual(retrieved_verb["infinitive"], verb_data["infinitive"])
        self.assertEqual(retrieved_verb["present_perfect"], verb_data["present_perfect"])

    def test_noun_operations(self):
        noun_data = {
            "noun": "Haus",
            "plural": "Häuser",
            "gender": "das",
            "case_forms": {"nominative": "Haus", "accusative": "Haus"},
            "english_translation": "house",
            "is_irregular": True
        }
        self.db.add_noun(noun_data)
        retrieved_noun = self.db.get_noun("Haus")
        self.assertIsNotNone(retrieved_noun)
        self.assertEqual(retrieved_noun["noun"], noun_data["noun"])
        self.assertEqual(retrieved_noun["case_forms"], noun_data["case_forms"])

    def test_adjective_operations(self):
        adjective_data = {
            "adjective": "schön",
            "comparative": "schöner",
            "superlative": "am schönsten",
            "english_translation": "beautiful",
            "is_regular": True,
            "is_comparable": True
        }
        self.db.add_adjective(adjective_data)
        retrieved_adjective = self.db.get_adjective("schön")
        self.assertIsNotNone(retrieved_adjective)
        self.assertEqual(retrieved_adjective["adjective"], adjective_data["adjective"])

    def test_adverb_operations(self):
        adverb_data = {
            "adverb": "schnell",
            "english_translation": "fast",
            "adverb_type": "modal",
            "is_comparable": True
        }
        self.db.add_adverb(adverb_data)
        retrieved_adverb = self.db.get_adverb("schnell")
        self.assertIsNotNone(retrieved_adverb)
        self.assertEqual(retrieved_adverb["adverb"], adverb_data["adverb"])

    def test_preposition_operations(self):
        preposition_data = {
            "preposition": "in",
            "english_translation": "in",
            "case_governed": "mixed",
            "preposition_type": "local"
        }
        self.db.add_preposition(preposition_data)
        retrieved_preposition = self.db.get_preposition("in")
        self.assertIsNotNone(retrieved_preposition)
        self.assertEqual(retrieved_preposition["preposition"], preposition_data["preposition"])

    def test_conjunction_operations(self):
        conjunction_data = {
            "conjunction": "und",
            "english_translation": "and",
            "conjunction_type": "coordinating"
        }
        self.db.add_conjunction(conjunction_data)
        retrieved_conjunction = self.db.get_conjunction("und")
        self.assertIsNotNone(retrieved_conjunction)
        self.assertEqual(retrieved_conjunction["conjunction"], conjunction_data["conjunction"])

    def test_user_operations(self):
        user_data = {"email": "test@example.com", "display_name": "Test User"}
        user_id = self.db.add_app_user(user_data)
        retrieved_user = self.db.get_app_user(user_id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user['email'], user_data['email'])

        settings_data = {"user_id": user_id, "level": "advanced", "daily_goal": 50}
        self.db.add_user_settings(settings_data)
        retrieved_settings = self.db.get_user_settings(user_id)
        self.assertIsNotNone(retrieved_settings)
        self.assertEqual(retrieved_settings['daily_goal'], settings_data['daily_goal'])

    def test_word_index_operations(self):
        word_uid = self.db.add_word_index({"item_type": "verb", "item_id": "gehen"})
        retrieved_word_index = self.db.get_word_index(word_uid)
        self.assertIsNotNone(retrieved_word_index)
        self.assertEqual(retrieved_word_index['item_id'], "gehen")

    def test_practice_operations(self):
        user_data = {"email": "test@example.com", "display_name": "Test User"}
        user_id = self.db.add_app_user(user_data)
        word_uid = self.db.add_word_index({"item_type": "verb", "item_id": "gehen"})
        
        user_word_data = {"user_id": user_id, "word_uid": word_uid, "status": "learning"}
        self.db.add_user_word(user_word_data)
        retrieved_user_word = self.db.get_user_word(user_id, word_uid)
        self.assertIsNotNone(retrieved_user_word)
        self.assertEqual(retrieved_user_word['status'], user_word_data['status'])

        session_data = {"user_id": user_id}
        session_id = self.db.add_practice_session(session_data)
        retrieved_session = self.db.get_practice_session(session_id)
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session['user_id'], user_id)

        prompt_data = {"id": "p1", "level": "beginner", "en": "to go", "de": "gehen", "tags": ["verb"]}
        self.db.add_prompt(prompt_data)
        retrieved_prompt = self.db.get_prompt("p1")
        self.assertIsNotNone(retrieved_prompt)
        self.assertEqual(retrieved_prompt['de'], "gehen")

        event_data = {
            "session_id": session_id,
            "user_id": user_id,
            "word_uid": word_uid,
            "prompt_id": "p1",
            "level_at_time": "beginner",
            "confidence": "Good",
            "expected": "gehen",
            "answer": "gehen",
            "correct": True,
            "issues": [],
            "normalized": {"answer": "gehen", "expected": "gehen"}
        }
        event_id = self.db.add_practice_event(event_data)
        retrieved_event = self.db.get_practice_event(event_id)
        self.assertIsNotNone(retrieved_event)
        self.assertEqual(retrieved_event['correct'], 1)

        prompt_word_data = {"prompt_id": "p1", "word_uid": word_uid}
        self.db.add_prompt_word(prompt_word_data)
        retrieved_prompt_word = self.db.get_prompt_word("p1", word_uid)
        self.assertIsNotNone(retrieved_prompt_word)
        self.assertEqual(retrieved_prompt_word['prompt_id'], "p1")

    def test_stats_operations(self):
        user_data = {"email": "test@example.com", "display_name": "Test User"}
        user_id = self.db.add_app_user(user_data)
        today = "2025-09-18"
        stats_data = {"user_id": user_id, "day": today, "learned": 5, "practiced": 10, "completed": 2}
        self.db.add_user_stats_daily(stats_data)
        retrieved_stats = self.db.get_user_stats_daily(user_id, today)
        self.assertIsNotNone(retrieved_stats)
        self.assertEqual(retrieved_stats['learned'], 5)

if __name__ == '__main__':
    unittest.main()