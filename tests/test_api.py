import datetime
import mongomock
import pytest
from fastapi.testclient import TestClient

from lexilearn import database as db_module
from lexilearn.database import Database
from lexilearn.main import app, populate_database


class DummyAgenticGraph:
    def invoke(self, _input):
        return type(
            "AgentResult",
            (),
            {
                "verbs_info": [
                    {
                        "infinitive": "spielen",
                        "english_alternative": ["to play"],
                        "notes": ["Regelmäßiges Verb"],
                        "present": {"ich": "spiele", "du": "spielst"},
                    }
                ],
                "nouns_info": [
                    {
                        "noun": "Haus",
                        "case_forms": {"nominative": "das Haus", "accusative": "das Haus"},
                        "english_translation": "house",
                    }
                ],
                "adjectives_info": [
                    {
                        "adjective": "groß",
                        "notes": ["Adjektivdeklination im Nominativ"],
                    }
                ],
            },
        )()


class DummyAgenticMain:
    def __init__(self, db):
        self.db = db

    def build_german_graph(self):
        return DummyAgenticGraph()

    def close(self):
        pass


class StubCourseBuilder:
    def __init__(self, *_, **__):
        pass

    def generate_assignment(self, **_kwargs):
        return {
            "focus": {
                "grammar": ["Perfekt mit haben"],
                "vocabulary": ["Freizeit"],
                "strategies": ["Chunking"],
            },
            "activities": [
                {
                    "title": "Kurzdialog",
                    "summary": "Übe Fragen zum Wochenende.",
                    "instructions": "Formuliere einen kurzen Dialog mit 'spielen'.",
                    "expected_output": "Ich spiele am Samstag Fußball.",
                    "tips": ["Nutze Präsens"],
                    "iteration_prompt": "Formuliere eine Variante mit einem anderen Verb.",
                }
            ],
            "reflection": ["Welche Verbformen fallen dir schwer?"],
            "real_world_bridge": ["Sprich über Freizeitaktivitäten mit Freunden."],
            "language_bank": [
                {"phrase": "Ich spiele", "usage": "Beginn einer Aussage"}
            ],
        }

    def generate_real_life_prompt(self, **_kwargs):
        return {
            "theme": "Im Café",
            "situation": "Du bestellst Getränke und beschreibst deinen Tag.",
            "role_play": {"you": "Besteller:in", "partner": "Servicekraft"},
            "checklist": ["Begrüßung", "Bestellung", "Small Talk"],
            "language_bank": [
                {"phrase": "Ich hätte gern...", "context": "Bestellung"}
            ],
        }


@pytest.fixture
def client(monkeypatch):
    db_module.reset_client_for_tests()
    mock_client = mongomock.MongoClient()
    db_module._MONGO_CLIENT = mock_client  # type: ignore[attr-defined]
    database = Database(db_module.get_db_connection())
    database.create_tables()
    populate_database(database)

    # Additional seed data for tests
    database.add_verb({
        "infinitive": "spielen",
        "present": {"ich": "spiele"},
        "present_perfect": ["hat gespielt"],
        "singular_present_tense": ["spielt"],
        "simple_past": ["spielte"],
        "is_separable": False,
        "is_regular": True,
        "english_alternative": ["to play"],
    })
    database.add_word_index({"item_type": "verb", "item_id": "spielen"})

    database.add_noun({
        "noun": "Haus",
        "plural": "Häuser",
        "gender": "das",
        "case_forms": {"nominative": "Haus", "accusative": "Haus", "dative": "Haus", "genitive": "Hauses"},
        "english_translation": "house",
        "is_irregular": False,
    })
    database.add_word_index({"item_type": "noun", "item_id": "Haus"})

    # Seed user progress
    now = datetime.datetime.utcnow()
    database.add_user_word({
        "user_id": "test_user",
        "item_type": "verb",
        "item_id": "spielen",
        "status": "queued",
        "due_at": now - datetime.timedelta(hours=1),
        "interval_days": 1,
        "stability": 0.5,
    })
    database.add_user_word({
        "user_id": "test_user",
        "item_type": "noun",
        "item_id": "Haus",
        "status": "learning",
        "due_at": now - datetime.timedelta(days=1),
        "interval_days": 2,
        "stability": 0.6,
        "lapses": 1,
    })

    database.add_user_settings({
        "user_id": "test_user",
        "level": "beginner",
        "daily_goal": 10,
        "style": "mixed",
        "review_enabled": True,
    })

    monkeypatch.setattr("lexilearn.main.AgenticMain", DummyAgenticMain)
    monkeypatch.setattr("lexilearn.rest.words.AgenticMain", DummyAgenticMain)
    monkeypatch.setattr("lexilearn.rest.learn.CourseBuilder", StubCourseBuilder)

    with TestClient(app) as test_client:
        yield test_client

    db_module.reset_client_for_tests()


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True, "data": {"status": "healthy"}}


