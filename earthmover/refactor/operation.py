import abc

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from earthmover.refactor.earthmover import Earthmover
    from earthmover.refactor.node import Node


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


    def __init__(self, config, *, earthmover: 'Earthmover'):
        self.config = config
        self.type = self.config.get('operation')

        self.earthmover = earthmover
        self.error_handler = self.earthmover.error_handler

        # `source` and `source_list` are mutually-exclusive attributes.
        self.source = None
        self.source_list = None  # For operations with multiple sources (i.e., dataframe operations)

        if 'sources' in self.config:
            self.error_handler.assert_key_type_is(self.config, 'sources', list)
            self.source_list = self.config['sources']

        elif 'source' in self.config:
            self.error_handler.assert_key_type_is(self.config, 'source', str)
            self.source = self.config['source']

        else:
            self.error_handler.throw(
                "A `source` or a list of `sources` must be defined for any operation!"
            )

        self.source_data_list = None  # Retrieved data for operations with multiple sources
        self.data = None  # Final dataframe after execute()
        self.expectations = None  # Similar to Node.expectations, but run within Transformation.execute().


    def get_source_node(self, source) -> 'Node':
        """

        :return:
        """
        return self.earthmover.graph.ref(source)


    @abc.abstractmethod
    def compile(self):
        """

        :return:
        """
        self.error_handler.ctx.update(
            file=self.earthmover.config_file, line=self.config["__line__"], node=None, operation=self
        )

        # Always check for expectations
        if 'expect' in self.config:
            self.error_handler.assert_key_type_is(self.config, 'expect', list)
            self.expectations = self.config['expect']

        pass


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
        self.error_handler.ctx.update(
            file=self.earthmover.config_file, line=self.config["__line__"], node=None, operation=self
        )

        # If multiple sources are required for an operation, self.data must be defined in the child class execute().
        if self.source_list:
            self.source_data_list = [
                self.get_source_node(source).data for source in self.source_list
            ]
        else:
            self.data = self.get_source_node(self.source).data

        self.verify()

        pass
