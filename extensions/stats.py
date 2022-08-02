from disnake.ext import tasks, commands

from features.base_cog import Base_Cog
from database import stats_repo

class Stats(Base_Cog):
  def __init__(self, bot):
    super(Stats, self).__init__(bot, __file__)
    if not self.stats_collection_task.is_running() and self.bot.is_ready():
      self.stats_collection_task.start()

  @commands.Cog.listener()
  async def on_ready(self):
    if not self.stats_collection_task.is_running():
      self.stats_collection_task.start()

  def cog_unload(self) -> None:
    if self.stats_collection_task.is_running():
      self.stats_collection_task.cancel()

  @tasks.loop(minutes=10)
  async def stats_collection_task(self):
    guilds = self.bot.guilds
    for guild in guilds:
      stats_repo.add_stats(guild, commit=False)
    stats_repo.session.commit()

def setup(bot):
  bot.add_cog(Stats(bot))
