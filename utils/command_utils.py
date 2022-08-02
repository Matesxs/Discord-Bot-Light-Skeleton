from disnake.ext import commands
from typing import Union
import os

# https://github.com/Toaster192/rubbergod/blob/master/utils.py
def get_command_signature(cmd_src: Union[commands.Context, commands.Command]):
  cmd = cmd_src.command if isinstance(cmd_src, commands.Context) else cmd_src
  cmd_string = f"{cmd} {cmd.signature}".rstrip(" ")
  return f"{cmd_string}"

def get_cogs_in_folder(folder: str="extensions"):
  return [cog[:-3].lower() for cog in os.listdir(folder) if str(cog).endswith(".py") and "__init__" not in str(cog)]