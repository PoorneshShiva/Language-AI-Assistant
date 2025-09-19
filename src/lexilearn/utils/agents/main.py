from langgraph.graph import StateGraph, END, START

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Send

from lexilearn.utils.agents.system_prompts import SysPrompts
from lexilearn.utils.agents.nodes import Nodes, GermanGrammerDetails, UserQuery



from lexilearn.database import Database, get_db_connection

class AgenticMain():

    def __init__(self, db: Database | None = None):
        """Initialize the agent graph helpers."""
        if db is None:
            self.db = Database(get_db_connection())
            self._owns_db = True
        else:
            self.db = db
            self._owns_db = False
        self.nodes = Nodes(self.db)

    def close(self):
        if getattr(self, "_owns_db", False):
            self.db.close()

    def build_german_graph(self):
        builder = StateGraph(GermanGrammerDetails, input=UserQuery)
        # builder = StateGraph(GermanGrammerDetails, )
        # builder = StateGraph(PartOfSpeech, input=UserQuery)

        builder.add_node("Part of Speech", self.nodes.part_of_speech)
        # builder.add_node("
        # builder.add_node("finalizer", self.nodes.finalizer)

        builder.add_edge(START, "Part of Speech")
        # builder.add_edge("Part of Speech", END)




        # builder.add_edge("part_of_speech", "verb_conjugation")
        # builder.add_edge("part_of_speech", "finalizer")


        # builder.add_edge(START, "Translation")
        # builder.add_node("Translation", self.nodes.translation)
        # builder.add_edge("Translation", END)



        # builder.add_node("Adverb", self.nodes.adverbs)
        # builder.add_edge("Adverb", END)

        builder.add_node("Verb Conjugation", self.nodes.verb_conjugation)
        # builder.add_conditional_edges("Part of Speech", self.nodes.send_queries, ["Verb Conjugation"])

        # builder.add_edge(START, "Verb Conjugation")


        builder.add_node("Noun", self.nodes.noun)



        builder.add_node("Adjective", self.nodes.adjective)
        builder.add_conditional_edges("Part of Speech", self.nodes.send_queries, ["Verb Conjugation", 
        "Adjective", "Noun", END
        ])
        builder.add_edge("Verb Conjugation", END)
        builder.add_edge("Adjective", END)
        builder.add_edge("Noun", END)


        # builder.add_edge(START, "translation")
        # builder.add_edge("translation", "finalizer")

        # builder.add_edge("finalizer", END)

        memory = MemorySaver()
        # app = builder.compile(checkpointer=memory, interrupt_before=["finalizer"])
        app = builder.compile()
        return app
