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
@lightbulb.command("play", "Start a game of tetris", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def tetris_play(ctx: lightbulb.Context):
    skin = config["skins"][0]

    game = tetris.BaseGame()
    embed = hikari.Embed(description=game.render(tiles=skin["pieces"], lines=14))

    embed.set_footer(
        text=ctx.author.username,
        icon=ctx.author.avatar_url or ctx.author.default_avatar_url,
    )

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
            embed.description = game.render(tiles=skin["pieces"], lines=14)

            try:
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE, embed=embed
                )

            except hikari.NotFoundError:
                await event.interaction.edit_initial_response(embed=embed)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
