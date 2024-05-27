from sqlalchemy.sql import select, delete, update
from .base import DatabaseManager
from typing import Final, Union, List
from .models import User, Pin, Chat, ChatGroup
from .base import Base


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
            return result.fetchone()

    """
                        ACTIONS WITH CHATS
    """

    async def get_chat_group(self, chat_group_id: Union[str, int]) -> ChatGroup:
        async with self.Session() as session:
            query = select(ChatGroup).where(ChatGroup.id == int(chat_group_id))
            result = await session.execute(query)
            return result.fetchone()

    async def get_chat(self, chat_id: Union[str, int]) -> Chat:
        async with self.Session() as session:
            query = select(Chat).where(Chat.chat_id == int(chat_id))
            result = await session.execute(query)
            return result.fetchone()

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

