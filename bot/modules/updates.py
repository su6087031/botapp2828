import sys
import subprocess
import heroku3

from datetime import datetime
from os import environ, execle, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from pyrogram import filters

from bot import app, OWNER_ID, UPSTREAM_REPO, UPSTREAM_BRANCH, bot
from bot.helper.ext_utils.heroku_utils import HEROKU_URL
from bot.helper.telegram_helper.bot_commands import BotCommands

REPO_ = UPSTREAM_REPO
BRANCH_ = UPSTREAM_BRANCH


def gen_chlog(repo, diff):
    ch_log = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += f'• [{c.committed_datetime.strftime(d_form)}]: {c.summary} **{c.author}**\n'
    return ch_log

# Update Command


@app.on_message(filters.command([BotCommands.UpdateCommand, f'{BotCommands.UpdateCommand}@{bot.username}']) & filters.user(OWNER_ID))
async def update_it(client, message):
    msg_ = await message.reply_text("`Succuesfully connected to SparkxCloud.org, Updating Please Wait!`")
    text = message.text.split(" ", 1)
    try:
        repo = Repo()
    except GitCommandError:
        return await msg_.edit(
            "**Invalid Git Command. Please Report This Bug To [Support Group](https://t.me/SparkXcloud)**"
        )
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "upstream" in repo.remotes:
            origin = repo.remote("upstream")
        else:
            origin = repo.create_remote("upstream", REPO_)
        origin.fetch()
        repo.create_head(UPSTREAM_BRANCH, origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
        if repo.active_branch.name != UPSTREAM_BRANCH:
            return await msg_.edit(
            f"`Seems Like You Are Using Custom Branch - {repo.active_branch.name}! Please Switch To {UPSTREAM_BRANCH} To Make This Updater Function!`"
        )
    try:
        repo.create_remote("upstream", REPO_)
    except BaseException:
