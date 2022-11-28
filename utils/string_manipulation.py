import math
from typing import List, Tuple

def add_string_until_length(strings:List[str], max_length:int, sep:str) -> Tuple[str, List[str]]:
  output = ""
  while strings:
    string = strings[0]
    tmp_output = (output + string) if output == "" else (output + sep + string)
    if len(tmp_output) > max_length:
      break
      
    strings.pop(0)
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