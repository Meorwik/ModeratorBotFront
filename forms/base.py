from typing import Dict


class Form:
    def as_dict(self) -> Dict:
        return self.__dict__


class BasePlacementTypes:
    group_repost: str = ""
    direct_messages_repost: str = ""
    message_from_bot: str = ""

    @classmethod
    def get_type(cls, option_number: int):
        if option_number == 1:
            return cls.message_from_bot

        elif option_number == 2:
            return cls.group_repost

        elif option_number == 3:
            return cls.direct_messages_repost



