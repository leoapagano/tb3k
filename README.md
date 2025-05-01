# tb3k

tb3k is a Python-based Discord bot with numerous cool, fun, and fancy features. These include:

- The ability to keep track of, and announce, the birthdays of server members
- The ability to send a custom response to messages matching specific regular expressions.

Other features are planned and will be available shortly.

## Setup

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

## Slash Commands and Bot Functioality

- In the slash command documentation below, a lock symbol (🔒) indicates a program that requires elevated permission to use.

### Say

The bot can be made to say anything by a trusted user.

- `/say message` (🔒): Makes tb3k say some `message` in the current channel.

You can tell tb3k to say something by adding your Discord user ID to the AUTHORIZED_USER_IDS list in `cogs/say.py` (TODO: move this to a preferences file). Then, use the `/say` command.

### Birthday Tracking

In each Discord server this bot is added to, the users of that server can opt to set their birthday such that a brief "Today is (user)'s birthday!" message will display. The following slash commands are available:

- `/get-birthday user`: Determines the birthday set by `user` for this server, if they have set one at all.
- `/set-birthday birthday`: Allows the user executing the command to set their birthday. `birthday` must be given as an ISO 8601 (YYYY-MM-DD) date.
- `/unset-birthday`: Allows the user exeucting the command to unset their birthday and opt out of birthday announcements.

One important thing to keep in mind is that birthdays are NOT global. If you set your birthday in one server with tb3k installed, and another server you're in installs tb3k, your birthday will not be set in the new server! This is because birthdays are uninitialized by default and must be set by the user.

The "happy birthday" messages, which are sent at 7AM every day in the system channel, takes the following form:

> "Today is $USER's $Nth birthday! Wish them a happy birthday!"

### Automatic Regex Responses

In each Discord server this bot is added to, permitted users may define regular expressions (regexes) which, for messages that match the regex, the bot will reply to with a predetermined message. The following slash commands are available:

- `/list-auto-responses page` (🔒): Displays a paginated list of all auto responses set on the server. Note that some long responses may be cut off.
- `/set-auto-response regex response` (🔒): Given a regular expression `regex` and a response phrase `response`, the bot will now respond to messages whose contents match that regex with `response`.
- `/unset-auto-response regex` (🔒): Disables a given regex response. As each unique `regex` only corresponds to one unique `response`, you select regex-response pairs using the `regex` argument.

As an example:

> `/set-auto-response "(?i)\bjoker\b" "Joker? I hardly know er!"`

In chat:

> You: "Man, I love having a holographic Joker on Ante 1."

> tb3k replies: "Joker? I hardly know er!"

This feature can also be useful for automatic moderation just as it is for fun.

## About data.json

When certain commands are run, tb3k saves information to a file called `data.json` in the current working directory. Any time a command which saves a state (such as birthday tracking) is run, the state is saved and backed up to this file. `data.json` is an important file which holds all of the states for this bot for all servers which it is in. In production hosting, be sure to back this file up regularly.
