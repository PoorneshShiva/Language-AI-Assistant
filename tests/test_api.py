from fastapi.testclient import TestClient
from lexilearn.main import app
from lexilearn.database import get_db_connection, Database
import sqlite3
import json
import datetime
import pytest

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    db = Database(conn)
    db.create_tables() # Create tables for the in-memory database

    # Add some dummy data for testing
    user_id = "test_user"
    db.add_app_user({"id": user_id, "email": "test@example.com", "display_name": "Test User"})

    # Add verb and noun and get their UIDs
    spielen_verb_data = {
        "infinitive": "spielen",
        "present": {"ich": "spiele", "du": "spielst", "er/sie/es": "spielt", "wir": "spielen", "ihr": "spielt", "sie/Sie": "spielen"},
        "present_perfect": ["hat gegessen"],
        "singular_present_tense": ["spiele", "spielst", "spielt"],
        "simple_past": ["spielte"],
        "is_separable": False,
        "is_regular": True,
        "english_alternative": ["to play"]
    }
    db.add_verb(spielen_verb_data)
    spielen_verb_uid = db.add_word_index({"item_type": "verb", "item_id": "spielen"})

    haus_noun_data = {
        "noun": "Haus",
        "plural": "Häuser",
        "gender": "das",
        "case_forms": {"nominative": "Haus", "accusative": "Haus", "dative": "Haus", "genitive": "Hauses"},
        "english_translation": "house",
        "is_irregular": False
    }
    db.add_noun(haus_noun_data)
    haus_noun_uid = db.add_word_index({"item_type": "noun", "item_id": "Haus"})

    # Add user_word entries for practice
    db.add_user_word({
        "user_id": user_id,
        "word_uid": spielen_verb_uid,
        "status": "queued",
        "due_at": datetime.datetime.now().isoformat(),
        "interval_days": 1,
        "stability": 0.5,
        "difficulty": 0.5,
        "lapses": 0,
        "added_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    })
    db.add_user_word({
        "user_id": user_id,
        "word_uid": haus_noun_uid,
        "status": "learning",
        "due_at": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat(),
        "interval_days": 2,
        "stability": 0.6,
        "difficulty": 0.4,
        "lapses": 1,
        "added_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    })

    yield conn # Yield the connection directly

    conn.close() # Close the connection after the test

@pytest.fixture
def client_with_db(db_conn):
    def get_test_db_connection():
        yield db_conn # Yield the connection from the fixture

    app.dependency_overrides[get_db_connection] = get_test_db_connection
    yield TestClient(app=app) # Pass app explicitly
    app.dependency_overrides = {} # Clean up overrides after test

def test_health_endpoint(client_with_db):
    response = client_with_db.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True, "data": {"status": "healthy"}}

def test_detect_words_endpoint(client_with_db):
    payload = {
        "sentence": "Ich spiele Fußball.",
        "level": "beginner",
        "exclude_keys": []
    }
    response = client_with_db.post("/api/v1/words/detect", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "detected" in response.json()["data"]
    assert isinstance(response.json()["data"]["detected"], list)

def test_random_words_endpoint(client_with_db):
    payload = {
        "level": "beginner",
        "exclude_keys": [],
        "preferred_types": ["verb", "noun"]
    }
    response = client_with_db.post("/api/v1/words/random", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "item" in response.json()["data"]
    assert response.json()["data"]["item"]["type"] in ["verb", "noun"]
    assert "id" in response.json()["data"]["item"]

def test_get_words_endpoint(client_with_db):
    response = client_with_db.get("/api/v1/words?types=verb,noun&limit=2")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "items" in response.json()["data"]
    assert isinstance(response.json()["data"]["items"], list)
    assert len(response.json()["data"]["items"]) <= 2

def test_get_verb_details_endpoint(client_with_db):
    response = client_with_db.get("/api/v1/verbs/spielen")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert response.json()["data"]["infinitive"] == "spielen"

def test_get_noun_details_endpoint(client_with_db):
    response = client_with_db.get("/api/v1/nouns/Haus")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert response.json()["data"]["noun"] == "Haus"

def test_get_practice_queue_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    response = client_with_db.get("/api/v1/practice/queue?level=beginner")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "queue" in response.json()["data"]
    assert isinstance(response.json()["data"]["queue"], list)
    assert len(response.json()["data"]["queue"]) == 1

def test_post_practice_confidence_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    user_id = "test_user"
    word_uid = db.get_word_index("verb:spielen")["word_uid"]
    user_word_before = db.get_user_word(user_id, word_uid)

    payload = {
        "item": {"type": "verb", "id": "spielen"},
        "confidence": "Good",
        "level": "beginner",
        "telemetry": {"correct": True}
    }
    response = client_with_db.post("/api/v1/practice/confidence", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "scheduled" in response.json()["data"]
    assert "moved_to" in response.json()["data"]

    user_word_after = db.get_user_word(user_id, word_uid)
    assert user_word_after["due_at"] > user_word_before["due_at"]
    assert user_word_after["interval_days"] > user_word_before["interval_days"]

def test_post_practice_complete_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    user_id = "test_user"
    word_uid = db.get_word_index("noun:Haus")["word_uid"]

    payload = {
        "item": {"type": "noun", "id": "Haus"}
    }
    response = client_with_db.post("/api/v1/practice/complete", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert response.json()["data"]["status"] == "completed"

    user_word = db.get_user_word(user_id, word_uid)
    assert user_word["status"] == "completed"

def test_post_practice_review_again_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    user_id = "test_user"
    word_uid = db.get_word_index("verb:spielen")["word_uid"]
    db.conn.execute("UPDATE user_word SET status = 'completed' WHERE user_id = ? AND word_uid = ?", (user_id, word_uid))
    db.conn.commit()

    payload = {
        "item": {"type": "verb", "id": "spielen"}
    }
    response = client_with_db.post("/api/v1/practice/review-again", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert response.json()["data"]["status"] == "queued"

    user_word = db.get_user_word(user_id, word_uid)
    assert user_word["status"] == "queued"

def test_get_completed_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    user_id = "test_user"
    word_uid = db.get_word_index("noun:Haus")["word_uid"]
    db.conn.execute("UPDATE user_word SET status = 'completed' WHERE user_id = ? AND word_uid = ?", (user_id, word_uid))
    db.conn.commit()

    response = client_with_db.get("/api/v1/completed")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "items" in response.json()["data"]
    assert isinstance(response.json()["data"]["items"], list)
    completed_items = response.json()["data"]["items"]
    assert len(completed_items) > 0
    assert any(item["id"] == "Haus" for item in completed_items)

def test_post_ignore_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    user_id = "test_user"
    new_verb_uid = db.add_word_index({"item_type": "verb", "item_id": "lernen"})
    db.add_user_word({"user_id": user_id, "word_uid": new_verb_uid, "status": "new"})

    payload = {
        "item": {"type": "verb", "id": "lernen"}
    }
    response = client_with_db.post("/api/v1/ignore", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert response.json()["data"]["status"] == "ignored"

    user_word = db.get_user_word(user_id, new_verb_uid)
    assert user_word["status"] == "ignored"

def test_delete_ignore_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    user_id = "test_user"
    ignored_verb_uid = db.add_word_index({"item_type": "verb", "item_id": "vergessen"})
    db.add_user_word({"user_id": user_id, "word_uid": ignored_verb_uid, "status": "ignored"})

    payload = {
        "item": {"type": "verb", "id": "vergessen"}
    }
    response = client_with_db.delete("/api/v1/ignore", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert response.json()["data"]["status"] == "unignored"

    user_word = db.get_user_word(user_id, ignored_verb_uid)
    assert user_word["status"] == "new"

def test_get_settings_endpoint(client_with_db):
    response = client_with_db.get("/api/v1/settings")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "level" in response.json()["data"]
    assert "daily_goal" in response.json()["data"]

def test_patch_settings_endpoint(client_with_db, db_conn):
    db = Database(db_conn)
    user_id = "test_user"
    payload = {
        "level": "advanced",
        "daily_goal": 20
    }
    response = client_with_db.patch("/api/v1/settings", json=payload)
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert response.json()["data"]["level"] == "advanced"
    assert response.json()["data"]["daily_goal"] == 20

    user_settings = db.get_user_settings(user_id)
    assert user_settings["level"] == "advanced"
    assert user_settings["daily_goal"] == 20

def test_get_stats_endpoint(client_with_db):
    response = client_with_db.get("/api/v1/stats")
    assert response.status_code == 200
    assert response.json()["ok"] == True
    assert "today" in response.json()["data"]
    assert "totals" in response.json()["data"]