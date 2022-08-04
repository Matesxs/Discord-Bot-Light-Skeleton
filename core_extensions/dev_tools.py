import asyncio
import datetime
import disnake
from disnake.ext import commands
from typing import List

from config import cooldowns, Strings, config
from features.base_cog import Base_Cog
from database import messages_repo, users_repo, channels_repo
from utils.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

class AdminTools(Base_Cog):
  def __init__(self, bot):
    super(AdminTools, self).__init__(bot, __file__)

  @commands.slash_command()
  @commands.is_owner()
  async def essentials(self, inter: disnake.CommandInteraction):
    pass

  @essentials.sub_command(description=Strings.dev_tools_pull_data_description)
  @commands.max_concurrency(1, per=commands.BucketType.default)
  @cooldowns.huge_cooldown
  @commands.guild_only()
  async def pull_data(self, inter: disnake.CommandInteraction, days_back: float=commands.Param(default=None, description="Days back to pull data", min_value=0.0)):
    async def save_messages(message_it: disnake.abc.HistoryIterator):
      retries = 0
      while True:
        try:
          async for message in message_it:
            if message.author.bot or message.author.system: continue
            messages_repo.add_or_set_message(message, commit=False)
            await asyncio.sleep(0.2)
          break
        except disnake.Forbidden:
          return
        except disnake.HTTPException:
          retries += 1
          if retries >= 10:
            logger.warning("Limit reached 10x, skipping")
            break

          logger.warning("Limit reached, waiting")
          await asyncio.sleep(60)

    await inter.response.defer(with_message=True, ephemeral=True)
    logger.info("Starting members pulling")

    members = inter.guild.members
    for member in members:
      users_repo.get_or_create_member_if_not_exist(member)

    logger.info("Starting channels pulling")

    channels = await inter.guild.fetch_channels()
    for channel in channels:
      if isinstance(channel, (disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.ForumChannel, disnake.Thread)):
        channels_repo.get_or_create_messageable_channel_if_not_exist(channel)
        await asyncio.sleep(0.2)

    channels_repo.session.commit()

    logger.info("Starting messages pulling")

    for channel in channels:
      if isinstance(channel, (disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.ForumChannel, disnake.Thread)):
        messages_it = channel.history(limit=None, oldest_first=True, after=datetime.datetime.utcnow() - datetime.timedelta(days=config.essentials.delete_messages_after_days if days_back is None else days_back))
        await save_messages(messages_it)
        messages_repo.session.commit()

        if hasattr(channel, "threads"):
          threads: List[disnake.Thread] = channel.threads
          for thread in threads:
            messages_it = thread.history(limit=None, oldest_first=True, after=datetime.datetime.utcnow() - datetime.timedelta(days=config.essentials.delete_messages_after_days if days_back is None else days_back))
            await save_messages(messages_it)
            messages_repo.session.commit()

    logger.info("Data pulling completed")

    if not inter.is_expired():
      await inter.send(content=Strings.dev_tools_pull_data_pulling_complete)

def setup(bot):
  bot.add_cog(AdminTools(bot))