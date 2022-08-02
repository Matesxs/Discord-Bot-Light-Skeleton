from features.base_bot import BaseAutoshardedBot
from config import config
from utils.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

if config.base.discord_api_key is None:
  logger.error("Discord API key is missing!")
  exit(-1)

bot = BaseAutoshardedBot()

bot.run(config.base.discord_api_key)
