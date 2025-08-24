"""GraphQL Mutations for LexiLearn Grammar processing."""
import strawberry
from typing import cast

# Updated import path for types
from lexilearn.graphql.types.grammar_types import UserQueryInput, GermanGrammarDetailsType
from lexilearn.graph_definitions.grammar_processing_graph import create_grammar_processing_graph
from lexilearn.models.common import UserQuery # For converting input
from lexilearn.models.grammar import GermanGrammarDetails # For casting output

# This is a simplified way to get the graph. 
# In a production app, you might initialize it once and make it available globally
# or through a dependency injection system.
compiled_grammar_graph = create_grammar_processing_graph()

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def process_grammar_query(self,
                                    user_query: UserQueryInput) -> GermanGrammarDetailsType:
        """Processes a user query through the grammar graph and returns detailed analysis."""
        
        pydantic_user_query = {
                "query": user_query.query,
                "query_language": user_query.query_language,
                "translated_language": user_query.translated_language
        }

        # Invoke the graph
        # The graph execution might be blocking. For a production FastAPI app,
        # consider running this in a thread pool executor if it's CPU-bound
        # or ensure the underlying LLM calls are async if I/O-bound.
        # For now, direct invocation is used.
        # TODO: Explore checkpointer for stateful interactions if needed.
        # config = {"configurable": {"thread_id": "some-unique-id-per-user-or-session"}} 
        # final_state_dict = compiled_grammar_graph.invoke(pydantic_user_query, config=config)
        
        final_state_dict = compiled_grammar_graph.invoke(pydantic_user_query)

        # Ensure the output is the expected Pydantic model. 
        # LangGraph can return dicts or the Pydantic state model directly.
        if isinstance(final_state_dict, dict):
            # If it's a dict, try to parse it into our Pydantic model.
            # This assumes the dict structure matches GermanGrammarDetails.
            final_state_pydantic = GermanGrammarDetails(**final_state_dict)
        elif isinstance(final_state_dict, GermanGrammarDetails):
            final_state_pydantic = final_state_dict
        else:
            # Handle unexpected output type
            # You might want to log this or raise a more specific GraphQL error
            raise Exception(f"Unexpected graph output type: {type(final_state_dict)}")

        # Strawberry will automatically convert the Pydantic model to the GraphQL type
        # because we used strawberry.experimental.pydantic.type for GermanGrammarDetailsType.
        return cast(GermanGrammarDetailsType, final_state_pydantic)
