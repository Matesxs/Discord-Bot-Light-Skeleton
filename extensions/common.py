import disnake
from disnake.ext import commands
import datetime
import time
import humanize

from config import cooldowns, Strings
from features.base_cog import Base_Cog
from utils import message_utils

class Common(Base_Cog):
  def __init__(self, bot):
    super(Common, self).__init__(bot, __file__)

  @commands.command(brief=Strings.common_uptime_brief)
  @cooldowns.default_cooldown
  async def uptime(self, ctx: commands.Context):
    await message_utils.delete_message(self.bot, ctx)
    description = f"{humanize.naturaldelta(datetime.datetime.utcnow() - self.bot.start_time)}\nLast error: {humanize.naturaltime(datetime.datetime.utcnow() - self.bot.last_error) if self.bot.last_error is not None else 'Never'}"
    embed = disnake.Embed(title="Uptime", description=description, color=disnake.Color.dark_blue())
    message_utils.add_author_footer(embed, ctx.author)
    await ctx.send(embed=embed)

  @commands.command(brief=Strings.common_ping_brief)
  @cooldowns.default_cooldown
  async def ping(self, ctx: commands.Context):
    await message_utils.delete_message(self.bot, ctx)

    em = disnake.Embed(color=disnake.Color.dark_blue(), title="Pong!")
    message_utils.add_author_footer(em, ctx.message.author)

    start_time = time.time()
    message: disnake.Message = await ctx.channel.send(embed=em)
    end_time = time.time()

    em.description = em.description = f'Bot: {round(self.bot.latency * 1000)} ms\nAPI: {round((end_time - start_time) * 1000)}ms'
    await message.edit(embed=em)

def setup(bot):
  bot.add_cog(Common(bot))
