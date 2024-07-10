from sqlalchemy import String, Integer, Enum, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, mapped_column, Mapped
from .enums import Roles, ModerationStatus, PostStatus
from sqlalchemy.sql.functions import current_date
from sqlalchemy.dialects.postgresql import ARRAY
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
        return f"User - {self.id} Role - {self.role}"


class ChatGroup(Base):
    __tablename__: str = "ChatGroups"

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    chats: Mapped[ARRAY] = mapped_column(ARRAY(item_type=BigInteger), nullable=False)
    cost_of_placement: Mapped[int] = mapped_column(nullable=False)
    cost_of_one_day_pin: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self):
        return f"ChatGroupId - {self.id} Chats - {self.chats}"


class Chat(Base):
    __tablename__: str = 'Chats'

    chat_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False, primary_key=True)
    chat_name: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"Chat - {self.chat_id} ChatName - {self.chat_name}"


class Post(Base):
    __tablename__: str = 'Posts'

    id: Mapped[int] = mapped_column(autoincrement=True, nullable=False, primary_key=True)
    job_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    status: Mapped[Enum] = mapped_column(Enum(PostStatus), nullable=False, default=PostStatus.deferred)
    publish_date: Mapped[Date] = mapped_column(Date, nullable=False)
    post: Mapped[str] = mapped_column(nullable=False)
    chats: Mapped[ARRAY] = mapped_column(ARRAY(BigInteger), nullable=False)
    message_ids: Mapped[ARRAY] = mapped_column(ARRAY(BigInteger), nullable=True)


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


