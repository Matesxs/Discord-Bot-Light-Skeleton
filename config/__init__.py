from features import dictionary_store
from . import cooldowns
from .strings import Strings

config = dictionary_store.DictionaryStore.from_toml("config/config.toml", "config/config.template.toml")