def test_random_words_endpoint(client):
    payload = {
        "level": "beginner",
        "exclude_keys": [],
        "preferred_types": ["verb", "noun"],
    }
    response = client.post("/api/v1/words/random", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["item"]["type"] in {"verb", "noun"}


def test_get_words_endpoint(client):
    response = client.get("/api/v1/words?types=verb,noun&limit=5")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert isinstance(body["data"]["items"], list)
    assert any(item["id"] == "spielen" for item in body["data"]["items"])


def test_get_practice_queue_endpoint(client):
    response = client.get("/api/v1/practice/queue?level=beginner")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert len(body["data"]["queue"]) >= 1


def test_post_practice_confidence_endpoint(client):
    payload = {
        "item": {"type": "verb", "id": "spielen"},
        "confidence": "Good",
        "level": "beginner",
        "telemetry": {"correct": True},
    }
    response = client.post("/api/v1/practice/confidence", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["moved_to"] in {"queued", "completed"}
    assert "due_at" in body["data"]["scheduled"]


def test_post_practice_complete_endpoint(client):
    payload = {"item": {"type": "noun", "id": "Haus"}}
    response = client.post("/api/v1/practice/complete", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "completed"


def test_get_settings_endpoint(client):
    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["level"] == "beginner"


def test_patch_settings_endpoint(client):
    payload = {"level": "advanced", "daily_goal": 20}
    response = client.patch("/api/v1/settings", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["level"] == "advanced"
    assert body["data"]["daily_goal"] == 20


def test_get_stats_endpoint(client):
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    body = response.json()
    assert "today" in body["data"]
    assert "totals" in body["data"]


def test_analyze_sentence_endpoint(client):
    payload = {
        "sentence": "Ich spiele am Wochenende Fußball im Park.",
        "level": "beginner",
        "goals": ["Freizeit", "Perfekt"],
    }
    response = client.post("/api/v1/learn/analyze", json=payload)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["analysis_id"]
    assert body["verbs"][0]["lemma"] == "spielen"
    assert "Kasus" in " ".join(body["focus"])


def test_assignment_generation_flow(client):
    analysis = client.post(
        "/api/v1/learn/analyze",
        json={
            "sentence": "Ich spiele am Wochenende Fußball im Park.",
            "level": "beginner",
            "goals": ["Perfekt"],
        },
    ).json()["data"]

    assignment_resp = client.post(
        "/api/v1/learn/assignments",
        json={
            "sentence": "Ich spiele am Wochenende Fußball im Park.",
            "level": "beginner",
            "goals": ["Perfekt"],
            "analysis_id": analysis["analysis_id"],
        },
    )
    assert assignment_resp.status_code == 200
    assignment = assignment_resp.json()["data"]
    assert assignment["assignment_id"]
    assert assignment["activities"]

    update_resp = client.patch(
        f"/api/v1/learn/assignments/{assignment['assignment_id']}",
        json={
            "status": "completed",
            "iteration_feedback": "Bitte Variation",
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()["data"]
    assert updated["iteration"] == 2
    assert updated["status"] == "completed"


def test_scenario_generation(client):
    response = client.post(
        "/api/v1/learn/scenarios",
        json={
            "level": "beginner",
            "theme": "Café",
            "recently_learned": ["Ich spiele"],
        },
    )
    assert response.status_code == 200
    scenario = response.json()["data"]
    assert scenario["theme"]

    listing = client.get("/api/v1/learn/scenarios?limit=5")
    assert listing.status_code == 200
    assert listing.json()["data"]
