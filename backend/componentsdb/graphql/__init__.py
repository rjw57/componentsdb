import strawberry

from .context import make_context
from .types import Mutation, Query

__all__ = ["schema", "make_context"]

schema = strawberry.Schema(query=Query, mutation=Mutation)
