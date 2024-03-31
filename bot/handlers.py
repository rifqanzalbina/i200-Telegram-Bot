
# ! Import Library
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

async def text_handler(update : Update, context : ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    
    
    # TODO : Verify if the message comes from the allowed group.
    if update.effective_chat.id != GROUP_COORDINATES_ID:
        await update.message.reply_text(
            "The command can only be activated in the @top100galaxy1 group. Translate to English."
        )
        return
    
    # TODO : Verify if the user is allowed to use the command.
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("You do not have permission to use this command.")
        return
    
    job = context.chat_data.get("callback_coordinate")
    
    if job : 
        await update.message.reply_text(
            "Sorry, there is already an active instance of the bot. Please wait for it to stop before starting another one."
        )
        return
    
    # TODO : If there is no active instance, proceed with handling the message.
    
    user_name = update.effective_user.first_name
    message_text = "Hello {user_name}, welcome to Adventure Elements!"
    message_text += "This is an explanatory menu:\n\n"
    message_text += "/iv100 - Starts sending coordinates with IV 100."
    message_text += "/iv90 - Starts sending coordinates with IV 90."
    message_text += "/stop - Stops the sending of coordinates."
    
    keyboard = [["/iv100", "/iv90","/stop"]]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True, resize_keyboard=True
    )

    await update.message.reply_text(message_text, reply_markup=reply_markup)

async def error_handler(update : Update, context : ContextTypes.DEFAULT_TYPE) -> None:
    # ! Log the error and send a telegram message to notify the developer.
    
    # $ Limit the message length if it is too long.
    
    max_message_length = 4000
    
    try : 
        logger.error("Exception while handling an update", exc_info=context.error)
        
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        
        tb_string = "".join(tb_list)
        
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            "An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )
        
        if len(message) > max_message_length:
            message = (
                message[:max_message_length]
                +"[...Message truncated due to length...]"
            )
            
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        print("Error in error_handler(): {e}")
    