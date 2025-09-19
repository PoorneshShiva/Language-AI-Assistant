# from trustcall import create_extractor
# from langgraph.prebuilt import create_react_agent

import spacy
import operator
from typing import Literal, List, NewType, Dict
from pydantic import BaseModel, Field 
from typing import Annotated, Optional
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage, HumanMessage
from lexilearn.utils.agents.system_prompts import SysPrompts
from lexilearn.database import Database
# from langgraph.graph.message import add_messages

from langgraph.types import Send

from langchain_ollama import ChatOllama

# Import BaseModel classes from common.py
from lexilearn.models.common import (
    UserQuery, LanguageClass, PartOfSpeech, Cases, Translation,
    GermanAdverbDetails, GermanPrepositionDetails, GermanVerbsDetails,
    GermanAdjectiveDetails, GermanNounDetails, GermanConjunctionDetails,
    GermanGrammerDetails
)


class Nodes:
    def __init__(self, db):
        self.sys_prompt = SysPrompts()
        self.llm = ChatOllama(
            model="gemma3",
            temperature=0,
            num_threads=29,
            num_gpu=1
        )
        try:
            self.nlp = spacy.load("de_core_news_lg")
        except OSError:
            print("Downloading language model for the first time. This may take a few minutes.")
            spacy.cli.download("de_core_news_lg")
            self.nlp = spacy.load("de_core_news_lg")
        self.db = db if isinstance(db, Database) else Database(db)

    def get_lemma(self, word: str) -> str:
        doc = self.nlp(word)
        return doc[0].lemma_


    def part_of_speech(self, state: UserQuery) -> LanguageClass:
        """Identifies parts of speech in a query using spaCy."""
        try:
            nlp = spacy.load("de_core_news_lg")
        except OSError:
            print("Downloading language model for the first time. This may take a few minutes.")
            spacy.cli.download("de_core_news_lg")
            nlp = spacy.load("de_core_news_lg")

        query = state.query
        doc = nlp(query)

        verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
        adjectives = [token.lemma_ for token in doc if token.pos_ == "ADJ"]
        adverbs = [token.lemma_ for token in doc if token.pos_ == "ADV"]
        prepositions = [token.lemma_ for token in doc if token.pos_ == "ADP"]
        nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
        conjunctions = [token.lemma_ for token in doc if token.pos_ == "CCONJ" or token.pos_ == "SCONJ"]
        interjections = [token.lemma_ for token in doc if token.pos_ == "INTJ"]

        return {
            "verbs": verbs,
            "adjectives": adjectives,
            "adverbs": adverbs,
            "prepositions": prepositions,
            "nouns": nouns,
            "conjunctions": conjunctions,
            "interjections": interjections,
        }
        
    def translation(self, state: UserQuery) -> LanguageClass:
        """ """
        query = state.query
        translation_usr_query = HumanMessage(f"Input (German): {query}")

        
        original_language = state.query_language
        translated_language = state.translated_language
        parser, translation_sys_query = self.sys_prompt.get_translation_query(
                            src=original_language,
                            dest=translated_language,
                            pydantic_format=Translation)
        
        response = self.llm.invoke([translation_sys_query, translation_usr_query])
        formated_response = parser.invoke(response)
        return {"translated_query": formated_response.model_dump()}

    def send_queries(self, state: PartOfSpeech):
        """Condition to send queries to different nodes based on part of speech."""
        verbs = state.verbs
        adjectives = state.adjectives
        adverbs = state.adverbs
        nouns = state.nouns
        prepositions = state.prepositions
        conjunctions = state.conjunctions

        tasks = []
        if verbs:
            tasks.extend([Send("Verb Conjugation", {"verb": verb}) for verb in verbs])
        if adjectives:
            tasks.extend([Send("Adjective", {"adjective": adj}) for adj in adjectives])
        if nouns:
            tasks.extend([Send("Noun", {"noun": noun}) for noun in nouns]) 
        # if adverbs:
        #     tasks.extend([Send("adverbs", {"adverb": adverb}) for adverb in adverbs])
        # if prepositions:
        #     tasks.extend([Send("prepositions", {"preposition": prep}) for prep in prepositions])
        # if conjunctions:
        #     tasks.extend([Send("conjunctions", {"conjunction": conj}) for conj in conjunctions])

        print(f"GEMINI_DEBUG: send_queries tasks: {tasks}")
        if not tasks:
            return []
        return [task for task in tasks]
    

    
    # def verb_conjugation(self, state: PartOfSpeech) ->  GermanGrammerDetails:
    def verb_conjugation(self, state: Dict[str, str]) ->  GermanGrammerDetails:
        verb = state["verb"]
               
        # Check the database first
        cached_verb = self.db.get_verb(verb)
        if cached_verb:
            return {"verbs_info": [cached_verb]}

        # If not in the database, call the LLM
        verb_usr_query = HumanMessage(f"Verb : {verb}")
        parser, verb_conj_sys_query = self.sys_prompt.get_verb_conjugations_query(
                            pydantic_format=GermanVerbsDetails)
        
        response = self.llm.invoke([verb_conj_sys_query, verb_usr_query])
        formated_response = parser.invoke(response)
        # Add the new verb to the database only if it was not cached
        if not cached_verb:
            verb_data = formated_response.model_dump()
            verb_data['infinitive'] = verb
            self.db.add_verb(verb_data)

        return {"verbs_info": [formated_response.model_dump()]}
    
    # def adjective(self, state: PartOfSpeech) ->  GermanGrammerDetails:
    def adjective(self, state: Dict[str, str]) ->  GermanGrammerDetails:
        adj = state["adjective"]
        print(f"DEBUG: adj type: {type(adj)}, value: {adj}")
        lemmatized_adj = self.get_lemma(adj)
        print(f"DEBUG: lemmatized_adj type: {type(lemmatized_adj)}, value: {lemmatized_adj}")
        
        # Check the database first
        cached_adj = self.db.get_adjective(lemmatized_adj)
        if cached_adj:
            return {"adjectives_info": [cached_adj]}

        # If not in the database, call the LLM
        adj_usr_query = HumanMessage(f"Adjective : {lemmatized_adj}")
        parser, adj_sys_query = self.sys_prompt.get_adjectives_query(
                            pydantic_format=GermanAdjectiveDetails)
        
        response = self.llm.invoke([adj_sys_query, adj_usr_query])
        formated_response = parser.invoke(response)

        # Add the new adjective to the database only if it was not cached
        if not cached_adj:
            adjective_data = formated_response.model_dump()
            adjective_data['adjective'] = lemmatized_adj
            self.db.add_adjective(adjective_data)

        return {"adjectives_info": [formated_response.model_dump()]}

    def noun(self, state: Dict[str, str]) ->  GermanGrammerDetails:
        noun_item = state["noun"]
        print(f"DEBUG: noun_item type: {type(noun_item)}, value: {noun_item}")
        lemmatized_noun = self.get_lemma(noun_item)
        print(f"DEBUG: lemmatized_noun type: {type(lemmatized_noun)}, value: {lemmatized_noun}")

        # Check the database first
        cached_noun = self.db.get_noun(lemmatized_noun)
        if cached_noun:
            return {"nouns_info": [cached_noun]}

        # If not in the database, call the LLM
        noun_usr_query = HumanMessage(f"Noun : {lemmatized_noun}")
        parser, noun_sys_query = self.sys_prompt.get_noun_query(
                            pydantic_format=GermanNounDetails)
        
        response = self.llm.invoke([noun_sys_query, noun_usr_query])
        if parser:
            formated_response = parser.invoke(response)

        # Add the new noun to the database
        noun_data = formated_response.model_dump()
        noun_data['noun'] = lemmatized_noun
        self.db.add_noun(noun_data)

        return {"nouns_info": [noun_data]}

    def adverbs(self, state: Dict[str, str]) ->  GermanGrammerDetails:
        adverb = state["adverb"]
        lemmatized_adverb = self.get_lemma(adverb)

        # Check the database first
        cached_adverb = self.db.get_adverb(lemmatized_adverb)
        if cached_adverb:
            return {"adverbs_info": [cached_adverb]}

        # If not in the database, call the LLM
        adverb_usr_query = HumanMessage(f"Adverb : {lemmatized_adverb}")
        parser, adverb_sys_query = self.sys_prompt.get_adverb_query(
                            pydantic_format=GermanAdverbDetails)
        
        response = self.llm.invoke([adverb_sys_query, adverb_usr_query])
        if parser:
            formated_response = parser.invoke(response)

        # Add the new adverb to the database only if it was not cached
        if not cached_adverb:
            adverb_data = formated_response.model_dump()
            adverb_data['adverb'] = lemmatized_adverb
            self.db.add_adverb(adverb_data)

        return {"adverbs_info": [formated_response.model_dump()]}

    def prepositions(self, state: Dict[str, str]) ->  GermanGrammerDetails:
        preposition = state["preposition"]
        lemmatized_preposition = self.get_lemma(preposition)

        # Check the database first
        cached_preposition = self.db.get_preposition(lemmatized_preposition)
        if cached_preposition:
            return {"prepositions_info": [cached_preposition]}

        # If not in the database, call the LLM
        preposition_usr_query = HumanMessage(f"Prepostion : {lemmatized_preposition}")
        parser, preposition_sys_query = self.sys_prompt.get_preposition_query(
                            pydantic_format=GermanPrepositionDetails)
        response = self.llm.invoke([preposition_sys_query, preposition_usr_query])
        if parser:
            formated_response = parser.invoke(response)

        # Add the new preposition to the database only if it was not cached
        if not cached_preposition:
            preposition_data = formated_response.model_dump()
            preposition_data['preposition'] = lemmatized_preposition
            self.db.add_preposition(preposition_data)

        return {"prepositions_info": [formated_response.model_dump()]}

    def conjunctions(self, state: Dict[str, str]) ->  GermanGrammerDetails:
        conjunction = state["conjunction"]
        lemmatized_conjunction = self.get_lemma(conjunction)

        # Check the database first
        cached_conjunction = self.db.get_conjunction(lemmatized_conjunction)
        if cached_conjunction:
            return {"conjunctions_info": [cached_conjunction]}

        # If not in the database, call the LLM
        conjunction_usr_query = HumanMessage(f"Conjunction : {lemmatized_conjunction}")
        parser, conjunction_sys_query = self.sys_prompt.get_conjuction_query(
                            pydantic_format=GermanConjunctionDetails)
         
        response = self.llm.invoke([conjunction_sys_query, conjunction_usr_query])
        if parser:
            formated_response = parser.invoke(response)

        # Add the new conjunction to the database
        conjunction_data = formated_response.model_dump()
        conjunction_data['conjunction'] = lemmatized_conjunction
        self.db.add_conjunction(conjunction_data)

        return {"conjunctions_info": [formated_response.model_dump()]}
