import strawberry
from lexilearn.graphql.queries.grammar_queries import GrammarQuery
from lexilearn.graphql.queries.app_queries import AppQuery
from lexilearn.graphql.mutations.app_mutations import AppMutation

@strawberry.type
class Query(GrammarQuery, AppQuery):
    pass

@strawberry.type
class Mutation(AppMutation):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)