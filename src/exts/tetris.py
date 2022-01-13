import hikari
import lightbulb

from src.config import config

plugin = lightbulb.Plugin("Tetris", "Play tetris!")


@plugin.command
@lightbulb.option("mode", "What mode to play", default="zen", choices=["zen"])
@lightbulb.command("play", "Start a game of tetris", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def tetris_play(ctx: lightbulb.Context):
    skin = config["skins"][0]["controls"]

    layout = [
        ["noop", "hard-drop", "noop1", "swap", "rotate-2cw"],
        ["left", "soft-drop", "right", "rotate-ccw", "rotate-cw"],
    ]

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
                    .set_label(skin[j])
                    .add_to_container()
                )

        rows.append(row)

    resp = await ctx.respond("\u200c", components=rows)

    message = await resp.message()

    with ctx.bot.stream(hikari.InteractionCreateEvent, 240).filter(
        lambda e: (
            isinstance(e.interaction, hikari.ComponentInteraction)
            and e.interaction.user == ctx.author
            and e.interaction.message == message
        )
    ) as stream:
        async for event in stream:
            try:
                await event.interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE,
                    content=event.interaction.custom_id,
                )

            except hikari.NotFoundError:
                await event.interaction.edit_initial_response(
                    event,
                    content=event.interaction.custom_id,
                )


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
