import uuid
import datetime

def _row_to_dict(row, cursor_description):
    if row is None:
        return None
    columns = [description[0] for description in cursor_description]
    return dict(zip(columns, row))

def get_app_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM app_user WHERE id = ?", (user_id,))
    return _row_to_dict(cursor.fetchone(), cursor.description)

def add_app_user(conn, user_data):
    cursor = conn.cursor()
    user_id = user_data.get('id', str(uuid.uuid4()))
    created_at = user_data.get('created_at', datetime.datetime.now().isoformat())
    cursor.execute("""
    INSERT INTO app_user (id, email, display_name, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        user_id,
        user_data['email'],
        user_data.get('display_name'),
        created_at
    ))
    conn.commit()
    return user_id

def get_user_settings(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
    return _row_to_dict(cursor.fetchone(), cursor.description)

def add_user_settings(conn, settings_data):
    cursor = conn.cursor()
    updated_at = settings_data.get('updated_at', datetime.datetime.now().isoformat())
    cursor.execute("""
    INSERT INTO user_settings (user_id, level, daily_goal, style, review_enabled, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        settings_data['user_id'],
        settings_data.get('level', 'beginner'),
        settings_data.get('daily_goal', 10),
        settings_data.get('style', 'mixed'),
        settings_data.get('review_enabled', True),
        updated_at
    ))
    conn.commit()

def get_user_stats_daily(conn, user_id, day):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_stats_daily WHERE user_id = ? AND day = ?", (user_id, day))
    return _row_to_dict(cursor.fetchone(), cursor.description)

def add_user_stats_daily(conn, stats_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO user_stats_daily (user_id, day, learned, practiced, completed)
    VALUES (?, ?, ?, ?, ?)
    """, (
        stats_data['user_id'],
        stats_data['day'],
        stats_data.get('learned', 0),
        stats_data.get('practiced', 0),
        stats_data.get('completed', 0)
    ))
    conn.commit()