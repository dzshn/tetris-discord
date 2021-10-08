# Intro

Firstly, thanks for considering contributing!!

Below is some info that might help you get started, it shouldn't be a long read nor have strict rulings, if you have any questions or need any kind of help, please please don't hesitate in asking on the [Discord server](https://discord.gg/ytJj3eQ74B)! New contributors are really important and, I do wish to help!!

# Table of contents

1. [Intro](#intro)
2. [Opening an issue](#opening-an-issue)
3. [Making a pull request](#making-a-pull-request)
4. [Navigating the codebase](#navigating-the-codebase)

# Opening an issue

Is something wrong? have an enhancement idea? try this! if you're not comfortable with doing this on github, you can go to #support on the server!

You can open an issue [here](https://github.com/dzshn/tetris-discord/issues/new/choose)! if you need help writing one, the following may help:

## For bugs

-   What's actually supposed to happen?
-   What actually happens?
-   Are there errors reported? if so, what are they?
-   Can you reproduce it? if so, provide steps on doing so
-   Can you upload an screenshot?

## For feature requests

-   What's your idea? have you considered alternatives?
-   Do you have some examples on how it'd be useful for other people?
-   Is it a breaking change? (i.e. could it cause conflicts with the current code/data, or change how the bot is controlled)

---

Regardless, your issue might be worth looking into even if missing info!

# Making a pull request

Do feel free to do so! if you need more guidance for the codebase, you can ask me directly or open a draft PR! also, it'd help to ensure these:

## For code changes

You can read more on setting up an instance on the project's `README.md`, if you encounter any issues, also do contact me for help!

-   You should format the code using [`yapf`](https://pypi.org/project/yapf/) and check for errors with [`flake8`](https://flake8.pycqa.org/) (these are also set as dev dependencies, so you should have them in your pipenv!)
-   If your code is not backwards compatible, try to note how an instance would be migrated

It would also help to provide info on why the change is needed and how it'd help

## For documentation changes

uhmmmm, not much! just ensure the wording lines up with the rest of the docs and,,, yeah!

You can test how it'll look by running `python3 docs.py`, which will open a proper server locally for testing

---

And, the following might as well help you:

# Navigating the codebase

It is currently very subject to change and possibly confusing to go through, but do feel free to ask me about anything from it, I'm willing to help as much as I can :)

Most important modules are:

-   `bot/exts/*` ~ the actual d.py extensions that have all the commands
-   `bot/exts/modes/*` ~ these create the games
-   `bot/lib/game.py` ~ this is the actual game object, which other modes inherit from and manage via the commands
-   `bot/lib/controls.py` ~ the `discord.View` objects with callbacks to controlling the game objects

As well as other core stuff:

-   `bot/exts/manager.py` ~ currently handles updating the bot and closing games
-   `bot/exts/settings.py` ~ handles editing user settings
-   `bot/lib/maps.py` ~ currently the format used for saving boards (i.e. in zen mode)

There is also another external module, [yade](https://github.com/dzshn/yade), which is an project of mine with some quite useful commands for debugging, all of them are owner-only:

-   `[prefix]eval <code>` ~ directly evaluates code, you can access the bot object as `b` and the context as `ctx`
-   `[prefix]shell <command>` ~ executes given command in an async shell
-   `[prefix]geterror <token>` ~ uncaught errors get stored under a token, you can use that to get the traceback/context

Also! documentation is written as follows:

In short: the website is a SPA (Single-page application) written using [vue.js](https://vuejs.org/) and [vue-router](https://next.router.vuejs.org/) (not python, sorry!!), new pages are written in `docs/pages/` and added to the index in `docs/main.js`, these are markdown files parsed by [marked.js](https://marked.js.org/), and are only loaded as-needed

Most of the html code is actually at main.js, the "pages" are a lie :)

_(and yes, this does break 404s)_
