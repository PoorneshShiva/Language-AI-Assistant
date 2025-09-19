import json

def get_verb(conn, infinitive):
    cursor = conn.cursor()
    print(f"Getting verb: {infinitive}")
    cursor.execute("SELECT * FROM verbs WHERE infinitive = ?", (infinitive,))
    row = cursor.fetchone()
    if row:
        columns = [description[0] for description in cursor.description]
        verb_data = dict(zip(columns, row))
        # Convert list-like strings back to lists
        verb_data['present_perfect'] = json.loads(verb_data['present_perfect'])
        verb_data['singular_present_tense'] = json.loads(verb_data['singular_present_tense'])
        verb_data['simple_past'] = json.loads(verb_data['simple_past'])
        verb_data['english_alternative'] = json.loads(verb_data['english_alternative'])
        return verb_data
    return None

def add_verb(conn, verb_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO verbs (infinitive, present_perfect, singular_present_tense, simple_past, is_separable, is_regular, english_alternative)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        verb_data['infinitive'],
        json.dumps(verb_data['present_perfect']),
        json.dumps(verb_data['singular_present_tense']),
        json.dumps(verb_data['simple_past']),
        verb_data['is_separable'],
        verb_data['is_regular'],
        json.dumps(verb_data['english_alternative'])
    ))
    conn.commit()