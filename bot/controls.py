from collections.abc import Callable
from typing import Optional

import discord

from bot import config
from bot.engine import BaseGame


class Controls(discord.ui.View):
    def __init__(self, game: BaseGame):
        self.game = game
        # FIXME: how do you even type coroutines what
        self._callback: Optional[Callable] = None
        self._check: Optional[Callable] = None
        super().__init__(timeout=600)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self._check is not None:
            return await self._check(interaction)

        return False

    def set_check(self, func: Callable):
        self._check = func

    async def callback(self, interaction: discord.Interaction):
        if self._callback is not None:
            await self._callback(interaction)

    def set_callback(self, func: Callable):
        self._callback = func

    async def on_error(self, error: Exception, *_):
        raise error  # Let the error handler take care of it

    def button(self, **kwargs):
        def wrapper(func):
            button: discord.ui.Button = discord.ui.Button(**kwargs)
            # Above is for `bot/controls.py:39: error: Need type annotation for "button"`

            async def cb_wrapper(*_):
                func()
                await self.callback(*_)

            button.callback = cb_wrapper  # type: ignore
            self.add_item(button)
            return func

        return wrapper


class DefaultControls(Controls):
    def __init__(self, game: BaseGame):
        emotes = config.data['skins'][0]['controls']
        super().__init__(game)

        @self.button(label='\u200c', disabled=True, style=discord.ButtonStyle.grey)
        def _0():
            pass

        @self.button(emoji=emotes['drop'][1])
        def hard_drop():
            game.piece.x += game.board.shape[0]
            game.lock_piece()

        @self.button(label='\u200c', disabled=True, style=discord.ButtonStyle.grey)
        def _1():
            pass

        @self.button(emoji=emotes['swap'])
        def swap():
            game.swap()

        @self.button(emoji=emotes['rotate'][2])
        def rotate_180():
            game.piece.rot += 2

        @self.button(emoji=emotes['drag'][0])
        def move_left():
            game.piece.y -= 1

        @self.button(emoji=emotes['drop'][0])
        def soft_drop():
            game.piece.x += 5

        @self.button(emoji=emotes['drag'][1])
        def move_right():
            game.piece.y += 1

        @self.button(emoji=emotes['rotate'][0])
        def rotate_ccw():
            game.piece.rot -= 1

        @self.button(emoji=emotes['rotate'][1])
        def rotate_cw():
            game.piece.rot += 1
