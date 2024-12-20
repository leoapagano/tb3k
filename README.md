# tb3k

tb3k is a Python-based Discord bot with numerous cool, fun, and fancy features such as birthday tracking, and with many more planned.

To setup, make sure your installed `python3` and `pip` are up to date. Then,

```bash
$ echo "DISCORD_TOKEN='AUTH_TOKEN'" >> ./.env
$ python3 -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```

Note that AUTH_TOKEN should be replaced with your Discord bot's authentication token. You can get this at [discord.dev](discord.dev).

To run:

```bash
$ python3 ./tb3k.py
```

## Functioality

### Say

You can tell tb3k to say something by adding your Discord user ID to the AUTHORIZED_USER_IDS list in `cogs/say.py` (TODO: move this to a preferences file). Then, use the `/say` command.

### Birthday Tracking

In each Discord server this bot is added to, the other users of that server can opt to set their birthday with the `/set-birthday` command. On their birthday, this bot will display a nice little "Happy Birthday!" message for this user in the server's system channel (if it has one). If the user later decides they don't want their birthday announced, they can unset it any time with `/unset-birthday`. They can also check the birthdays of other users in that server with `/get-birthday`. Please keep in mind that birthdays do not carry over across servers and must be set for each server in which both the user and this bot are in. The message prints out at 7AM every day, Eastern time (TODO: move this to a preferences file). 

## About data.json

When certain commands are run, tb3k saves information to a file called `data.json` in the current working directory. Any time a command which saves a state (such as birthday tracking) is run, the state is saved and backed up to this file. `data.json` is an important file which holds all of the states for this bot for all servers which it is in. In production hosting, be sure to back this file up regularly.
