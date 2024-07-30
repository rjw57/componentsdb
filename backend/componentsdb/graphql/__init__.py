import strawberry
from strawberry.extensions import MaxAliasesLimiter, MaxTokensLimiter, QueryDepthLimiter

from .context import make_context
from .types import Mutation, Query

__all__ = ["schema", "make_context"]


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[QueryDepthLimiter(max_depth=15), MaxTokensLimiter(1000), MaxAliasesLimiter(10)],
)
