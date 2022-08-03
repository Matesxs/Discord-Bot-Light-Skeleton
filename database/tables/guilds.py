import disnake
from typing import Optional
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from database import database
from features.base_bot import BaseAutoshardedBot

class Guild(database.base):
  __tablename__ = "guilds"

  id = Column(String, primary_key=True)

  messageable_channels = relationship("MessageableChannel", back_populates="guild", uselist=True)
  members = relationship("Member", back_populates="guild", uselist=True)

  @classmethod
  def from_guild(cls, guild: disnake.Guild):
    return cls(id=str(guild.id))

  async def to_object(self, bot: BaseAutoshardedBot) -> Optional[disnake.Guild]:
    guild = bot.get_guild(int(self.id))
    if guild is None:
      try:
        guild = await bot.fetch_guild(int(self.id))
      except disnake.NotFound:
        return None
    return guild