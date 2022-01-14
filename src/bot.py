import os

import hikari
import lightbulb

from src import exts
from src.config import config

bot = lightbulb.BotApp(
    token=os.environ.get("TOKEN") or open("TOKEN").read().strip(),
    intents=hikari.Intents.ALL_UNPRIVILEGED,
    default_enabled_guilds=config["test-servers"],
    banner=None,
)

bot.load_extensions_from(exts.__path__[0], must_exist=True)
