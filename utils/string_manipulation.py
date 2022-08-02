import math
from typing import List, Tuple

def add_string_until_length(strings:List[str], max_length:int, sep:str) -> Tuple[str, List[str]]:
  output = ""
  number_of_strings = len(strings)
  for _ in range(number_of_strings):
    string = strings.pop(0)
    tmp_output = (output + string) if output == "" else (output + sep + string)
    if len(tmp_output) > max_length:
      break
    output = tmp_output
  return output, strings

def truncate_string(string: str, limit: int, ellipsis :str="…", from_beginning: bool=False) -> str:
  if len(string) <= limit: return string

  if from_beginning:
    return ellipsis + string[len(string) - limit + len(ellipsis):]
  else:
    return string[:limit - len(ellipsis)] + ellipsis

def split_to_parts(items: str, length: int) -> List[str]:
  result = []

  for x in range(math.ceil(len(items) / length)):
    result.append(items[x * length:(x * length) + length])

  return result