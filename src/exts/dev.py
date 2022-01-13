import collections
import contextlib
import io
import pprint
import sys
import textwrap
import time
import traceback

import hikari
import lightbulb
from lightbulb.commands import OptionModifier

from src.config import config

plugin = lightbulb.Plugin(
    "Dev", "Debug stuff", default_enabled_guilds=config["test-servers"]
)
plugin.add_checks(lightbulb.checks.owner_only)

eval_history = collections.deque()


@plugin.command
@lightbulb.option(
    "code", "The code to be executed", modifier=OptionModifier.CONSUME_REST
)
@lightbulb.command("eval", "evaluate some code")
@lightbulb.implements(lightbulb.SlashCommand)
async def dev_eval(ctx: lightbulb.Context):
    exec_time = time.perf_counter()

    code = ctx.options.code

    if "\n" not in code:
        code = "return " + code

    code = "async def func():\n" + textwrap.indent(code, "  ")

    code_return = None
    stdout = io.StringIO()
    stderr = io.StringIO()

    modules = {k: v for k, v in sys.modules.items() if "." not in k}
    shorthands = {
        "app": ctx.app,
        "ctx": ctx,
        "event": ctx.event,
        "author": ctx.author,
    }
    history = {}

    for i, j in enumerate(reversed(eval_history)):
        if i == 0:
            history["_"] = j
        else:
            history[f"_{i}"] = j

    env = modules | history | shorthands

    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            exec(code, env)
            code_return = await env["func"]()

        except Exception:
            traceback.print_exc()

    embed = hikari.Embed(
        title=f'Evaluated code with {"error" if stderr.getvalue() else "success"}!',
        description=f"{(time.perf_counter()-exec_time)*1000:g}ms :clock2:",
    )
    attachments = []

    results = [
        ("return", pprint.pformat(code_return, compact=True, width=50)),
        ("stdout", stdout.getvalue()),
        ("stderr", stderr.getvalue()),
    ]

    for name, value in results:
        if len(value) > 512:
            attachments.append(hikari.files.Bytes(value.encode(), f"{name}.py"))

        elif value:
            embed.add_field(name=name.title(), value=f"```py\n{value}\n```")

    if code_return is not None:
        eval_history.append(code_return)

    await ctx.respond(embed=embed)

    if attachments:
        await ctx.respond(attachments=attachments)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
