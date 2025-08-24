"""Defines the grammar processing graph using LangGraph."""

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver # For persisting state, if needed
from langgraph.constants import Send # Corrected import path for Send

from lexilearn.models.common import UserQuery, PartOfSpeech # Input and intermediate state
from lexilearn.models.grammar import GermanGrammarDetails   # Main graph state
from lexilearn.graph_nodes.grammar_processing_nodes import Nodes # Node implementations

# Placeholder for actual LLM client used by Nodes. 
# Ensure the `llm` instance in grammar_processing_nodes.py is correctly configured.
# from lexilearn.graph_nodes.grammar_processing_nodes import llm # If you want to import it to show it's a dependency


def create_grammar_processing_graph():
    """Creates and compiles the grammar processing LangGraph.

    The graph processes a user query to identify parts oasdff speech, then
    dispatches tasks to specialized nodes for verbs, nouns, and adjectives
    to gather detailed grammatical information.

    Returns:
        A compiled LangGraph application.
    """
    nodes_instance = Nodes() # Instantiate the class containing graph node logic

    # Define the StateGraph. 
    # GermanGrammarDetails will accumulate results from different nodes.
    # UserQuery is the initial input type to the graph.
    builder = StateGraph(GermanGrammarDetails, input=UserQuery)

    # Add nodes to the graph
    # The first argument is a unique name for the node.
    # The second argument is the function or method that implements the node's logic.
    builder.add_node("Part of Speech", nodes_instance.identify_parts_of_speech)
    builder.add_node("Verb Conjugation", nodes_instance.get_verb_details)
    builder.add_node("Noun", nodes_instance.get_noun_details) # As per notebook: builder.add_node("Noun", nodes.noun)
    builder.add_node("Adjective", nodes_instance.get_adjective_details) # As per notebook: builder.add_node("Adjective", nodes.adjective)

    # Define the entry point of the graph
    builder.add_edge(START, "Part of Speech")

    # Conditional edges based on the output of the "Part of Speech" node.
    # The `dispatch_grammar_tasks` method in Nodes class determines which downstream
    # nodes should be called (e.g., "Verb Conjugation", "Adjective", "Noun").
    builder.add_conditional_edges(
        "Part of Speech", 
        nodes_instance.dispatch_grammar_tasks, 
        ["Verb Conjugation", "Adjective", "Noun", END] # Added END as a possible route
    )

    # Edges from specific grammar detail nodes to END, signifying they are terminal for their branch.
    builder.add_edge("Verb Conjugation", END)
    builder.add_edge("Adjective", END)
    builder.add_edge("Noun", END)

    # Compile the graph. A checkpointer can be added for persistence.
    # memory = MemorySaver()
    # app = builder.compile(checkpointer=memory)
    app = builder.compile()

    return app

if __name__ == '__main__':
    # This section is for local testing or demonstration.
    # To visualize or run the graph:
    
    app = create_grammar_processing_graph()

    # 1. Visualize the graph (requires graphviz installed: pip install graphviz)
    try:
        graph_png = app.get_graph().draw_png()
        with open("grammar_processing_graph.png", "wb") as f:
            f.write(graph_png)
        print("Graph visualization saved to grammar_processing_graph.png")
    except Exception as e:
        print(f"Could not generate graph visualization: {e}")
        print("Ensure graphviz is installed (pip install graphviz) and in your system PATH.")

    # 2. Example of how to invoke the graph (replace with actual input):
    print("\nSimulating graph invocation...")
    initial_input = UserQuery(query="Ich spiele das schöne Haus")
    
    # For a stateful graph with checkpointer, you'd manage thread_id for conversations
    # config = {"configurable": {"thread_id": "test-thread-1"}}
    # final_state = app.invoke(initial_input, config)

    # For a non-persistent graph compiled without a checkpointer:
    final_state = app.invoke(initial_input)
    
    print("\nGraph execution finished.")
    print("Final State:")
    if isinstance(final_state, GermanGrammarDetails):
        print(final_state.model_dump_json(indent=2))
    else:
        # If using older LangGraph or different state passing, final_state might be a dict
        import json
        print(json.dumps(final_state, indent=2))

    # To get intermediate steps (if compiled with a checkpointer and using .stream()):
    # print("\nStreaming intermediate steps...")
    # for s in app.stream(initial_input, config):
    #    print(s)
    #    print("----") 