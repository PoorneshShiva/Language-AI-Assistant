import strawberry
from typing import Optional
from lexilearn.utils.agents.main import AgenticMain
from lexilearn.database import Database
from lexilearn.graphql.types.grammar_types import VerbType, NounType, AdjectiveType

@strawberry.type
class GrammarQuery:
    """
    GraphQL Query type for grammar-related operations.
    """
    @strawberry.field
    def process_text(self, info: strawberry.Info, text: str) -> str:
        print(f"GEMINI_DEBUG: Processing text: {text}")
        agent = info.context["agent_main"].build_german_graph()
        result = agent.invoke({"query": text})
        print(f"GEMINI_DEBUG: Agent output: {result}")
        if result is None:
            return "GEMINI_DEBUG: Agent returned None"
        return str(result)

    @strawberry.field
    def get_verb(self, info: strawberry.Info, infinitive: str) -> Optional[VerbType]:
        db = Database(info.context["conn"])
        verb_data = db.get_verb(infinitive)
        if verb_data:
            return VerbType(**verb_data)
        return None

    @strawberry.field
    def get_noun(self, info: strawberry.Info, noun: str) -> Optional[NounType]:
        db = Database(info.context["conn"])
        noun_data = db.get_noun(noun)
        if noun_data:
            return NounType(**noun_data)
        return None

    @strawberry.field
    def get_adjective(self, info: strawberry.Info, adjective: str) -> Optional[AdjectiveType]:
        db = Database(info.context["conn"])
        adjective_data = db.get_adjective(adjective)
        if adjective_data:
            return AdjectiveType(**adjective_data)
        return None