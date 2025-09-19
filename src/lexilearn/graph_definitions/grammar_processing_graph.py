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
    """Creates and compiles the grammar processing LangGraph."""
    nodes_instance = Nodes()

    builder = StateGraph(GermanGrammarDetails, input=UserQuery)

    builder.add_node("part_of_speech", nodes_instance.part_of_speech)
    builder.add_node("verb_conjugation", nodes_instance.verb_conjugation)
    builder.add_node("noun", nodes_instance.noun)
    builder.add_node("adjective", nodes_instance.adjective)
    builder.add_node("adverbs", nodes_instance.adverbs)
    builder.add_node("prepositions", nodes_instance.prepositions)
    builder.add_node("conjunctions", nodes_instance.conjunctions)

    builder.add_edge(START, "part_of_speech")

    builder.add_conditional_edges(
        "part_of_speech",
        nodes_instance.send_queries,
    )

    builder.add_edge("verb_conjugation", END)
    builder.add_edge("adjective", END)
    builder.add_edge("noun", END)
    builder.add_edge("adverbs", END)
    builder.add_edge("prepositions", END)
    builder.add_edge("conjunctions", END)

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