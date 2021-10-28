from types import CoroutineType
from types import FunctionType
from typing import Optional

import discord

from bot import config
from bot.engine import BaseGame


class Controls(discord.ui.View):
    def __init__(self, game, **kwargs):
        self.game = game
        self._callback: Optional[CoroutineType] = None

        kwargs.pop('timeout', None)
        super().__init__(**kwargs, timeout=600)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self

    async def on_error(self, error: Exception, *_):
        raise error  # Let the error handler take care of it

    def button(self, *args, **kwargs):
        def wrapper(func):
            button = discord.ui.Button(*args, **kwargs)

            async def cb_wrapper(*_):
                func()

            button.callback = cb_wrapper
            self.add_item(button)
            return func

        return wrapper


class DefaultControls(Controls):
    def __init__(self, game: BaseGame, **kwargs):
        emotes = config['skins'][0]['controls']
        super().__init__(game, **kwargs)

        @self.button(label='\u200c', disabled=True, style=discord.ButtonStyle.grey)
        def _():
            pass

        @self.button(emoji=emotes['drop'][1])
        def hard_drop():
            game.piece.x += game.board.shape[0]
            game.lock_piece()

        @self.button(label='\u200c', disabled=True, style=discord.ButtonStyle.grey)
        def _():
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
