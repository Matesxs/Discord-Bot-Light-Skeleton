class CallableString(str):
  __call__ = str.format

class Formatable(type):
  def __init__(cls, clsname, superclasses, attributedict):
    cls.clsname = clsname

  def __getattribute__(cls, key):
    try:
      return CallableString(object.__getattribute__(cls, key))
    except AttributeError:
      raise AttributeError(f"{cls.clsname} class has no attribute {key}")