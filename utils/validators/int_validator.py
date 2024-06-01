from typing import Union, Final
from .base import BaseValidator


class IntegerValidator(BaseValidator):

    __name__: str = "IntegerValidator"

    def __init__(self, max_possible_value: int = 0):
        self.max_possible_value: Final[int] = max_possible_value

    def _validate(self, value: Union[str, int]) -> bool:
        try:
            int_value: int = int(value)

        except ValueError:
            return False, 0

        return int_value <= self.max_possible_value, int_value
