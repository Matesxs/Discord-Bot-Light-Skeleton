import disnake
from disnake.ext import commands
from typing import Union, Optional

async def get_or_fetch_channel(source: Union[disnake.Guild, commands.AutoShardedBot], channel_id: int) -> Optional[Union[disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.CategoryChannel, disnake.ForumChannel, disnake.Thread]]:
  channel = source.get_channel(channel_id)
  if channel is None:
    try:
      channel = await source.fetch_channel(channel_id)
    except:
      return None

  return channel

async def get_or_fetch_message(bot: commands.AutoShardedBot, source: Optional[Union[disnake.TextChannel, disnake.Thread]], message_id: int) -> Optional[disnake.Message]:
  message = bot.get_message(message_id)
  if message is None and source is not None:
    try:
      message = await source.fetch_message(message_id)
    except:
      return None
  return message

async def get_or_fetch_member(source: Union[disnake.Guild, commands.AutoShardedBot], member_id: int) -> Optional[disnake.Member]:
  if isinstance(source, disnake.Guild):
    user = source.get_member(member_id)
    if user is None:
      try:
        user = await source.fetch_member(member_id)
      except:
        return None
  else:
    users = source.get_all_members()
    user = disnake.utils.get(users, id=member_id)
  return user