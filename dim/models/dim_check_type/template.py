from typing import Any, Dict

from dim.models.dim_check_type.base import Base


class REPLACE_ME(Base):
    def __init__(
        self,
        project_id,
        dataset,
        table,
    ):
        super().__init__(project_id, dataset, table, "REPLACE_ME_WITH_CHECK_TYPE_NAME")

    def generate_test_sql(self, *, params: Dict[Any, Any]) -> str:
        return super().generate_test_sql(params=params)

    def execute_test_sql(self, sql: str) -> Any:
        return super().execute_test_sql(sql=sql)
