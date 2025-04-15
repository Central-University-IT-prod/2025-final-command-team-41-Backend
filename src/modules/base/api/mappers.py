from src.modules.base.api.schemas import PaginationSchema
from src.modules.base.domain.value_objects import Pagination


class PaginationMapper:
    @staticmethod
    def to_domain(schema: PaginationSchema) -> Pagination:
        return Pagination(limit=schema.count, offset=schema.count * schema.page)
