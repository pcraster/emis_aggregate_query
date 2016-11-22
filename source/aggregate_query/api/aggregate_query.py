from . import api_restful
from .resource import *


api_restful.add_resource(AggregateQueryResource,
    "/aggregate_queries/<int:id>",
    endpoint="aggregate_query")
api_restful.add_resource(AggregateQueriesResource,
    "/aggregate_queries",
    endpoint="aggregate_queries")