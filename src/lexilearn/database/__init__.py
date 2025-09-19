import sqlite3
from lexilearn.database.schema import create_tables
from lexilearn.database.operations import verbs, nouns, users, practice, misc

class Database:
    def __init__(self, conn):
        self.conn = conn
        # Enable foreign key support
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def create_tables(self):
        create_tables(self.conn)

    def close(self):
        self.conn.close()

    # Verbs
    def get_verb(self, infinitive):
        return verbs.get_verb(self.conn, infinitive)

    def add_verb(self, verb_data):
        return verbs.add_verb(self.conn, verb_data)

    # Nouns
    def get_noun(self, noun):
        return nouns.get_noun(self.conn, noun)

    def add_noun(self, noun_data):
        return nouns.add_noun(self.conn, noun_data)

    # Users
    def get_app_user(self, user_id):
        return users.get_app_user(self.conn, user_id)

    def add_app_user(self, user_data):
        return users.add_app_user(self.conn, user_data)

    def get_user_settings(self, user_id):
        return users.get_user_settings(self.conn, user_id)

    def add_user_settings(self, settings_data):
        return users.add_user_settings(self.conn, settings_data)

    def get_user_stats_daily(self, user_id, day):
        return users.get_user_stats_daily(self.conn, user_id, day)

    def add_user_stats_daily(self, stats_data):
        return users.add_user_stats_daily(self.conn, stats_data)

    # Practice
    def get_user_word(self, user_id, word_uid):
        return practice.get_user_word(self.conn, user_id, word_uid)

    def add_user_word(self, user_word_data):
        return practice.add_user_word(self.conn, user_word_data)

    def get_practice_session(self, session_id):
        return practice.get_practice_session(self.conn, session_id)

    def add_practice_session(self, session_data):
        return practice.add_practice_session(self.conn, session_data)

    def get_practice_event(self, event_id):
        return practice.get_practice_event(self.conn, event_id)

    def add_practice_event(self, event_data):
        return practice.add_practice_event(self.conn, event_data)

    # Misc
    def get_adjective(self, adjective):
        return misc.get_adjective(self.conn, adjective)
    
    def add_adjective(self, adjective_data):
        return misc.add_adjective(self.conn, adjective_data)

    def get_adverb(self, adverb):
        return misc.get_adverb(self.conn, adverb)

    def add_adverb(self, adverb_data):
        return misc.add_adverb(self.conn, adverb_data)

    def get_preposition(self, preposition):
        return misc.get_preposition(self.conn, preposition)

    def add_preposition(self, preposition_data):
        return misc.add_preposition(self.conn, preposition_data)

    def get_conjunction(self, conjunction):
        return misc.get_conjunction(self.conn, conjunction)

    def add_conjunction(self, conjunction_data):
        return misc.add_conjunction(self.conn, conjunction_data)

    def get_word_index(self, word_uid):
        return misc.get_word_index(self.conn, word_uid)

    def add_word_index(self, word_index_data):
        return misc.add_word_index(self.conn, word_index_data)

    def get_prompt(self, prompt_id):
        return misc.get_prompt(self.conn, prompt_id)

    def add_prompt(self, prompt_data):
        return misc.add_prompt(self.conn, prompt_data)

    def get_prompt_word(self, prompt_id, word_uid):
        return misc.get_prompt_word(self.conn, prompt_id, word_uid)

    def add_prompt_word(self, prompt_word_data):
        return misc.add_prompt_word(self.conn, prompt_word_data)


# Dependency to get a database connection
def get_db_connection(db_name="lexilearn.db"):
    conn = sqlite3.connect(db_name, check_same_thread=False)
    return conn