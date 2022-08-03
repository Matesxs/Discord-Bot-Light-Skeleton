import disnake
from typing import Optional
from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database import database, BigIntegerType
from database import users_repo
from features.base_bot import BaseAutoshardedBot
from utils import object_getters

class Message(database.base):
  __tablename__ = "messages"

  id = Column(String, primary_key=True)
  author_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
  guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=True, index=True)
  member_iid = Column(BigIntegerType, ForeignKey("members.member_iid", ondelete="SET NULL"), index=True, nullable=True)

  member = relationship("Member", back_populates="messages", uselist=False)
  user = relationship("User", back_populates="messages", uselist=False)

  created_at = Column(DateTime, index=True, nullable=False)
  edited_at = Column(DateTime)

  is_DM = Column(Boolean, nullable=False, index=True)
  channel_id = Column(String, ForeignKey("messageable_channels.id", ondelete="CASCADE"), index=True, nullable=True)
  thread_id = Column(String, ForeignKey("text_threads.id", ondelete="CASCADE"), index=True, nullable=True)

  channel = relationship("MessageableChannel", back_populates="messages", uselist=False)
  thread = relationship("TextThread", back_populates="messages", uselist=False)

  @classmethod
  def from_message(cls, message: disnake.Message):
    channel_is_thread = isinstance(message.channel, disnake.Thread)
    channel_is_dm = isinstance(message.channel, disnake.DMChannel)

    channel_id = (message.channel.parent.id if channel_is_thread else message.channel.id) if message.channel is not None and not channel_is_dm else None
    thread_id = message.channel.id if channel_is_thread else None
    guild_id = message.guild.id if message.guild is not None else None
    user_id = message.author.id
    member_iid = None
    if guild_id is not None:
      member_iid = users_repo.member_identifier_to_member_iid(user_id, guild_id)

    return cls(id=str(message.id),
               author_id=str(user_id),
               guild_id=str(guild_id) if guild_id is not None else None,
               member_iid=member_iid,
               created_at=message.created_at,
               edited_at=message.edited_at,
               is_DM=channel_is_dm,
               channel_id=str(channel_id) if channel_id is not None else None,
               thread_id=str(thread_id) if thread_id is not None else None)

  async def to_object(self, bot: BaseAutoshardedBot) -> Optional[disnake.Message]:
    message = await object_getters.get_or_fetch_message(bot, None, int(self.id))
    if message is None:
      if not self.is_DM:
        channel = await self.channel.to_object(bot)
        if channel is None: return None

        message = await object_getters.get_or_fetch_message(bot, channel, int(self.id))
      else:
        user = await self.user.to_object(bot)
        if user is None: return None

        message = await object_getters.get_or_fetch_message(bot, user, int(self.id))

    return message
