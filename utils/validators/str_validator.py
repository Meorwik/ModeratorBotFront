from .base import BaseValidator


class StringValidator(BaseValidator):
    __name__: str = "StringValidator"

    def __init__(self, max_string_length: int = 0):
        self.max_string_length: int = max_string_length

    def _validate(self, value: str) -> bool:
        if value is None:
            return True

        return len(value) <= self.max_string_length
