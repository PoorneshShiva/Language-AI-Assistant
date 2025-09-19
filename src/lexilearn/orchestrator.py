from lexilearn.database import Database
from lexilearn.utils.agents.main import AgenticMain
from lexilearn.models.common import UserQuery

def run_pipeline(user_id: str, text: str):
    db = Database()
    agent_main = AgenticMain(db)

    # Step 1: Save submission
    sub_id = db.save_submission(user_id, text)

    # Step 2 & 3: Detect and Enrich words
    agent = agent_main.build_german_graph()
    result = agent.invoke(UserQuery(query=text))

    enriched_words = []
    if hasattr(result, "verbs_info"):
        for verb_info in result.verbs_info or []:
            word_data = {
                "lemma": verb_info.get("infinitive"),
                "pos": "VERB",
                "translations_en": verb_info.get("english_alternative", []),
                "grammar": {"verb": verb_info},
            }
            enriched_words.append(word_data)

    if hasattr(result, "nouns_info"):
        for noun_info in result.nouns_info or []:
            word_data = {
                "lemma": noun_info.get("noun"),
                "pos": "NOUN",
                "translations_en": [noun_info.get("english_translation")],
                "grammar": {"noun": noun_info},
            }
            enriched_words.append(word_data)

    if hasattr(result, "adjectives_info"):
        for adj_info in result.adjectives_info or []:
            word_data = {
                "lemma": adj_info.get("adjective"),
                "pos": "ADJ",
                "translations_en": [adj_info.get("english_translation")],
                "grammar": {"adjective": adj_info},
            }
            enriched_words.append(word_data)

    unique_lemmas = { (w["lemma"], w["pos"]): w for w in enriched_words }.values()

    for word_data in unique_lemmas:
        if not word_data["lemma"]:
            continue
        word = db.upsert_word(word_data)
        db.upsert_user_word_progress({
            "user_id": user_id,
            "word_id": word["_id"],
        })

    db.close()
    agent_main.close()

    return {"status": "success", "submission_id": sub_id}
