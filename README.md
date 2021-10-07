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

If you wish to contribute or just fork off this, the following should work:

**Requirements:**

-   Python >= 3.9
-   [Poetry](https://python-poetry.org/)

And of course, a discord bot token, create one [here](https://discord.com/developers/applications)

**Install the project:**

Simply run `poetry install`.

**Set the token:**

Create a new file named `TOKEN` on the project's root and write the bot token into it

**Edit your config** _(optional)_:

If you skip this option, `config_defaults.json` will be copied automatically to `config.json`

-   Copy `config_defaults.json` into `config.json`
-   Edit `"prefix": "tt!"` to whatever you'd prefer
-   If wanted, setup skins:
    -   Upload the emotes into a server you and the bot share, named as so:
        -   `I_`, `L_`, `J_`, `S_`, `Z_`, `O_` - the actual piece tiles
        -   `BG` - The background tile
        -   `GA` - Garbage piece tile
        -   `GH` - Ghost piece tile
    -   For each skin, set the following:
        -   `"name": ...`: whatever you wish
        -   `"pieces": ...`: Should be a list of the emote formats (i.e. `<:NAME:ID>`), ordered as `BG`, `I_`, `L_`, `J_`, `S_`, `Z_`, `O_`, `GA`, `GH`

**Run the bot:**

Enter a pipenv shell with `poetry shell` and run `python3 -m bot`

**Set the status message** _(optional)_:

On the channel you want, run `[prefix]setpersiststs`, this is the same on #data in the discord server and is periodically edited with the bot's stats

**That's it, you should now have an instance running! :D**

## How

A bit too much of free time, [`discord.py`](https://github.com/Rapptz/discord.py/), [`numpy`](https://numpy.org/), [`tinydb`](https://tinydb.readthedocs.io/) and maybe some magic.

Yes, this gets rate-limited, yes, it does only use emotes, no, it is not resource-heavy at all, no, I don't mind if you break the bot (please do report it though!).

## Credits

This project is maintained and mainly developed by me ([dzshn](https://dzshn.xyz/)). My friend [zuli](https://www.instagram.com/zulimations/) (also: [twitter](https://twitter.com/zulimations)) is doing all graphics stuff (they'd suck otherwise!1!!), so very very much thanks to him!!

I'd also like to thank everyone coming from my [reddit post](https://www.reddit.com/r/discordapp/comments/pqqdnt/thought_some_of_you_might_like_what_im_currently/) (and now other places!?)! :D

I did not expect to get as much attention, and it has been quite fun to work on this knowing people are also enjoying it as much as I like to work on it :)

And of course, this also runs on lots and lots of open-source software, but you probably know that..

## What's missing from guidelines

-   **Full board size**, there's not enough space for 20 lines if using custom emotes, so instead there are 16 (although pieces do spawn at rows 21-22)
-   ??????
-   i forgor 💀
