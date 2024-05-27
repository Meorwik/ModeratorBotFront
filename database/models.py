from sqlalchemy import Column, String, Integer, Enum, Date, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql.functions import current_date
from sqlalchemy.dialects.postgresql import ARRAY
from dataclasses import dataclass
from typing import Final
from .base import Base
import enum

MAX_USERNAME_LENGTH: Final[int] = 32
MAX_FIRST_NAME_LENGTH: Final[int] = 50
MAX_LAST_NAME_LENGTH: Final[int] = 50


class Roles(enum.Enum):
    user: Final[str] = "user"
    admin: Final[str] = "admin"


class User(Base):
    __tablename__: str = 'Users'

    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True, nullable=False, unique=True)
    username: Mapped[String] = mapped_column(String(length=MAX_USERNAME_LENGTH), nullable=True)
    first_name: Mapped[String] = mapped_column(String(length=MAX_FIRST_NAME_LENGTH), nullable=True)
    last_name: Mapped[String] = mapped_column(String(length=MAX_LAST_NAME_LENGTH), nullable=True)
    role: Mapped[Enum] = mapped_column(Enum(Roles), default=Roles.user)
    register_date: Mapped[Date] = mapped_column(Date, default=current_date())

    def __repr__(self):
        return f"User - {self.id}\nRole - {self.role}\nUserObject - ({id(self)})\n"


class ChatGroup(Base):
    __tablename__: str = "ChatGroups"

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    chats: Mapped[ARRAY] = mapped_column(ARRAY(item_type=BigInteger), nullable=False)
    link: Mapped[String] = mapped_column(String, nullable=False)
    cost: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self):
        return f"ChatGroupId - {self.id}\nChats - {self.chats}\nChatGroupObject - ({id(self)})"


class Chat(Base):
    __tablename__: str = 'Chats'

    chat_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False, primary_key=True)
    chat_name: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"Chat - {self.chat_id}\nChatName - {self.chat_name}\nChatObject - ({id(self)})"


class Pin(Base):
    __tablename__: str = 'Pins'

    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)
    user_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)
    chats: Mapped[ARRAY] = mapped_column(ARRAY(BigInteger), nullable=False)
    expiry_date: Mapped[Date] = mapped_column(Date, nullable=False)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"Pin - {self.id}\nUser - {self.user_id}\nChats - ({self.chats})\nPinObject - ({id(self)})"

