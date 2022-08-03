import disnake
from disnake.ext import commands
from typing import List
import asyncio
import traceback

from features.base_cog import Base_Cog
from utils.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

class Listeners(Base_Cog):
  def __init__(self, bot):
    super(Listeners, self).__init__(bot, __file__)

  @commands.Cog.listener()
  async def on_raw_message_edit(self, payload: disnake.RawMessageUpdateEvent):
    before = payload.cached_message
    after = self.bot.get_message(payload.message_id)

    if after is None:
      channel = self.bot.get_channel(payload.channel_id)

      if channel is None:
        try:
          channel = await self.bot.fetch_channel(payload.channel_id)
        except:
          return

      after = await channel.fetch_message(payload.message_id)
      if after is None:
        return

    cogs: List[Base_Cog] = self.bot.cogs.values()
    try:
      cogs_listening_futures = [cog.handle_message_edited(before, after) for cog in cogs]
      await asyncio.gather(*cogs_listening_futures)
    except:
      logger.warning(f"Failed to execute message edit handler\n{traceback.format_exc()}")

def setup(bot):
  bot.add_cog(Listeners(bot))
