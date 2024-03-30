from telegram import Update
from telegram.ext import (
    ContextTypes
)
from telegram import ReplyKeyboardMarkup
from settings import config
import traceback
import html
import json
from telegram.constants import ParseMode
from common.log import logger

DEVELOPER_CHAT_ID = config.DEVELOPER_CHAT_ID

# TODO : ID of the group to which the coordinates will be sent.

GROUP_COORDINATES_ID = int(config.CHAT_ID)

# TODO : List of users allowed to activate the commands

ALLOWED_USERS = [int(config.SUPPORT), int(config.ADMIN)]

async def text_handler(upadate : Update, context : ContextTypes.DEFAULT_TYPE):
    if Update..message is None:
        return
    
    # TODO : Verify if the message comes from the allowed group.
    
    if Update