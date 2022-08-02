# Basic scroller for embeds
# Inspired by https://github.com/Toaster192/rubbergod/blob/master/buttons/embed.py

import disnake
from typing import List, Optional, Union

from utils import message_utils

def pagination_next(id: str, page: int, max_page: int, roll_around: bool = True):
  if 'next' in id:
    next_page = page + 1
  elif 'prev' in id:
    next_page = page - 1
  elif 'start' in id:
    next_page = 1
  elif 'end' in id:
    next_page = max_page
  else:
    return 0

  if 1 <= next_page <= max_page:
    return next_page
  elif roll_around and next_page == 0:
    return max_page
  elif roll_around and next_page > max_page:
    return 1
  else:
    return 0

reaction_ids = ["embed:start_page", "embed:prev_page", "embed:next_page", "embed:end_page"]

class EmbedView(disnake.ui.View):

  def __init__(self, author: disnake.User, embeds: List[disnake.Embed], perma_lock: bool = False, roll_arroud: bool = True, end_arrow: bool = True, timeout: Optional[float] = 300, invisible: bool=False):
    self.message: Optional[Union[disnake.Message, disnake.ApplicationCommandInteraction, disnake.ModalInteraction, disnake.MessageCommandInteraction]] = None
    self.page = 1
    self.author = author
    self.locked = False
    self.roll_arroud = roll_arroud
    self.perma_lock = perma_lock
    self.embeds = embeds
    self.max_page = len(embeds)
    self.invisible = invisible
    super().__init__(timeout=timeout)

    if self.max_page > 1:
      self.add_item(
        disnake.ui.Button(
          emoji="⏪",
          custom_id="embed:start_page",
          style=disnake.ButtonStyle.primary
        )
      )
      self.add_item(
        disnake.ui.Button(
          emoji="◀",
          custom_id="embed:prev_page",
          style=disnake.ButtonStyle.primary
        )
      )
      self.add_item(
        disnake.ui.Button(
          emoji="▶",
          custom_id="embed:next_page",
          style=disnake.ButtonStyle.primary
        )
      )
      if end_arrow:
        self.add_item(
          disnake.ui.Button(
            emoji="⏩",
            custom_id="embed:end_page",
            style=disnake.ButtonStyle.primary
          )
        )
      if not perma_lock:
        # if permanent lock is applied, dynamic lock is removed from buttons
        self.lock_button = disnake.ui.Button(
          emoji="🔓",
          custom_id="embed:lock",
          style=disnake.ButtonStyle.success
        )
        self.add_item(self.lock_button)

  def embed(self):
    page = self.embeds[self.page - 1]
    page.set_author(name=f"{self.page}/{self.max_page}")
    return page

  async def run(self, ctx):
    if isinstance(ctx, (disnake.ApplicationCommandInteraction, disnake.ModalInteraction, disnake.MessageCommandInteraction, disnake.CommandInteraction)):
      await ctx.send(embed=self.embed(), view=self, ephemeral=self.invisible)
      self.message = ctx
    else:
      self.message = await ctx.send(embed=self.embed(), view=self)

  async def interaction_check(self, interaction: disnake.MessageInteraction) -> None:
    if interaction.data.custom_id == "embed:lock":
      if interaction.author.id == self.author.id:
        self.locked = not self.locked
        if self.locked:
          self.lock_button.style = disnake.ButtonStyle.danger
          self.lock_button.emoji = "🔒"
        else:
          self.lock_button.style = disnake.ButtonStyle.success
          self.lock_button.emoji = "🔓"
        await interaction.response.edit_message(view=self)
      else:
        await message_utils.generate_error_message(interaction, "You are not author of this embed")
      return

    if interaction.data.custom_id not in reaction_ids or self.max_page <= 1:
      return
    if (self.perma_lock or self.locked) and interaction.author.id != self.author.id:
      await message_utils.generate_error_message(interaction, "You are not author of this embed")
      return

    self.page = pagination_next(
      interaction.data.custom_id,
      self.page,
      self.max_page,
      self.roll_arroud
    )
    await interaction.response.edit_message(embed=self.embed())

  async def on_timeout(self):
    try:
      self.clear_items()
      if isinstance(self.message, disnake.Message):
        await self.message.edit(view=self)
      else:
        await self.message.edit_original_message(view=self)
    except:
      pass
