import secrets

import discord
from discord.ext import commands

import engine
from bot import config
from bot import controls
from bot.modes import base
from engine import encoder
from engine.mixins import StandardScore


class ZenGame(StandardScore, engine.BaseGame):
    pass


class ZenMode(base.BaseMode, name='zen', game_cls=ZenGame):
    async def command(self, ctx: commands.Context):
        game = ZenGame()
        if await self.db.exists(f'zen:{ctx.author.id:x}'):
            h = await self.db.hgetall(f'zen:{ctx.author.id:x}')
            game.board = encoder.decode(h[b'board']).board
            game.piece = engine.Piece(
                board=game.board, type=engine.PieceType(int(h[b'piece']))
            )
            game.score = int(h[b'score'])
            game.queue = engine.Queue(
                queue=list(h[b'queue'][:4]),
                bag=list(h[b'queue'][4:]),
                seed=secrets.token_bytes(),
            )
            game.hold_lock = int(h[b'hold']) & (1 << 4)
            game.hold = int(h[b'hold']) ^ (1 << 4)

        view = controls.DefaultControls(game)

        self.cog.games[ctx.author.id] = game, view

        message = await ctx.send(content='\u200c', view=view)
        view.set_callback(self.get_callback(game, message, view))
        view.set_check(self.get_check(ctx))
        await self.update_message(game, message, view)
        await view.wait()

        del self.cog.games[ctx.author.id]
        await self.db.hset(
            f'zen:{ctx.author.id:x}',
            mapping={
                'board': encoder.encode(game.board),
                'piece': game.piece.type.value,
                'score': game.score,
                'queue': bytes(game.queue.pieces + game.queue.bag),
                'hold': (game.hold or 0) + (game.hold_lock << 4),
            },
        )

    async def update_message(
        self, game: ZenGame, message: discord.Message, view: discord.ui.View
    ):
        embed = discord.Embed(
            color=0xFA50A0,
            description=game.render(tiles=config.data['skins'][0]['pieces'], lines=16),
        )

        embed.add_field(name='Score', value=game.score)

        await message.edit(content=None, embed=embed, view=view)
