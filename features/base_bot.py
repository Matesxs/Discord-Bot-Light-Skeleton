# Precursor for bot class

import datetime
import disnake
from disnake.ext import commands
import traceback
from aiohttp import ClientSession, ClientTimeout

from utils import message_utils, object_getters, command_utils
from config import config
from utils.logger import setup_custom_logger
from database import init_tables

logger = setup_custom_logger(__name__)

intents = disnake.Intents.none()
intents.guilds = True
intents.members = True
intents.emojis = True
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.presences = True
intents.typing = True
intents.voice_states = True

class BaseAutoshardedBot(commands.AutoShardedBot):
  def __init__(self):
    super(BaseAutoshardedBot, self).__init__(
      command_prefix=commands.when_mentioned_or(config.base.command_prefix),
      help_command=None,
      case_insensitive=True,
      allowed_mentions=disnake.AllowedMentions(roles=False, everyone=False, users=True),
      intents=intents,
      sync_commands=True,
      max_messages=config.essentials.max_cached_messages
    )
    self.initialized = False

    self.last_error = None
    self.start_time = datetime.datetime.utcnow()

    self.http_session = ClientSession(timeout=ClientTimeout(total=15))

    self.event(self.on_ready)
    init_tables()

    for cog in command_utils.get_cogs_in_folder("core_extensions"):
      try:
        self.load_extension(f"core_extensions.{cog}")
        logger.info(f"{cog} loaded")
      except:
        output = traceback.format_exc()
        logger.error(f"Failed to load {cog} module\n{output}")
        exit(-2)
    logger.info("Protected modules loaded")

    for cog in config.base.default_loaded_extensions:
      try:
        self.load_extension(f"extensions.{cog}")
        logger.info(f"{cog} loaded")
      except:
        output = traceback.format_exc()
        logger.warning(f"Failed to load {cog} module\n{output}")
    logger.info("Defaul modules loaded")

  async def on_ready(self):
    if self.initialized: return
    self.initialized = True

    logger.info(f"Logged in as: {self.user} (ID: {self.user.id}) on {self.shard_count} shards")
    await self.change_presence(activity=disnake.Game(name=config.base.status_message, type=0), status=disnake.Status.online)
    log_channel = await object_getters.get_or_fetch_channel(self, config.base.log_channel_id)
    if log_channel is not None:
      await message_utils.generate_success_message(log_channel, "Bot is ready!")
    logger.info("Ready!")
