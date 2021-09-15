import discord
from discord.ext import commands

from bot.lib.game import Game, Pieces


class Controls(discord.ui.View):
    def __init__(self, game: Game, ctx: commands.Context, message: discord.Message):
        super().__init__()
        self.game = game
        self.ctx = ctx
        self.message = message

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.ctx.author

    @discord.ui.button(label='\u200c', disabled=True, row=0)
    async def _0(self, *_):
        pass

    @discord.ui.button(label='⇊', style=discord.ButtonStyle.primary, row=0)
    async def hard_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.hard_drop()
        await self.update_message()

    @discord.ui.button(label='\u200c', disabled=True, row=0)
    async def _1(self, *_):
        pass

    @discord.ui.button(label='⤭', style=discord.ButtonStyle.primary, row=0)
    async def swap(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.swap()
        await self.update_message()

    @discord.ui.button(label='🗘', style=discord.ButtonStyle.primary, row=0)
    async def rotate_cw2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.rotate(2)
        await self.update_message()

    @discord.ui.button(label='🡸', style=discord.ButtonStyle.primary, row=1)
    async def move_left(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.drag(-1)
        await self.update_message()

    @discord.ui.button(label='🡻', style=discord.ButtonStyle.primary, row=1)
    async def soft_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.soft_drop()
        await self.update_message()

    @discord.ui.button(label='🡺', style=discord.ButtonStyle.primary, row=1)
    async def move_right(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.drag(+1)
        await self.update_message()

    @discord.ui.button(label='↺', style=discord.ButtonStyle.primary, row=1)
    async def rotate_ccw(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.rotate(-1)
        await self.update_message()

    @discord.ui.button(label='↻', style=discord.ButtonStyle.primary, row=1)
    async def rotate_cw(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.rotate(+1)
        await self.update_message()

    async def update_message(self):
        self.swap.disabled = self.game.hold_lock
        embed = discord.Embed(
            color=0xfa50a0,
            title=self.game.action_text or discord.Embed.Empty,
            description=self.game.get_text()
        )
        embed.add_field(
            name='Hold', value=f'`{Pieces(self.game.hold).name}`' if self.game.hold is not None else '`None`'
        )
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in self.game.queue))
        embed.add_field(
            name='Score', value=f'**{self.game.score:,}** +{self.game.score - self.game.previous_score}'
        )
        embed.set_footer(text=self.ctx.author, icon_url=self.ctx.author.avatar)
        await self.message.edit(embed=embed, view=self)
