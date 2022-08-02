import disnake
from disnake.ext import commands
from typing import Union, Iterable, Any
import datetime

from config import config

async def generate_error_message(ctx: Union[commands.Context, disnake.abc.Messageable, disnake.Message, disnake.MessageInteraction, disnake.ModalInteraction, disnake.CommandInteraction], text: str):
  response_embed = disnake.Embed(color=disnake.Color.dark_red(), title=":x: | Error", description=text)
  if isinstance(ctx, disnake.ModalInteraction) or isinstance(ctx, disnake.CommandInteraction) or isinstance(ctx, disnake.MessageInteraction):
    return await ctx.send(embed=response_embed, ephemeral=True)
  elif isinstance(ctx, disnake.Message):
    return await ctx.reply(embed=response_embed)
  else:
    return await ctx.send(embed=response_embed, delete_after=config.base.error_duration)

async def generate_success_message(ctx: Union[commands.Context, disnake.abc.Messageable, disnake.Message, disnake.MessageInteraction, disnake.ModalInteraction, disnake.CommandInteraction], text: str):
  response_embed = disnake.Embed(color=disnake.Color.green(), title=":white_check_mark: | Success", description=text)
  if isinstance(ctx, disnake.ModalInteraction) or isinstance(ctx, disnake.CommandInteraction) or isinstance(ctx, disnake.MessageInteraction):
    return await ctx.send(embed=response_embed, ephemeral=True)
  elif isinstance(ctx, disnake.Message):
    return await ctx.reply(embed=response_embed)
  else:
    return await ctx.send(embed=response_embed, delete_after=config.base.success_duration)

def add_author_footer(embed: disnake.Embed, author: Union[disnake.User, disnake.Member],
                      set_timestamp=True, additional_text: Union[Iterable[str], None] = None):
  if set_timestamp:
    embed.timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

  if additional_text is not None:
    embed.set_footer(icon_url=author.display_avatar.url, text=' | '.join((str(author), *additional_text)))
  else:
    embed.set_footer(icon_url=author.display_avatar.url, text=str(author))

  return embed

async def delete_message(bot: commands.AutoShardedBot, cnt: Any):
  try:
    if isinstance(cnt, commands.Context):
      if cnt.guild is not None or cnt.message.author.id == bot.user.id:
        await cnt.message.delete()
    else:
      if cnt.guild is not None or cnt.message.author.id == bot.user.id:
        await cnt.delete()
  except:
    pass