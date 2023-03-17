from typing import Optional

class ErrorContext:
    """

    """
    def __init__(self, file=None, line=None, node=None, operation=None):
        self.file = None
        self.line = None
        self.node = None
        self.operation = None
        self.config_template = ""
        self.macros_lines = 0

        self.update(file=file, line=line, node=node, operation=operation)
    
    def update_config_template(self, config_template):
        self.config_template = config_template

    def update_macros_lines(self, macros_lines):
        self.macros_lines = macros_lines

    def update(self, file=None, line=None, node=None, operation=None):
        self.file = file
        self.line = line
        self.node = node
        self.operation = operation


    def add(self, file=None, line=None, node=None, operation=None):
        if file:
            self.file = file
        if line:
            self.line = line
        if node:
            self.node = node
        if operation:
            self.operation = operation


    def remove(self, *args):
        for arg in args:
            if arg == 'file':
                self.file = None
            if arg == 'line':
                self.line = None
            if arg == 'node':
                self.node = None
            if arg == 'operation':
                self.operation = None

    
    def __repr__(self) -> str:
        """
        Example error messages:
            "(near line 79 of `config.yaml` in `$transformations.joined_inventories` operation `join`)
            "(at `$destinations.big_cats`)

        :return:
        """
        if self.line:
            log = f"near line {self.line} of "
        else:
            log = "at "

        if self.file:
            log += f"`{self.file}` "

        if self.node:
            log += f"in `${self.node.type}s.{self.node.name}` "

        if self.operation:
            log += f"operation `{self.operation.type}` "

        return "(" + log.strip() + ") "


    def __add__(self, other):
        return str(self) + other



class ErrorHandler:
    
    config_template = None
    macros_lines = 0

    def __init__(self, file=None, line=None, node=None, operation=None):
        self.ctx = ErrorContext(file=file, line=line, node=node, operation=operation)

    def update_context(self, config_template, macros_lines):
        self.ctx.update_config_template(config_template)
        self.ctx.update_macros_lines(macros_lines)

    def assert_get_key(self, obj: dict, key: str,
        dtype: Optional[type] = None,
        required: bool = True,
        default: Optional[object] = None
    ) -> Optional[object]:
        """

        :param obj:
        :param key:
        :param dtype:
        :param required:
        :param default:
        :return:
        """
        value = obj.get(key)

        if value is None:
            if required:
                raise Exception(
                    f"{self.ctx} must define `{key}`"
                )
            else:
                return default

        if dtype and not isinstance(value, dtype):
            raise Exception(
                f"{self.ctx} `{key}` is defined, but wrong type (should be {dtype}, is {type(value)})"
            )

        return value

    def throw(self, message: str):
        raise Exception(
            f"{self.ctx} {message})"
        )
