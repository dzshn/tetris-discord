# tetris-discord

Tetris! but on discord! it's also [_almost_](#what-s-missing-from-guidelines) guideline compliant, i think

This is still in an alpha state, but apart from the 8 times I somehow yote user data, I say it's quite stable! or at least playable, idk..

More info can be found on [it's website](https://tetris-dsc.dzshn.xyz). If you want to check it out now, you can join the [Discord server](https://discord.gg/ytJj3eQ74B) or [invite the bot](https://discord.com/api/oauth2/authorize?client_id=883520648553594920&permissions=116736&scope=bot%20applications.commands)!

Also, for development progress you can check the [v1.0.0 project](https://github.com/dzshn/tetris-discord/projects/2) on this repo and the [issues tab](https://github.com/dzshn/tetris-discord/issues), I keep them up-to-date

## Table of contents

1. [Setup](#setup)
2. [How](#how)
3. [Credits](#credits)
4. [Missing guideline stuff](#whats-missing-from-guidelines)

## Setup

_**Docker package soon:tm:**_

If you wish to contribute or just fork off this, the following should work:

**Requirements:**

-   [Python](https://www.python.org/) >= 3.9 \*
-   [Poetry](https://python-poetry.org/)
-   [redis-server](https://redis.io/) _(optional\*)_
-   A discord bot account _(create one [here](https://discord.com/developers/applications)!)_

_⁰\*: currently tested on `3.9.7`/`3.9.5`, I recommended [pyenv](https://github.com/pyenv/pyenv/) if you don't have these_

_¹\*: if no redis server is found running on `localhost:6379`, the bot will fallback to [fakeredis](https://github.com/jamesls/fakeredis) and will **not** save any data_

**Install the project and dependencies:**

Simply run `poetry install`!

**Configure the bot**

-   **Set the token**

    Create a new file named `TOKEN` on the project's root and write the bot token into it, this is the only required setting

-   **Setup `config.yaml`**:

    Copy `config.sample.yaml` into `config.yaml` and edit it as necessary, the most important settings are:

    _**Note:** to prevent issues with old configs, if the config isn't found to be complete, it'll be ignored and `config.sample.yaml` will be used instead, so make sure to keep all config keys!_

**Run the bot:**

_**::** If you wish to use redis, just run `redis-server redis.conf` on another terminal_

Simply:

```sh
~$ poetry shell
Spawning shell within ~/.cache/pypoetry/virtualenvs/tetris-...-py3.9
(tetris-...-py3.9) ~$ python -m bot

# ..or run directly:
~$ poetry run python3 -m bot
```

**That's it, you should now have an instance running! :tada:**

## How

A bit too much of free time, a lot of coffee, ~~[`discord.py`](https://github.com/Rapptz/discord.py/)~~ [`nextcord`](https://github.com/nextcord/nextcord) (!), [`numpy`](https://numpy.org/), ~~[`tinydb`](https://tinydb.readthedocs.io/)~~ [`redis`](https://redis.io/), probably at least 40 deps and sub-deps... and maybe some magic.

erh.. I mean, the internal stuff pretty much what you'd need implementing a tetris game with proper [SRS](https://harddrop.com/wiki/SRS) rotation (I know that's _just_ the rotation system, but if you take a look around you'll probably understand why!), so not much specific on that.. as with discord, it's just a "button click" -> "update message" loop, and the board is "rendered" using emotes

but, if you're interested in more technical stuff, the [`CONTRIBUTING.md`](CONTRIBUTING.md) file has some info on the project's structure!

## Credits

This project is maintained and mainly developed by me ([dzshn](https://dzshn.xyz/)). My friend [zuli](https://www.instagram.com/zulimations/) (also: [twitter](https://twitter.com/zulimations)) is doing all graphics stuff (they'd suck otherwise!1!!), so very very much thanks to him!!

I'd also like to thank everyone coming from my [reddit post](https://www.reddit.com/r/discordapp/comments/pqqdnt/thought_some_of_you_might_like_what_im_currently/) (and now other places!?)! :D

I did not expect to get as much attention, and it has been quite fun to work on this knowing people are also enjoying it as much as I like to work on it :)

And of course, this also runs on lots and lots of open-source software, but you probably know that..

## What's missing from guidelines

-   **Full board size**, there's not enough space for 20 lines if using custom emotes, so instead there are 16 (although pieces do spawn at rows 21-22)
-   ??????
-   i forgor 💀
