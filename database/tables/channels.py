import disnake
from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from typing import Optional, Union

from database import database
from features.base_bot import BaseAutoshardedBot
from utils import object_getters

class TextThread(database.base):
  __tablename__ = "text_threads"

  id = Column(String, primary_key=True)
  channel_id = Column(String, ForeignKey("messageable_channels.id", ondelete="CASCADE"), nullable=False, index=True)

  created_at = Column(DateTime, nullable=False)

  archived = Column(Boolean, nullable=False)
  locked = Column(Boolean, nullable=False)

  channel = relationship("MessageableChannel", back_populates="threads", uselist=False)
  messages = relationship("Message", back_populates="thread", uselist=True)

  @classmethod
  def from_thread(cls, thread: disnake.Thread):
    return cls(id=str(thread.id), channel_id=str(thread.parent.id), created_at=thread.created_at, archived=thread.archived, locked=thread.locked)

  async def to_object(self, bot: BaseAutoshardedBot) -> Optional[disnake.Thread]:
    channel = await self.channel.to_object(bot)
    if channel is None:
      guild = await self.channel.guild.to_object(bot)
      if guild is None: return None
      thread = await object_getters.get_or_fetch_channel(guild, int(self.id))
      return thread

    message = await channel.fetch_message(int(self.id)) # Get main message of thread
    if message is None: return None

    return message.thread

class MessageableChannel(database.base):
  __tablename__ = "messageable_channels"

  id = Column(String, primary_key=True)
  guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False, index=True)

  created_at = Column(DateTime, nullable=False)

  guild = relationship("Guild", back_populates="messageable_channels", uselist=False)
  threads = relationship("TextThread", back_populates="channel", uselist=True)
  messages = relationship("Message", back_populates="channel", uselist=True)

  @classmethod
  def from_text_channel(cls, channel: Union[disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.CategoryChannel, disnake.ForumChannel, disnake.Thread]):
    return cls(id=str(channel.id), guild_id=str(channel.guild.id), created_at=channel.created_at)

  async def to_object(self, bot: BaseAutoshardedBot) -> Optional[Union[disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.CategoryChannel, disnake.ForumChannel, disnake.Thread]]:
    guild = await self.guild.to_object(bot)
    if guild is None: return None
    channel = await object_getters.get_or_fetch_channel(guild, int(self.id))
    return channel
