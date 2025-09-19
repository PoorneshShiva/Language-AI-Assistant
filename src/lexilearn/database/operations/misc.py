import uuid
import datetime
import json

def _row_to_dict(row, cursor_description):
    if row is None:
        return None
    columns = [description[0] for description in cursor_description]
    return dict(zip(columns, row))

def get_adjective(conn, adjective):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM adjectives WHERE adjective = ?", (adjective,))
    row = cursor.fetchone()
    if row:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
    return None

def add_adjective(conn, adjective_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO adjectives (adjective, comparative, superlative, english_translation, is_regular, is_comparable)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        adjective_data['adjective'],
        adjective_data['comparative'],
        adjective_data['superlative'],
        adjective_data['english_translation'],
        adjective_data['is_regular'],
        adjective_data['is_comparable']
    ))
    conn.commit()

def get_adverb(conn, adverb):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM adverbs WHERE adverb = ?", (adverb,))
    row = cursor.fetchone()
    if row:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
    return None

def add_adverb(conn, adverb_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO adverbs (adverb, english_translation, adverb_type, is_comparable)
    VALUES (?, ?, ?, ?)
    """, (
        adverb_data['adverb'],
        adverb_data['english_translation'],
        adverb_data['adverb_type'],
        adverb_data['is_comparable']
    ))
    conn.commit()

def get_preposition(conn, preposition):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prepositions WHERE preposition = ?", (preposition,))
    row = cursor.fetchone()
    if row:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
    return None

def add_preposition(conn, preposition_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO prepositions (preposition, english_translation, case_governed, preposition_type)
    VALUES (?, ?, ?, ?)
    """, (
        preposition_data['preposition'],
        preposition_data['english_translation'],
        preposition_data['case_governed'],
        preposition_data['preposition_type']
    ))
    conn.commit()

def get_conjunction(conn, conjunction):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conjunctions WHERE conjunction = ?", (conjunction,))
    row = cursor.fetchone()
    if row:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
    return None

def add_conjunction(conn, conjunction_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO conjunctions (conjunction, english_translation, conjunction_type)
    VALUES (?, ?, ?)
    """, (
        conjunction_data['conjunction'],
        conjunction_data['english_translation'],
        conjunction_data['conjunction_type']
    ))
    conn.commit()

def get_word_index(conn, word_uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM word_index WHERE word_uid = ?", (word_uid,))
    return _row_to_dict(cursor.fetchone(), cursor.description)

def add_word_index(conn, word_index_data):
    cursor = conn.cursor()
    word_uid = word_index_data.get('word_uid', str(uuid.uuid4()))
    cursor.execute("""
    INSERT INTO word_index (word_uid, item_type, item_id)
    VALUES (?, ?, ?)
    """, (
        word_uid,
        word_index_data['item_type'],
        word_index_data['item_id']
    ))
    conn.commit()
    return word_uid

def get_prompt(conn, prompt_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prompt WHERE id = ?", (prompt_id,))
    row_dict = _row_to_dict(cursor.fetchone(), cursor.description)
    if row_dict and row_dict.get('tags'):
        row_dict['tags'] = json.loads(row_dict['tags'])
    return row_dict

def add_prompt(conn, prompt_data):
    cursor = conn.cursor()
    created_at = prompt_data.get('created_at', datetime.datetime.now().isoformat())
    cursor.execute("""
    INSERT INTO prompt (id, level, en, de, tags, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        prompt_data['id'],
        prompt_data['level'],
        prompt_data['en'],
        prompt_data['de'],
        json.dumps(prompt_data.get('tags', [])),
        created_at
    ))
    conn.commit()

def get_prompt_word(conn, prompt_id, word_uid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prompt_word WHERE prompt_id = ? AND word_uid = ?", (prompt_id, word_uid))
    return _row_to_dict(cursor.fetchone(), cursor.description)

def add_prompt_word(conn, prompt_word_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO prompt_word (prompt_id, word_uid)
    VALUES (?, ?)
    """, (
        prompt_word_data['prompt_id'],
        prompt_word_data['word_uid']
    ))
    conn.commit()