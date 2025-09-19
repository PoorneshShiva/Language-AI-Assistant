import strawberry
from lexilearn.graphql.queries.grammar_queries import GrammarQuery
from lexilearn.graphql.queries.app_queries import AppQuery
from lexilearn.graphql.queries.mvp_queries import MvpQuery
from lexilearn.graphql.mutations.app_mutations import AppMutation
from lexilearn.graphql.mutations.mvp_mutations import MvpMutation

@strawberry.type
class Query(GrammarQuery, AppQuery, MvpQuery):
    pass

@strawberry.type
class Mutation(AppMutation, MvpMutation):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)