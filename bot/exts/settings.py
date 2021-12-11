from typing import Any

import discord
from discord.ext import commands
from tinydb import TinyDB
from tinydb import where

from bot.lib.maps import Encoder


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config: dict[str, Any] = bot.config
        self.db: TinyDB = bot.db

    @commands.command()
    async def preview(self, ctx: commands.Context):
        """Preview what your current config looks like in a game"""
        user_skin = (self.bot.db.table('settings').get(where('user_id') == ctx.author.id) or {}).get('skin', 0)
        board, piece = Encoder.decode('ACIAAAAAAlUAATMCZVdxMAZmF3EwAEQVUXcEQhNVdwIiEzM=@6+16+-1+1')
        ghost = piece.copy()
        ghost.x += 30
        for x, y in ghost.shape + ghost.pos:
            board[x, y] = 9

        for x, y in piece.shape + piece.pos:
            board[x, y] = piece.type

        await ctx.send(
            embed=discord.Embed(
                color=0xfa50a0,
                description='\n'.join(
                    ''.join(self.bot.config['skins'][user_skin]['pieces'][j] for j in i) for i in board[-16:]
                )
            )
        )

    @commands.command(aliases=['config', 'cfg'])
    async def settings(self, ctx: commands.Context, name: str = None, value: str = None):
        """Customise your gameplay"""
        query = (where('user_id') == ctx.author.id)
        if not self.db.table('settings').contains(query):
            self.db.table('settings').insert({'user_id': ctx.author.id})

        default = {'skin': 0, 'controls': 0}
        names: dict[str, list[str]] = {
            'skin': [i['name'] for i in self.config['skins']],
            'controls': ['basic', 'advanced', 'compact']
        }
        user_settings: dict[str, int] = (default | self.db.table('settings').get(query))
        user_settings.pop('user_id')
        if name is None:
            await ctx.send(
                embed=discord.Embed(
                    color=0xfa50a0,
                    title='Your settings',
                    description='\n'.join(f'**`{k}`**: `{names[k][v]}`' for k, v in user_settings.items())
                )
            )

        elif value is None:
            name = name.lower()
            if name not in user_settings:
                raise commands.BadArgument(f"Setting {name} doesn't exist")

            await ctx.send(
                f'`{name}` is set to `{names[name][user_settings[name]]}` of `{"`, `".join(names[name])}`'
            )

        else:
            name = name.lower()
            value = value.lower()
            if name not in user_settings:
                raise commands.BadArgument(f"Setting {name} doesn't exist")
            if value not in names[name]:
                raise commands.BadArgument(f"{value} isn't a valid for setting {name}")

            self.db.table('settings').upsert({name: names[name].index(value)}, query)
            await ctx.send(f'Updated `{name}` to `{value}`!')


def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))
