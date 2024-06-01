from abc import ABC


class BaseValidator(ABC):

    __name__: str = "Base"

    def __repr__(self):
        return f"{self.__name__}Object - ({id(self)})"

    def _validate(self, value: any) -> bool:
        """
        Override this function in order to create your own validation method
        :param value: (your value type)
        :return: bool
        """
        ...

    def validate(self, value: any) -> bool:
        """
        Interface for better and easier interaction with child classes

        :param value:
        :return: bool
        """
        return self._validate(value)

