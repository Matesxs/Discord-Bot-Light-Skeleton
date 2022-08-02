import disnake

from database import session
from database.tables import stats

def add_stats(guild: disnake.Guild, commit: bool=True) -> stats.Stats:
  item = stats.Stats.from_guild(guild)
  session.add(item)
  if commit:
    session.commit()
  return item
