import discord
from discord.ext import commands
from tinydb import TinyDB, where


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.db: TinyDB = bot.db

    @commands.command(aliases=['config', 'cfg'])
    async def settings(self, ctx: commands.Context, name: str = None, value: str = None):
        query = (where('user_id') == ctx.author.id)
        if not self.db.table('settings').contains(query):
            self.db.table('settings').insert({'user_id': ctx.author.id})

        default = {'skin': 0, 'controls': 0}
        names: dict[str, list[str]] = {'skin': ['default'], 'controls': ['basic', 'advanced']}
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

            await ctx.send(f'`{name}` is set to `{names[name][user_settings[name]]}`')

        else:
            name = name.lower()
            value = value.lower()
            if name not in user_settings:
                raise commands.BadArgument(f"Setting {name} doesn't exist")
            if value not in names[name]:
                raise commands.BadArgument(f"{value} isn't a valid for setting {name}")

            self.db.table('settings').upsert({name: names[name].index(value)}, query)
            await ctx.send(f'Updated `{name}` to {value}!')


def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))
