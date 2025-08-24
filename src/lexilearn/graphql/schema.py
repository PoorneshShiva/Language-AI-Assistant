"""GraphQL Schema for LexiLearn."""
import strawberry
# Updated import path for Mutation
from lexilearn.graphql.mutations.grammar_mutations import Mutation
# Import queries here if you add them: from .queries import Query # Assuming queries would also be in a subfolder
from .queries.grammar_queries import GrammarQuery # Importing the new Query type

# If you had queries, you would define a Query type and pass it to the Schema:
# @strawberry.type
# class Query:
#     @strawberry.field
#     def hello(self) -> str:
#         return "world"

# schema = strawberry.Schema(query=Query, mutation=Mutation)

schema = strawberry.Schema(
    query=GrammarQuery, 
    mutation=Mutation
) # Only mutations for now

# You might also have subscriptions:
# from .subscriptions import SubscriptionType # Example
# schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=SubscriptionType)
