def create_tables(conn):
    cursor = conn.cursor()

    # Existing tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verbs (
        infinitive TEXT PRIMARY KEY,
        present_perfect TEXT,
        singular_present_tense TEXT,
        simple_past TEXT,
        is_separable BOOLEAN,
        is_regular BOOLEAN,
        english_alternative TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nouns (
        noun TEXT PRIMARY KEY,
        plural TEXT,
        gender TEXT,
        case_forms TEXT,
        english_translation TEXT,
        is_irregular BOOLEAN
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adjectives (
        adjective TEXT PRIMARY KEY,
        comparative TEXT,
        superlative TEXT,
        english_translation TEXT,
        is_regular BOOLEAN,
        is_comparable BOOLEAN
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adverbs (
        adverb TEXT PRIMARY KEY,
        english_translation TEXT,
        adverb_type TEXT,
        is_comparable BOOLEAN
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prepositions (
        preposition TEXT PRIMARY KEY,
        english_translation TEXT,
        case_governed TEXT,
        preposition_type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conjunctions (
        conjunction TEXT PRIMARY KEY,
        english_translation TEXT,
        conjunction_type TEXT
    )
    """)

    # New tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_user (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        display_name TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id TEXT PRIMARY KEY,
        level TEXT NOT NULL,
        daily_goal INTEGER NOT NULL,
        style TEXT NOT NULL,
        review_enabled BOOLEAN NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS word_index (
        word_uid TEXT PRIMARY KEY,
        item_type TEXT NOT NULL,
        item_id TEXT NOT NULL,
        UNIQUE (item_type, item_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_word (
        user_id TEXT NOT NULL,
        word_uid TEXT NOT NULL,
        status TEXT NOT NULL,
        due_at TEXT,
        interval_days REAL,
        stability REAL,
        difficulty REAL,
        lapses INTEGER NOT NULL,
        last_result TEXT,
        last_prompt_id TEXT,
        added_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (user_id, word_uid),
        FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE,
        FOREIGN KEY (word_uid) REFERENCES word_index(word_uid) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_word_due ON user_word(user_id, status, due_at)
    WHERE status IN ('queued','learning') AND due_at IS NOT NULL;
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_word_status ON user_word(user_id, status);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS practice_session (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        started_at TEXT NOT NULL,
        ended_at TEXT,
        FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS practice_event (
        id TEXT PRIMARY KEY,
        session_id TEXT,
        user_id TEXT NOT NULL,
        word_uid TEXT NOT NULL,
        prompt_id TEXT,
        level_at_time TEXT NOT NULL,
        confidence TEXT,
        expected TEXT,
        answer TEXT,
        correct BOOLEAN,
        issues TEXT,
        normalized TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES practice_session(id) ON DELETE SET NULL,
        FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE,
        FOREIGN KEY (word_uid) REFERENCES word_index(word_uid) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_practice_event_user_time ON practice_event(user_id, created_at DESC);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_practice_event_word ON practice_event(user_id, word_uid);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompt (
        id TEXT PRIMARY KEY,
        level TEXT NOT NULL,
        en TEXT NOT NULL,
        de TEXT NOT NULL,
        tags TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompt_word (
        prompt_id TEXT NOT NULL,
        word_uid TEXT NOT NULL,
        PRIMARY KEY (prompt_id, word_uid),
        FOREIGN KEY (prompt_id) REFERENCES prompt(id) ON DELETE CASCADE,
        FOREIGN KEY (word_uid) REFERENCES word_index(word_uid) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_prompt_level ON prompt(level);
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_stats_daily (
        user_id TEXT NOT NULL,
        day TEXT NOT NULL,
        learned INTEGER NOT NULL,
        practiced INTEGER NOT NULL,
        completed INTEGER NOT NULL,
        PRIMARY KEY (user_id, day),
        FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE
    )
    """)

    conn.commit()