# This file makes the 'graphql' directory a Python package. 

# from .mutations.grammar_mutations import Mutation
from lexilearn.graphql.queries.grammar_queries import GrammarQuery

__all__ = [
    # "Mutation",
     "GrammarQuery"] 