from typing import Optional

import hikari
import lightbulb
import tetris

from src.config import config

plugin = lightbulb.Plugin("Tetris", "Play tetris!")


MOVES = {
    "left": tetris.Move.left(),
    "right": tetris.Move.right(),
    "das-left": tetris.Move.left(10),
    "das-right": tetris.Move.right(10),
    "soft-drop": tetris.Move.soft_drop(5),
    "hard-drop": tetris.Move.hard_drop(),
    "rotate-ccw": tetris.Move.rotate(-1),
    "rotate-cw": tetris.Move.rotate(+1),
    "rotate-2cw": tetris.Move.rotate(+2),
    "swap": tetris.Move.swap(),
}


class DiscordGame(tetris.BaseGame):
    def render(self, tiles: list[str], lines: Optional[int] = None) -> str:
        return super().render(
            tiles=tiles,
            lines=lines or 4096 // (max(map(len, tiles)) * (self.board.shape[1] + 1)),
        )

    def embed(self, ctx: lightbulb.Context, tiles: list[str]) -> hikari.Embed:
        embed = hikari.Embed(description=self.render(tiles=tiles))
        embed.add_field(
            "Queue", ",".join("`" + i.name + "`" for i in self.queue[:4]), inline=True
        )
        embed.add_field(
            "Hold", "`" + self.hold.name + "`" if self.hold else "`None`", inline=True
        )
        embed.add_field("Score", f"**{self.score:,}**")
        embed.set_footer(
            text=ctx.author.username,
            icon=ctx.author.avatar_url or ctx.author.default_avatar_url,
        )

        return embed


def build_components(
    ctx: lightbulb.Context,
    layout: list[list[str]],
    emojis: dict[str, str],
) -> list[hikari.api.ActionRowBuilder]:
    rows = []

    for i in layout:
        row = ctx.bot.rest.build_action_row()
        for j in i:
            if j.startswith("noop"):
                (
                    row.add_button(hikari.ButtonStyle.SECONDARY, j)
                    .set_label("\u200c")
                    .set_is_disabled(True)
                    .add_to_container()
                )
            else:
                (
                    row.add_button(hikari.ButtonStyle.PRIMARY, j)
                    .set_label(emojis[j])
                    .add_to_container()
                )

        rows.append(row)

    return rows


@plugin.command
@lightbulb.option("mode", "What mode to play", default="zen", choices=["zen"])
@lightbulb.command("play", "Start a game of tetris")
@lightbulb.implements(lightbulb.SlashCommand)
async def tetris_play(ctx: lightbulb.SlashContext):
    skin = config["skins"][0]

    game = DiscordGame()
    embed = game.embed(skin["pieces"])
    embed.colour = 0xFA509F

    layout = [
        ["noop", "hard-drop", "noop1", "swap", "rotate-2cw"],
        ["left", "soft-drop", "right", "rotate-ccw", "rotate-cw"],
    ]

    resp = await ctx.respond(
        embed=embed, components=build_components(ctx, layout, skin["controls"])
    )

    message = await resp.message()

    with ctx.bot.stream(hikari.InteractionCreateEvent, 240).filter(
        lambda e: (
            isinstance(e.interaction, hikari.ComponentInteraction)
            and e.interaction.user == ctx.author
            and e.interaction.message == message
        )
    ) as stream:
        async for event in stream:
            cid = event.interaction.custom_id
            game.push(MOVES[cid])

            embed = game.embed(skin["pieces"])
            embed.colour = 0xFA509F

            if game.lost:
                embed.colour = 0xFA5050
                embed.title = "Top out!"
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE, embed=embed, components=[]
                )
                return

            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_UPDATE, embed=embed
            )

    embed = game.embed(skin["pieces"])
    embed.colour = 0xFA5050
    embed.title = "Timed out!"

    await ctx.interaction.edit_initial_response(embed=embed, components=[])
    await ctx.interaction.execute(
        "This game timed out due to inactivity, but you can resume it with /play!",
        flags=hikari.MessageFlag.EPHEMERAL,
    )


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
