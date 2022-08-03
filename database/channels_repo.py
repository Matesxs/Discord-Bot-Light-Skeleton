import disnake
from typing import Optional, Union

from database import session
from database.tables.channels import MessageableChannel, TextThread
from database import guilds_repo

def get_thread(thread_id: int) -> Optional[TextThread]:
  return session.query(TextThread).filter(TextThread.id == str(thread_id)).one_or_none()

def get_or_create_text_thread(thread: disnake.Thread) -> TextThread:
  thread_it = get_thread(thread.id)
  if thread_it is None:
    thread_it = TextThread.from_thread(thread)
    session.add(thread_it)
    session.commit()
  else:
    if thread_it.archived != thread.archived or thread_it.locked != thread_it.locked:
      thread_it.archived = thread.archived
      thread_it.locked = thread.locked
      session.commit()
  return thread_it

def remove_thread(thread_id: int):
  session.query(TextThread).filter(TextThread.id == str(thread_id)).delete()
  session.commit()

def get_messageable_channel(channel_id: int) -> Optional[MessageableChannel]:
  return session.query(MessageableChannel).filter(MessageableChannel.id == str(channel_id)).one_or_none()

def get_or_create_messageable_channel_if_not_exist(channel: Union[disnake.VoiceChannel, disnake.StageChannel, disnake.TextChannel, disnake.CategoryChannel, disnake.ForumChannel, disnake.Thread]) -> MessageableChannel:
  guilds_repo.get_or_create_guild_if_not_exist(channel.guild)

  if isinstance(channel, disnake.Thread):
    get_or_create_text_thread(channel)
    channel = channel.parent

  channel_it = get_messageable_channel(channel.id)
  if channel_it is None:
    channel_it = MessageableChannel.from_text_channel(channel)
    session.add(channel_it)
    session.commit()

  return channel_it

def remove_channel(channel_id: int):
  session.query(MessageableChannel).filter(MessageableChannel.id == str(channel_id)).delete()
  session.commit()
