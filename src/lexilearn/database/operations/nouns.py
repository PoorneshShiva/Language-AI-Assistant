import json

def get_noun(conn, noun):
    cursor = conn.cursor()
    print(f"Getting noun: {noun}")
    cursor.execute("SELECT * FROM nouns WHERE noun = ?", (noun,))
    row = cursor.fetchone()
    if row:
        # Convert case_forms back to dictionary
        row = list(row)
        row[3] = json.loads(row[3])
        return dict(zip([description[0] for description in cursor.description], row))
    return None

def add_noun(conn, noun_data):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO nouns (noun, plural, gender, case_forms, english_translation, is_irregular)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        noun_data['noun'],
        noun_data['plural'],
        noun_data['gender'],
        json.dumps(noun_data['case_forms']),
        noun_data['english_translation'],
        noun_data['is_irregular']
    ))
    conn.commit()