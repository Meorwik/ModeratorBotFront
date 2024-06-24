from pickle import dumps, loads
from typing import Final


class MarshalTool:
    __name__: str = "BASE"

    def __str__(self):
        return f"{self.__name__}Object"


class Serializer(MarshalTool):
    __name__: str = "Serializer"

    async def serialize(self, obj: object) -> str:
        bytes_object: bytes = dumps(obj)
        return str(bytes_object)


class Deserializer(MarshalTool):
    __name__: str = "Deserializer"

    __ENCODING: Final[str] = "utf-8"

    async def deserialize(self, data: str):
        cleaned_bytes_string = data[2:-1]
        bytes_obj = bytes(cleaned_bytes_string, self.__ENCODING).decode('unicode_escape').encode('latin1')
        return loads(bytes_obj)
