# Error handling extension

import datetime
import disnake
from disnake.ext import commands
import traceback

from utils import message_utils, command_utils, string_manipulation
from utils.logger import setup_custom_logger
from features.base_cog import Base_Cog
from config import config, Strings
from features.base_bot import BaseAutoshardedBot

logger = setup_custom_logger(__name__)

class Errors(Base_Cog):
  def __init__(self, bot: BaseAutoshardedBot):
    super(Errors, self).__init__(bot, __file__)

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    await self.command_error_handling(ctx, error)

  @commands.Cog.listener()
  async def on_message_command_error(self, inter, error):
    await self.command_error_handling(inter, error)

  @commands.Cog.listener()
  async def on_user_command_error(self, inter, error):
    await self.command_error_handling(inter, error)

  @commands.Cog.listener()
  async def on_slash_command_error(self, inter, error):
    await self.command_error_handling(inter, error)

  async def command_error_handling(self, ctx, error):
    if isinstance(error, commands.CommandNotFound):
      await message_utils.generate_error_message(ctx, Strings.error_unknown_command)
    elif isinstance(error, commands.CommandOnCooldown):
      await message_utils.generate_error_message(ctx, Strings.error_command_on_cooldown(remaining=round(error.retry_after, 2)))
    elif isinstance(error, commands.MissingPermissions):
      await message_utils.generate_error_message(ctx, Strings.error_missing_permission)
    elif isinstance(error, commands.MissingRole):
      await message_utils.generate_error_message(ctx, Strings.error_missing_role(role=error.missing_role))
    elif isinstance(error, commands.MissingRequiredArgument):
      await message_utils.generate_error_message(ctx, Strings.error_missing_argument(argument=error.param, signature=command_utils.get_command_signature(ctx)))
    elif isinstance(error, commands.BadArgument):
      await message_utils.generate_error_message(ctx, Strings.error_bad_argument)
    elif isinstance(error, commands.MaxConcurrencyReached):
      await message_utils.generate_error_message(ctx, Strings.error_max_concurrency_reached)
    elif isinstance(error, commands.NoPrivateMessage):
      await message_utils.generate_error_message(ctx, Strings.error_no_private_message)
    elif isinstance(error, disnake.InteractionTimedOut):
      await message_utils.generate_error_message(ctx, Strings.error_interaction_timeout)
    elif isinstance(error, disnake.Forbidden):
      await message_utils.generate_error_message(ctx, Strings.error_forbiden)
    elif isinstance(error, disnake.HTTPException) and error.code == 50007:
      await message_utils.generate_error_message(ctx, Strings.error_blocked_dms)
    else:
      self.bot.last_error = datetime.datetime.utcnow()

      output = "".join(traceback.format_exception(type(error), error, error.__traceback__))
      logger.error(output)

      log_channel = self.bot.get_channel(config.ids.log_channel)
      if log_channel is None: return

      if isinstance(ctx, (disnake.ApplicationCommandInteraction, disnake.ModalInteraction, disnake.MessageCommandInteraction)):
        embed = disnake.Embed(title=f"Ignoring exception in application interaction {ctx.application_command}", color=0xFF0000)
      else:
        embed = disnake.Embed(title=f"Ignoring exception in command {ctx.command}", color=0xFF0000)
        embed.add_field(name="Message", value=ctx.message.content[:1000])
        embed.add_field(name="Link", value=ctx.message.jump_url, inline=False)

      embed.add_field(name="Autor", value=str(ctx.author))
      embed.add_field(name="Type", value=str(type(error)))

      if ctx.guild:
        embed.add_field(name="Guild", value=ctx.guild.name)

      await log_channel.send(embed=embed)

      output = string_manipulation.split_to_parts(output, 1900)
      if log_channel is not None:
        for message in output:
          await log_channel.send(f"```\n{message}\n```")

  @commands.Cog.listener()
  async def on_error(self, event_method, *args, _):
    self.bot.last_error = datetime.datetime.utcnow()

    output = traceback.format_exc()
    logger.error(output)

    log_channel = self.bot.get_channel(config.ids.log_channel)
    if log_channel is None: return

    embeds = []
    for arg in args:
      if arg.guild_id:
        guild = self.bot.get_guild(arg.guild_id)
        event_guild = guild.name
        channel = guild.get_channel(arg.channel_id)
        try:
          message = await channel.fetch_message(arg.message_id)
          message = message.content[:1000]
        except:
          message = arg.message_id
      else:
        event_guild = "DM"
        message = arg.message_id

      user = self.bot.get_user(arg.user_id)
      if not user:
        user = arg.user_id
      else:
        channel = self.bot.get_channel(arg.channel_id)
        if channel:
          try:
            message = await channel.fetch_message(arg.message_id)
            if message.content:
              message = message.content[:1000]
            elif message.embeds:
              embeds.extend(message.embeds)
              message = "Embed in previous message"
            elif message.attachments:
              message_out = ""
              for attachment in message.attachments:
                message_out += f"{attachment.url}\n"
              message = message_out
          except:
            message = arg.message_id
        else:
          message = arg.message_id
        user = str(user)

      embed = disnake.Embed(title=f"Ignoring exception in event '{event_method}'", color=0xFF0000)
      embed.add_field(name="Message", value=message, inline=False)
      embed.add_field(name="Guild", value=event_guild)

      if arg.member:
        reaction_from = str(arg.member)
      else:
        reaction_from = user
      embed.add_field(name="Reaction from", value=reaction_from)
      embed.add_field(name="Reaction", value=arg.emoji)
      embed.add_field(name="Type", value=arg.event_type)
      if arg.guild_id:
        link = f"https://disnake.com/channels/{arg.guild_id}/{arg.channel_id}/{arg.message_id}"
        embed.add_field(name="Link", value=link, inline=False)
      embeds.append(embed)

    output = string_manipulation.split_to_parts(output, 1900)
    for embed in embeds:
      await log_channel.send(embed=embed)
    for message in output:
      await log_channel.send(f"```\n{message}```")


def setup(bot):
  bot.add_cog(Errors(bot))
