# Custom help extension

import asyncio
import disnake
from disnake.ext import commands

from config import config, cooldowns, Strings
from features.paginator import EmbedView
from features.base_cog import Base_Cog
from utils.logger import setup_custom_logger
from typing import Union, List, Optional
from features.base_bot import BaseAutoshardedBot
from utils import command_utils, string_manipulation, message_utils

logger = setup_custom_logger(__name__)

async def command_check(com, ctx):
  if not com.checks:
    return True

  for check in com.checks:
    try:
      if asyncio.iscoroutinefunction(check):
        result = await check(ctx)
        if not result:
          return False
      else:
        if not check(ctx):
          return False
    except Exception:
      return False

  return True

async def get_all_commands(bot: BaseAutoshardedBot, ctx):
  return [com for cog in bot.cogs.values() for com in cog.walk_commands() if isinstance(com, commands.Command) and not com.hidden and await command_check(com, ctx)]

async def help_name_autocomplete(inter, string):
  everything = [str(cog.qualified_name).replace("_", " ") for cog in inter.bot.cogs.values()]
  everything.extend([com.name for com in await get_all_commands(inter.bot, inter)])

  if string is None or string == "":
    return everything[:25]
  return [d for d in everything if string.lower() in d.lower()][:25]

def generate_com_help(com):
  help_string = f"**Help**: " + com.help if com.help is not None else ""
  brief = f"**Brief**: {com.brief}" if com.brief is not None else ""
  aliases = ("**Aliases**: " + ", ".join(com.aliases)) + "" if com.aliases else ""

  string_array = [it for it in [aliases, brief, help_string] if it != ""]
  output = "\n".join(string_array) if string_array else "*No description*"

  return f"{config.base.command_prefix}{command_utils.get_command_signature(com)}", string_manipulation.truncate_string(output, 4000)

def add_command_help(embed, com):
  signature, description = generate_com_help(com)
  embed.add_field(name=signature, value=description, inline=False)


async def generate_help_for_cog(cog: Base_Cog, ctx) -> Union[None, List[disnake.Embed]]:
  if cog.hidden: return None

  coms = [com for com in cog.walk_commands() if isinstance(com, commands.Command) and not com.hidden and await command_check(com, ctx)]
  number_of_coms = len(coms)
  if number_of_coms == 0: return None

  coms = [generate_com_help(com) for com in coms]

  pages = []
  title = f"{str(cog.qualified_name)} Help"
  emb = disnake.Embed(title=title, colour=disnake.Color.green())
  message_utils.add_author_footer(emb, ctx.author)

  while coms:
    signature, description = coms.pop()
    embed_len = len(emb)
    added_length = len(signature) + len(description)

    if embed_len + added_length > 5000:
      pages.append(emb)
      emb = disnake.Embed(title=title, colour=disnake.Color.green())
      message_utils.add_author_footer(emb, ctx.author)

    emb.add_field(name=signature, value=description, inline=False)

  pages.append(emb)

  return pages

class Help(Base_Cog):
  def __init__(self, bot):
    super(Help, self).__init__(bot, __file__)

  @commands.slash_command(name="help", description=Strings.help_description)
  @cooldowns.short_cooldown
  async def help(self, ctx: disnake.CommandInteraction, name: Optional[str]=commands.Param(default=None, description=Strings.help_name_param_description, autocomplete=help_name_autocomplete)):
    await message_utils.delete_message(self.bot, ctx)

    pages = []
    if name is not None:
      all_commands = await get_all_commands(self.bot, ctx)
      command = disnake.utils.get(all_commands, name=name)
      if command is not None:
        emb = disnake.Embed(title="Help", colour=disnake.Color.green())
        message_utils.add_author_footer(emb, ctx.author)
        add_command_help(emb, command)
        return await ctx.send(embed=emb)

    for cog in self.bot.cogs.values():
      if name is not None:
        if name.lower() != cog.qualified_name.lower() and \
            name.lower() != cog.file.lower() and \
            name.lower() != cog.file.lower().replace("_", " "):
          continue

      cog_pages = await generate_help_for_cog(cog, ctx)
      if cog_pages is not None:
        pages.extend(cog_pages)

    if pages:
      await EmbedView(ctx.author, embeds=pages, perma_lock=True).run(ctx)
    else:
      emb = disnake.Embed(title="Help", description="*No help available*", colour=disnake.Color.orange())
      await ctx.send(embed=emb)

  @commands.slash_command(name="command_list", description=Strings.help_commands_list_description)
  @cooldowns.short_cooldown
  async def command_list(self, inter: disnake.CommandInteraction):
    await message_utils.delete_message(self.bot, inter)

    all_commands = await get_all_commands(self.bot, inter)
    command_strings = [f"{config.base.command_prefix}{command_utils.get_command_signature(com)}" for com in all_commands]

    pages = []
    while command_strings:
      output, command_strings = string_manipulation.add_string_until_length(command_strings, 4000, "\n")
      embed = disnake.Embed(title="Commands list", description=output, colour=disnake.Color.dark_blue())
      message_utils.add_author_footer(embed, inter.author)
      pages.append(embed)

    if pages:
      await EmbedView(inter.author, embeds=pages, perma_lock=True).run(inter)
    else:
      emb = disnake.Embed(title="Commands list", description="*No commands available*", colour=disnake.Color.orange())
      message_utils.add_author_footer(emb, inter.author)
      await inter.send(embed=emb, ephemeral=True)

def setup(bot):
  bot.add_cog(Help(bot))
