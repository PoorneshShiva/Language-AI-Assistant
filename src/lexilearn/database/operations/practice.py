import uuid
import datetime
import json

def _row_to_dict(row, cursor_description):
    if row is None:
        return None
    columns = [description[0] for description in cursor_description]
    return dict(zip(columns, row))

def get_user_word(conn, user_id, word_uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_word WHERE user_id = ? AND word_uid = ?", (user_id, word_uid))
    return _row_to_dict(cursor.fetchone(), cursor.description)

def add_user_word(conn, user_word_data):
    cursor = conn.cursor()
    added_at = user_word_data.get('added_at', datetime.datetime.now().isoformat())
    updated_at = user_word_data.get('updated_at', datetime.datetime.now().isoformat())
    cursor.execute("""
    INSERT INTO user_word (user_id, word_uid, status, due_at, interval_days, stability, difficulty, lapses, last_result, last_prompt_id, added_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_word_data['user_id'],
        user_word_data['word_uid'],
        user_word_data.get('status', 'new'),
        user_word_data.get('due_at'),
        user_word_data.get('interval_days', 0),
        user_word_data.get('stability', 0.0),
        user_word_data.get('difficulty', 0.0),
        user_word_data.get('lapses', 0),
        user_word_data.get('last_result'),
        user_word_data.get('last_prompt_id'),
        added_at,
        updated_at
    ))
    conn.commit()

def get_practice_session(conn, session_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM practice_session WHERE id = ?", (session_id,))
    return _row_to_dict(cursor.fetchone(), cursor.description)

def add_practice_session(conn, session_data):
    cursor = conn.cursor()
    session_id = session_data.get('id', str(uuid.uuid4()))
    started_at = session_data.get('started_at', datetime.datetime.now().isoformat())
    cursor.execute("""
    INSERT INTO practice_session (id, user_id, started_at, ended_at)
    VALUES (?, ?, ?, ?)
    """, (
        session_id,
        session_data['user_id'],
        started_at,
        session_data.get('ended_at')
    ))
    conn.commit()
    return session_id

def get_practice_event(conn, event_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM practice_event WHERE id = ?", (event_id,))
    row_dict = _row_to_dict(cursor.fetchone(), cursor.description)
    if row_dict:
        if row_dict.get('issues'):
            row_dict['issues'] = json.loads(row_dict['issues'])
        if row_dict.get('normalized'):
            row_dict['normalized'] = json.loads(row_dict['normalized'])
    return row_dict

def add_practice_event(conn, event_data):
    cursor = conn.cursor()
    event_id = event_data.get('id', str(uuid.uuid4()))
    created_at = event_data.get('created_at', datetime.datetime.now().isoformat())
    cursor.execute("""
    INSERT INTO practice_event (id, session_id, user_id, word_uid, prompt_id, level_at_time, confidence, expected, answer, correct, issues, normalized, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        event_data.get('session_id'),
        event_data['user_id'],
        event_data['word_uid'],
        event_data.get('prompt_id'),
        event_data['level_at_time'],
        event_data.get('confidence'),
        event_data.get('expected'),
        event_data.get('answer'),
        event_data.get('correct'),
        json.dumps(event_data['issues']) if event_data.get('issues') else None,
        json.dumps(event_data['normalized']) if event_data.get('normalized') else None,
        created_at
    ))
    conn.commit()
    return event_id