import disnake
import datetime
from sqlalchemy import Column, DateTime, String

from database import database, BigIntegerType

class Stats(database.base):
  __tablename__ = "stats"

  id = Column(BigIntegerType, primary_key=True, unique=True, index=True, autoincrement=True)

  guild_id = Column(String, nullable=False, index=True)
  timestamp = Column(DateTime, index=True)
  online = Column(BigIntegerType)
  idle = Column(BigIntegerType)
  offline = Column(BigIntegerType)

  @classmethod
  def from_guild(cls, guild: disnake.Guild):
    members = guild.members

    online, idle, offline = 0, 0, 0
    for member in members:
      if member.status == disnake.Status.online:
        online += 1
      elif member.status == disnake.Status.offline:
        offline += 1
      else:
        idle += 1
    return cls(guild_id=str(guild.id), timestamp=datetime.datetime.utcnow(), online=online, idle=idle, offline=offline)
