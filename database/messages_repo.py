import disnake
from typing import Optional
import datetime

from database import session
from database.tables.messages import Message
from database import users_repo, channels_repo

def get_message(message_id: int) -> Optional[Message]:
  return session.query(Message).filter(Message.id == str(message_id)).one_or_none()

def add_or_set_message(message: disnake.Message, commit: bool=True) -> Optional[Message]:
  if isinstance(message.author, disnake.Member):
    users_repo.get_or_create_member_if_not_exist(message.author)
  else:
    users_repo.get_or_create_user_if_not_exist(message.author)

  if message.channel is not None and not isinstance(message.channel, disnake.DMChannel):
    channels_repo.get_or_create_messageable_channel_if_not_exist(message.channel)

  message_it = get_message(message.id)
  if message_it is None:
    message_it = Message.from_message(message)
    session.add(message_it)
  else:
    message_it.edited_at = message.edited_at

  if commit:
    session.commit()
  return message_it

def delete_message(message_id: int, commit: bool=True):
  session.query(Message).filter(Message.id == str(message_id)).delete()
  if commit:
    session.commit()

def delete_old_messages(days: int, commit: bool=True):
  threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
  session.query(Message).filter(Message.created_at <= threshold).delete()
  if commit:
    session.commit()
