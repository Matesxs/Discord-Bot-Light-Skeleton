import disnake
from disnake.ext import commands, tasks
from typing import Optional

from utils.logger import setup_custom_logger
from config import config
from database import messages_repo, users_repo, guilds_repo, channels_repo
from features.base_cog import Base_Cog

logger = setup_custom_logger(__name__)

class DataCollection(Base_Cog):
  def __init__(self, bot):
    super(DataCollection, self).__init__(bot, __file__)

    if not self.cleanup_task.is_running():
      self.cleanup_task.start()

  def cog_unload(self) -> None:
    if self.cleanup_task.is_running():
      self.cleanup_task.cancel()

  @commands.Cog.listener()
  async def on_raw_thread_update(self, after: disnake.Thread):
    thread_it = channels_repo.get_thread(after.id)
    if thread_it is not None:
      thread_it.archived = after.archived
      thread_it.locked = after.locked
      channels_repo.session.commit()

  @commands.Cog.listener()
  async def on_thread_create(self, thread: disnake.Thread):
    channels_repo.get_or_create_text_thread(thread)

  @commands.Cog.listener()
  async def on_raw_thread_delete(self, payload: disnake.RawThreadDeleteEvent):
    channels_repo.remove_thread(payload.thread_id)

  @commands.Cog.listener()
  async def on_guild_channel_create(self, channel: disnake.abc.GuildChannel):
    if isinstance(channel, (disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.CategoryChannel, disnake.ForumChannel, disnake.Thread)):
      channels_repo.get_or_create_messageable_channel_if_not_exist(channel)

  @commands.Cog.listener()
  async def on_guild_channel_delete(self, channel: disnake.abc.GuildChannel):
    if isinstance(channel, (disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.CategoryChannel, disnake.ForumChannel, disnake.Thread)):
      channels_repo.remove_channel(channel.id)

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if message.author.bot: return
    if message.content.startswith(config.base.command_prefix): return

    messages_repo.add_or_set_message(message, commit=True)

  async def handle_message_edited(self, before: Optional[disnake.Message], after: disnake.Message):
    if after.author.bot: return
    if after.content.startswith(config.base.command_prefix): return

    messages_repo.add_or_set_message(after, commit=True)

  @commands.Cog.listener()
  async def on_message_delete(self, message: disnake.Message):
    if message.author.bot: return
    if message.content.startswith(config.base.command_prefix): return

    messages_repo.delete_message(message.id, commit=True)

  @commands.Cog.listener()
  async def on_member_update(self, _, after: disnake.Member):
    user_it = users_repo.get_member(after.id, after.guild.id)
    if user_it is not None:
      user_it.nick = after.display_name
      user_it.icon_url = after.display_avatar.url
      user_it.premium = after.premium_since is not None
      users_repo.session.commit()

  @commands.Cog.listener()
  async def on_member_join(self, member: disnake.Member):
    users_repo.get_or_create_member_if_not_exist(member)

  @commands.Cog.listener()
  async def on_member_remove(self, member: disnake.Member):
    users_repo.remove_member(member.id, member.guild.id)

  @commands.Cog.listener()
  async def on_guild_join(self, guild: disnake.Guild):
    guilds_repo.get_or_create_guild_if_not_exist(guild)
    for member in guild.members:
      users_repo.get_or_create_member_if_not_exist(member)

  @commands.Cog.listener()
  async def on_guild_remove(self, guild: disnake.Guild):
    guilds_repo.remove_guild(guild.id)

  @tasks.loop(hours=24)
  async def cleanup_task(self):
    messages_repo.delete_old_messages(config.essentials.delete_messages_after_days)

def setup(bot):
  bot.add_cog(DataCollection(bot))
