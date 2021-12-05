import secrets

import discord
import numpy as np
from discord.ext import commands

import engine
from bot import config
from bot import controls
from bot.modes import base
from engine import encoder
from engine.mixins import StandardScore


class ZenGame(StandardScore, engine.BaseGame):
    def reset(self):
        self.seed = secrets.token_bytes()
        self.queue = engine.Queue(queue=[], bag=[], seed=self.seed)
        self.board = np.zeros((40, 10), dtype=np.int8)
        self.piece = engine.Piece(self.board, self.queue.pop())
        self.hold = None
        self.hold_lock = False


class ZenMode(base.BaseMode, name='zen', game_cls=ZenGame):
    async def command(self, ctx: commands.Context):
        game = ZenGame()
        if (save := await self.get_save(ctx.author)) is not None:
            game.board = encoder.decode(save['board']).board
            game.piece = engine.Piece(
                board=game.board, type=engine.PieceType(int(save['piece']))
            )
            game.score = int(save['score'])
            game.queue = engine.Queue(
                queue=list(save['queue'][:4]),
                bag=list(save['queue'][4:]),
                seed=secrets.token_bytes(),
            )
            game.hold_lock = bool(save['hlock'])
            game.hold = engine.PieceType(int(save['hold'])) if int(save['hold']) else None

        view = controls.DefaultControls(game)

        self.cog.games[ctx.author.id] = game, view

        message = await ctx.send(content='\u200c', view=view)
        view.set_callback(self.get_callback(game, message, view))
        view.set_check(self.get_check(ctx))
        await self.update_message(game, message, view)
        await view.wait()

        del self.cog.games[ctx.author.id]
        await self.save(
            ctx.author,
            {
                'board': encoder.encode(board=game.board),
                'piece': game.piece.type.value,
                'score': game.score,
                'queue': bytes(game.queue.pieces + game.queue.bag),
                'hold': int(game.hold) or 0,
                'hlock': game.hold_lock << 4,
            },
        )

    async def update_message(
        self, game: ZenGame, message: discord.Message, view: discord.ui.View
    ):
        embed = discord.Embed(
            color=0xFA50A0,
            description=game.render(tiles=config.data['skins'][0]['pieces'], lines=16),
        )

        embed.add_field(name='Score', value=f'**{game.score}**\n{game.score_delta:+}')
        embed.add_field(
            name='Queue', value=', '.join(f'`{i}`' for i in game.queue.pieces[:4])
        )
        embed.add_field(name='Hold', value=f'`{game.hold}`')

        await message.edit(content=None, embed=embed, view=view)
