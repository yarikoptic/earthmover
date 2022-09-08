import abc
import jinja2
import pandas as pd

from earthmover.refactor import util

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from earthmover.refactor.earthmover import Earthmover


class Node:
    """

    """
    def __init__(self, name: str, config: dict, *, earthmover: 'Earthmover'):
        self.name = name
        self.config = config
        self.type = None

        self.earthmover = earthmover
        self.logger = earthmover.logger
        self.error_handler = earthmover.error_handler

        self.data = None
        self.size = None
        self.rows = None
        self.cols = None

        self.expectations = []


    @abc.abstractmethod
    def compile(self):
        """

        :return:
        """
        self.error_handler.ctx.update(
            file=self.earthmover.config_file, line=self.config['__line__'], node=self, operation=None
        )
        pass


    @abc.abstractmethod
    def execute(self):
        """

        :return:
        """
        self.error_handler.ctx.update(
            file=self.earthmover.config_file, line=self.config["__line__"], node=self, operation=None
        )
        pass


    def check_expectations(self):
        """

        :return:
        """
        expectation_result_col = "__expectation_result__"

        if not self.data:
            self.logger.debug("skipping checking expectations (not yet loaded)")
            return

        if self.expectations:
            result = self.data.copy()

            for expectation in self.expectations:
                template = jinja2.Template("{{" + expectation + "}}")

                result[expectation_result_col] = result.apply(
                    util.render_jinja_template, axis=1,
                    meta=pd.Series(dtype='str', name=expectation_result_col),
                    template=template,
                    error_handler = self.error_handler
                )

                num_failed = len(result.query(f"{expectation_result_col}=='False'"))
                if num_failed > 0:
                    self.error_handler.throw(
                        f"Source `${self.type}s.{self.name}` failed expectation `{expectation}` ({num_failed} rows fail)"
                    )

            result.drop(columns=expectation_result_col)
