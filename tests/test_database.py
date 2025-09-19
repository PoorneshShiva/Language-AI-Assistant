import unittest
import datetime
import mongomock

from lexilearn import database as db_module
from lexilearn.database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        db_module.reset_client_for_tests()
        self.mock_client = mongomock.MongoClient()
        db_module._MONGO_CLIENT = self.mock_client  # type: ignore[attr-defined]
        self.db = Database(db_module.get_db_connection())
        self.db.create_tables()

    def tearDown(self):
        db_module.reset_client_for_tests()

    def test_verb_operations(self):
        verb_data = {
            "infinitive": "essen",
            "present": {"ich": "esse", "du": "isst"},
            "present_perfect": ["hat gegessen"],
            "singular_present_tense": ["isst"],
            "simple_past": ["aß"],
            "is_separable": False,
            "is_regular": False,
            "english_alternative": ["to eat"],
            "notes": ["irregular"]
        }
        self.db.add_verb(verb_data)
        retrieved = self.db.get_verb("essen")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["infinitive"], "essen")
        self.assertIn("hat gegessen", retrieved["present_perfect"])
        self.assertEqual(retrieved["notes"], ["irregular"])

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
        retrieved = self.db.get_noun("Haus")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["case_forms"]["nominative"], "Haus")

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
        retrieved = self.db.get_adjective("schön")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["superlative"], "am schönsten")

    def test_user_operations(self):
        user_id = self.db.add_app_user({"email": "test@example.com", "display_name": "Tester"})
        user = self.db.get_app_user(user_id)
        self.assertEqual(user["email"], "test@example.com")

        self.db.add_user_settings({"user_id": user_id, "level": "advanced", "daily_goal": 20})
        settings = self.db.get_user_settings(user_id)
        self.assertEqual(settings["level"], "advanced")
        self.assertEqual(settings["daily_goal"], 20)

    def test_word_index_operations(self):
        word_uid = self.db.add_word_index({"item_type": "verb", "item_id": "gehen"})
        self.assertEqual(word_uid, "verb:gehen")
        retrieved = self.db.get_word_index(word_uid)
        self.assertEqual(retrieved["item_id"], "gehen")

    def test_practice_operations(self):
        user_id = self.db.add_app_user({"email": "test@example.com"})
        word_uid = self.db.add_word_index({"item_type": "verb", "item_id": "gehen"})

        self.db.add_user_word({
            "user_id": user_id,
            "word_uid": word_uid,
            "status": "learning",
            "due_at": datetime.datetime.utcnow(),
            "interval_days": 1,
        })
        user_word = self.db.get_user_word(user_id, word_uid)
        self.assertEqual(user_word["status"], "learning")

        session_id = self.db.add_practice_session({"user_id": user_id})
        self.assertTrue(session_id)

        prompt_id = self.db.add_prompt({
            "id": "p1",
            "level": "beginner",
            "en": "to go",
            "de": "gehen",
            "tags": ["verb"],
            "word_uids": [word_uid],
        })
        prompt = self.db.get_prompt(prompt_id)
        self.assertEqual(prompt["de"], "gehen")

        event_id = self.db.add_practice_event({
            "session_id": session_id,
            "user_id": user_id,
            "word_uid": word_uid,
            "prompt_id": prompt_id,
            "level_at_time": "beginner",
            "confidence": "Good",
            "expected": "gehen",
            "answer": "gehen",
            "correct": True,
            "issues": [],
            "normalized": {"answer": "gehen"}
        })
        event = self.db.get_practice_event(event_id)
        self.assertTrue(event["correct"])

        self.db.add_prompt_word({"prompt_id": prompt_id, "word_uid": word_uid})
        prompt_word = self.db.get_prompt_word(prompt_id, word_uid)
        self.assertEqual(prompt_word["prompt_id"], prompt_id)

    def test_stats_operations(self):
        user_id = self.db.add_app_user({"email": "stats@example.com"})
        today = datetime.date.today().isoformat()
        self.db.add_user_stats_daily({"user_id": user_id, "day": today, "learned": 3, "practiced": 5, "completed": 2})
        stats = self.db.get_user_stats_daily(user_id, today)
        self.assertEqual(stats["learned"], 3)

    def test_assignment_and_scenario_persistence(self):
        user_id = self.db.add_app_user({"email": "assignments@example.com"})
        analysis_id = self.db.save_sentence_analysis(
            user_id,
            "Ich spiele Fußball.",
            {"verbs": [], "nouns": [], "adjectives": [], "notes": []},
            focus=["Verbkonjugation"],
        )
        assignment_id = self.db.create_assignment(
            {
                "user_id": user_id,
                "sentence": "Ich spiele Fußball.",
                "level": "beginner",
                "goals": ["Perfekt"],
                "focus": {"grammar": ["Perfekt"]},
                "activities": [{"title": "Aktivität", "summary": "", "instructions": "", "expected_output": "", "tips": []}],
                "reflection": ["Reflexion"],
                "real_world_bridge": ["Sprich mit Freunden"],
                "language_bank": [{"phrase": "Ich spiele", "usage": "Einstieg"}],
                "analysis_id": analysis_id,
                "analysis_snapshot": {"verbs": []},
            }
        )
        assignment = self.db.get_assignment(assignment_id)
        self.assertEqual(assignment["sentence"], "Ich spiele Fußball.")
        self.db.update_assignment(assignment_id, {"status": "completed"})
        refreshed = self.db.get_assignment(assignment_id)
        self.assertEqual(refreshed["status"], "completed")

        scenario_id = self.db.add_real_life_scenario(
            {
                "user_id": user_id,
                "level": "beginner",
                "theme": "Café",
                "situation": "Bestellung",
                "role_play": {"you": "Gast", "partner": "Servicekraft"},
                "checklist": ["Begrüßung"],
                "language_bank": [{"phrase": "Ich hätte gern", "context": "Bestellung"}],
            }
        )
        scenarios = self.db.list_real_life_scenarios(user_id)
        self.assertTrue(any(scenario["scenario_id"] == scenario_id for scenario in scenarios))


if __name__ == '__main__':
    unittest.main()
