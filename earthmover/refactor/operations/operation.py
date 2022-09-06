import abc

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from earthmover.refactor.earthmover import Earthmover


class Operation:
    """

    """
    def __new__(cls, config, *, earthmover: 'Earthmover'):
        """
        :param config:
        :param earthmover:
        """
        from earthmover.refactor.operations import (
            row as row_operations,
            groupby as groupby_operations,
            dataframe as dataframe_operations,
            column as column_operations
        )

        OPERATION_MAPPING = {
            'join': dataframe_operations.JoinOperation,
            'union': dataframe_operations.UnionOperation,

            'add_columns': column_operations.AddColumnsOperation,
            'modify_columns': column_operations.ModifyColumnsOperation,
            'duplicate_columns': column_operations.DuplicateColumnsOperation,
            'rename_columns': column_operations.RenameColumnsOperation,
            'drop_columns': column_operations.DropColumnsOperation,
            'keep_columns': column_operations.KeepColumnsOperation,
            'combine_columns': column_operations.CombineColumnsOperation,
            'map_values': column_operations.MapValuesOperation,
            'date_format': column_operations.DateFormatOperation,

            'distinct_rows': row_operations.DistinctRowsOperation,
            'filter_rows': row_operations.FilterRowsOperation,

            'group_by_with_count': groupby_operations.GroupByWithCountOperation,
            'group_by_with_ag': groupby_operations.GroupByWithAggOperation,
            'group_by': groupby_operations.GroupByOperation,
        }

        operation = config.get('operation')
        operation_class = OPERATION_MAPPING.get(operation)

        if operation_class is None:
            earthmover.error_handler.throw(
                f"invalid transformation operation `{operation}`"
            )
            raise

        return object.__new__(operation_class)


    def __init__(self, config, *, earthmover: 'Earthmover'):
        self.operation = config.get('operation')
        self.config = config

        self.earthmover = earthmover
        self.error_handler = self.earthmover.error_handler


    def get_source(self, source):
        """

        :return:
        """
        return self.earthmover.graph.ref(source)


    @abc.abstractmethod
    def compile(self):
        pass


    @abc.abstractmethod
    def verify(self):
        pass  # Verifications are optional.


    @abc.abstractmethod
    def execute(self):
        self.verify()
        pass
