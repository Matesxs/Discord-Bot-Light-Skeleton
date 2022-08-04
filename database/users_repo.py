import disnake
from typing import Optional, Union

from database import session
from database.tables.users import User, Member
from database import guilds_repo

def get_user(user_id: int) -> Optional[User]:
  return session.query(User).filter(User.id == str(user_id)).one_or_none()

def get_member(member_id: int, guild_id: int) -> Optional[Member]:
  return session.query(Member).filter(Member.id == str(member_id), Member.guild_id == str(guild_id)).one_or_none()

def get_or_create_user_if_not_exist(user: Union[disnake.Member, disnake.User]) -> User:
  user_it = get_user(user.id)
  if user_it is None:
    user_it = User.from_user(user)
    session.add(user_it)
    session.commit()
  else:
    if user_it.name != user.name:
      user_it.name = user.name
      session.commit()
  return user_it

def get_or_create_member_if_not_exist(member: disnake.Member) -> Member:
  member_it = get_member(member.id, member.guild.id)

  if member_it is None:
    get_or_create_user_if_not_exist(member)
    guilds_repo.get_or_create_guild_if_not_exist(member.guild)

    member_it = Member.from_member(member)
    session.add(member_it)
    session.commit()

  if member_it.nick != member.display_name:
    member_it.nick = member.display_name
    session.commit()
  return member_it

def remove_member(user_id: int, guild_id: int):
  session.query(Member).filter(Member.id == str(user_id), Member.guild_id == str(guild_id)).delete()
  session.commit()

def member_identifier_to_member_iid(user_id: int, guild_id: int) -> Optional[int]:
  data = session.query(Member.member_iid).filter(Member.id == str(user_id), Member.guild_id == str(guild_id)).one_or_none()
  if data is None: return None
  return data[0]
