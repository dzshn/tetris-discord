hi!! here are some info that may or may not help you help this project!

if you have any specific questions, you can ask them on the [Discord server](https://discord.gg/ytJj3eQ74B) or [contact me](https://dzshn.xyz) directly!

# Opening an issue

You can do so [here](https://github.com/dzshn/tetris-discord/issues/new/choose)! whether it's for a feature request or a bug or anything, you may ask it there

for short questions or just simple things in general, I'd really recommend not using the issue tracker for it, but don't worry too much about it!

something something provide as much info as you can byebye ty <3

# Making a PR

Feel free to do so!!! there are currently no proposed rules for it, but, if your PR is a code change, I'd like you to try to make sure it passes the [lint pipeline](.github/workflows/lint.yml):

-   after installing the project, if you did not provide the `--no-dev` option, you can format & lint the project with the same stuff by running:

    ```sh
    # actual usage of tox soon™
    ~$ poetry shell
    (tetris-...-py3.9) ~$ black .   # <- formatter
    (tetris-...-py3.9) ~$ isort .   # <- very cool thing that sorts imports
    (tetris-...-py3.9) ~$ flake8 .  # <- will scream if there is a possible error
    (tetris-...-py3.9) ~$ mypy .    # <- will scream if types aren't properly set
    ```

If you aren't able to do so, don't worry! those can be fixed via a rebase!

# what does this do!!!!!!!

good question! the code isn't properly documented (yet!), so here's some info I think might be helpful for starting!

**Structure:**

Currently, the bot itself is a package ([`bot/`](bot)), split into three major ones + a few single-file scripts:

-   [`bot.engine`](bot/engine): This has the core stuff for creating new games, mainly the `BaseGame` class, which is subclassed for each mode to add their own functionality. In fact though, this class can be used on it's own! e.g.::

    ```py
    >>> from bot.engine import BaseGame
    >>> game = BaseGame(seed='abcd')
    >>> game.queue
    Queue(queue=[<PieceType.S: 4>, <PieceType.T: 6>, <PieceType.O: 7>, <PieceType.Z: 5>], bag=[<PieceType.I: 1>, <PieceType.L: 2>])
    >>> p = lambda: print(game.render(lines=8))
    >>> p()

       @
       @@@
    >>> game.drag(y=-2)
    >>> game.hard_drop()
    >>> p()

        @@
     J @@
     JJJ
    >>>
    ```

    the main methods for this class are: `reset()`, `lock_piece()`, `render()`, `swap()`, `drag()`, `rotate()`, `hard_drop()`, `soft_drop()` (which are hopefully named concisely enough)

-   [`bot.exts`](bot/exts): These are all the d.py cogs that actually implement the discord commands, it's automatically loaded by `__main__.py`

-   [`bot.modes`](bot/modes): The actual game modes! each mode is a subclass of the base ABC (on [base.py](bot/modes/base.py)) that also goes along with a subclass of `BaseGame` (on [engine](bot/engine/__init__.py)), these are probably the scripts most prone to bugs too :p
