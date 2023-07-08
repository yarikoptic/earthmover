import abc

from earthmover.node import Node

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from earthmover.earthmover import Earthmover


class Operation(Node):
    """

    """
    def __new__(cls, name: str, config: dict, *, earthmover: 'Earthmover'):
        """
        :param config:
        :param earthmover:
        """
        from earthmover.operations import groupby as groupby_operations
        from earthmover.operations import dataframe as dataframe_operations
        from earthmover.operations import column as column_operations
        from earthmover.operations import row as row_operations

        operation_mapping = {
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
        operation_class = operation_mapping.get(operation)

        if operation_class is None:
            earthmover.error_handler.throw(
                f"invalid transformation operation `{operation}`"
            )
            raise

        return object.__new__(operation_class)


    def __init__(self, name: str, config: dict, *, earthmover: 'Earthmover'):
        full_name = f"{name}.operations:{config.get('operation')}"
        super().__init__(full_name, config, earthmover=earthmover)

        self.type = "transformation" # self.config.get('operation')

        self.allowed_configs.update(['operation'])

        self.sources = []

        # `source` and `source_list` are optional attributes used for Joins and Unions respectively.
        _source_list = self.error_handler.assert_get_key(self.config, 'source_list', dtype=str, required=False)
        if _source_list:
            self.sources.extend(_source_list)

        _source = self.error_handler.assert_get_key(self.config, 'source', dtype=str, required=False)
        if _source:
            self.sources.append(_source)




    @abc.abstractmethod
    def compile(self):
        """

        :return:
        """
        super().compile()


    def verify(self):
        """
        Because verifications are optional, this is not an abstract method.

        :return:
        """
        pass


    @abc.abstractmethod
    def execute(self):
        """

        :return:
        """
        super().execute()

        # If multiple sources are required for an operation, self.data must be defined in the child class execute().
        if self.source_list:
            self.source_data_list = [
                self.get_source_node(source).data for source in self.source_list
            ]
        else:
            self.data = self.get_source_node(self.source).data

        self.verify()

        pass
