from sqlalchemy import Column, String, Integer, Enum, Date, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql.functions import current_date
from sqlalchemy.dialects.postgresql import ARRAY
from .enums import Roles, ModerationStatus
from typing import Final
from .base import Base

MAX_USERNAME_LENGTH: Final[int] = 32
MAX_FIRST_NAME_LENGTH: Final[int] = 50
MAX_LAST_NAME_LENGTH: Final[int] = 50


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
    cost_of_placement: Mapped[int] = mapped_column(nullable=False)
    cost_of_one_day_pin: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self):
        return f"ChatGroupId - {self.id} Chats - {self.chats} ChatGroupObject - ({id(self)})"


class Chat(Base):
    __tablename__: str = 'Chats'

    chat_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False, primary_key=True)
    chat_name: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"Chat - {self.chat_id} ChatName - {self.chat_name} ChatObject - ({id(self)})"


class Pin(Base):
    __tablename__: str = 'Pins'

    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)
    user_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey(User.id), nullable=False)
    chats: Mapped[ARRAY] = mapped_column(ARRAY(String), nullable=False)
    expiry_date: Mapped[Date] = mapped_column(Date, nullable=False)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"Pin - {self.id} User - {self.user_id} Chats - ({self.chats}) PinObject - ({id(self)})"


class IncomeRecord(Base):
    __tablename__: str = 'IncomeStatistics'

    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)
    income_sum: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False, default=current_date())


class PublicationRecord(Base):
    __tablename__: str = 'PublicationStatistics'

    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)
    with_pin: Mapped[bool] = mapped_column(nullable=False)


class ModerationRequest(Base):
    __tablename__: str = 'Moderation'

    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)
    from_user: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('Users.id'), nullable=False)
    form: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[Enum] = mapped_column(Enum(ModerationStatus), nullable=False, default=ModerationStatus.waiting)


