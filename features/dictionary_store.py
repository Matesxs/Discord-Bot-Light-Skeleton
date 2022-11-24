# Parsing and storing of json-like data in object as attributes

import os
import toml

class DictionaryStore:
  def to_dict(self):
    def convert(value, attr_name=None):
      if isinstance(value, DictionaryStore):
        return value.to_dict()
      elif isinstance(value, list):
        return [convert(item) for item in value]
      elif hasattr(self, "__environment__") and attr_name in self.__environment__:
        return "<env>"
      else:
        return value

    return { attr: convert(getattr(self, attr), attr) for attr in self.__exportable__   }

  def __repr__(self):
    return f'{type(self).__name__}.parse({self.to_dict()!r})'

  def write(self, path):
    with open(path, "w", encoding="utf-8") as fd:
      toml.dump(self.to_dict(), fd)

  @classmethod
  def parse(cls, obj, obj_key=None):
    if isinstance(obj, list):
      return [cls.parse(v) for v in obj]
    elif isinstance(obj, dict):
      result = cls()
      result.__exportable__ = []
      result.__environment__ = []
      for k, v in obj.items():
        result.__exportable__.append(k)
        if k == "<env>":
          result.__environment__.append(k)
        setattr(result, k, cls.parse(v, k))
      return result
    elif isinstance(obj, str) and obj == "<env>":
      assert obj_key is not None
      return os.getenv(obj_key)
    else:
      return obj

  @classmethod
  def from_toml(cls, *paths, **kwargs):
    existing_paths = [*filter(os.path.exists, paths)]
    if len(existing_paths) == 0:
      raise ValueError(f'none of {paths} were found')
    return cls.parse(toml.load(existing_paths[0], **kwargs))

  @classmethod
  def from_json(cls, data: dict):
    return cls.parse(data)