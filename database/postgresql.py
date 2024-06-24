from .models import User, Pin, Chat, ChatGroup, IncomeRecord, PublicationRecord, ModerationRequest
from .enums import ModerationStatus, Roles
from sqlalchemy.sql import select, delete, update
from typing import Final, Union, List
from sqlalchemy import func
from .base import DatabaseManager, Base
from datetime import datetime, date


class PostgresManager(DatabaseManager):
    __name__ = "PostgresManager"

    async def init(self) -> bool:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        return True

    """
                        ACTIONS WITH USERS
    """

    async def add_user(self, user: User) -> bool:
        async with self.Session() as session:
            session.add(user)
            await session.commit()

        return True

    async def get_user(self, user_id: Union[str, int]) -> User:
        async with self.Session() as session:
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    async def get_admin(self) -> User:
        async with self.Session() as session:
            query = select(User).where(User.role == Roles.admin)
            result = await session.execute(query)
            return result.scalars().one()

    async def count_users_joined_today(self) -> int:
        async with self.Session() as session:
            today_start = datetime.combine(date.today(), datetime.min.time())
            today_end = datetime.combine(date.today(), datetime.max.time())

            query = select(func.count(User.id)).where(
                User.register_date >= today_start,
                User.register_date <= today_end
            )

            result = await session.execute(query)
            return result.scalars().one()

    """
                        ACTIONS WITH CHATS
    """

    async def get_chat_group(self, chat_group_id: Union[str, int]) -> ChatGroup:
        async with self.Session() as session:
            query = select(ChatGroup).where(ChatGroup.id == int(chat_group_id))
            result = await session.execute(query)
            return result.scalars().one()

    async def get_chat(self, chat_id: Union[str, int]) -> Chat:
        async with self.Session() as session:
            query = select(Chat).where(Chat.chat_id == int(chat_id))
            result = await session.execute(query)
            return result.scalars().one()

    async def get_chat_ids(self) -> List[int]:
        async with self.Session() as session:
            query = select(Chat.chat_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_chats(self) -> List[Chat]:
        async with self.Session() as session:
            query = select(Chat)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_chat_groups(self) -> List[ChatGroup]:
        async with self.Session() as session:
            query = select(ChatGroup)
            result = await session.execute(query)
            return result.scalars().all()

    async def add_chat(self, chat: Chat) -> bool:
        async with self.Session() as session:
            session.add(chat)
            session.commit()

        return True

    """
                        ACTIONS WITH PINS
    """
    async def add_pin(self, pin: Pin):
        ...

    """
                        ACTIONS WITH MODERATION REQUESTS
    """

    async def add_moderation_request(self, moderation_request: ModerationRequest):
        async with self.Session() as session:
            session.add(moderation_request)
            await session.commit()

    async def get_moderation_request(self) -> ModerationRequest:
        record_limit: Final[int] = 1
        async with self.Session() as session:
            query = select(ModerationRequest).where(
                ModerationRequest.status == ModerationStatus.waiting
            ).order_by(ModerationRequest.id).limit(record_limit)
            result = await session.execute(query)
            return result.scalars().one_or_none()

    async def count_requests_waiting_for_moderation(self) -> int:
        async with self.Session() as session:
            query = select(func.count(ModerationRequest.status)).where(
                ModerationRequest.status == ModerationStatus.waiting
            )
            result = await session.execute(query)
            return result.scalars().one()

    async def change_moderation_request_status(self, moderation_request_id: int, status: ModerationStatus):
        async with self.Session() as session:
            query = update(ModerationRequest).where(
                ModerationRequest.id == moderation_request_id,
                ModerationRequest.status == ModerationStatus.waiting
            ).values(status=status)

            result = await session.execute(query)
            await session.commit()

