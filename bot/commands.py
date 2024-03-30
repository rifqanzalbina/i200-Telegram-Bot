"""FileCommander.py"""

### IMPORT LIBRARY
# ! Import Library
import asyncio
from bot.service import (
    generate_pokemon_messages,
    fetch_pokemon_data,
    coordinates_waiting_time,
)
from telegram import Update
from telegram.ext import ContextTypes
from settings import config
import telegram
from typing import List

# TODO : ID dari grup tempat koordinat akan dikirimkan
GROUP_COORDINATES_ID = int(config.CHAT_ID)

# TODO : Daftar pengguna yang diizinkan untuk mengaktifkan perintah
ALLOWED_USERS = [int(config.SUPPORT), int(config.ADMIN)]

PERIOD = int(config.PERIOD)

# NOTE : Send Coordinates
async def send_coordinates(
    context : ContextTypes.DEFAULT_TYPE, total_text : List[str], iv
):
    if total_text:
        messages_number = len(total_text)
        message_delay = 3 if len(total_text) > 20 else 2
        plural_letter = "" if messages_number == 1 else "s"
        await context.bot.send_message(
            chat_id=GROUP_COORDINATES_ID,
            text=f"send {messages_number} coordinate{plural_letter} IV {str(iv)}...",
        )
        for text in total_text:
            await context.bot.send_message(
                chat_id=GROUP_COORDINATES_ID, text=text, parse_mode="MarkdownV2"
            )        
            await asyncio.sleep(message_delay)
        await context.bot.send_message(
            chat_id=GROUP_COORDINATES_ID,
            text=f"No coordinates were found. I will search for more within {PERIOD} minutes.",
        )
    else:
        await context.bot.send_message(
            chat_id=GROUP_COORDINATES_ID,
            text = f"No coordinates were found. I will search for more within {PERIOD} minutes."
        )
            
# NOTE : Callback coordinate iv 90
async def callback_coordinate_iv_90(context : ContextTypes.DEFAULT_TYPE):
    try : 
        total_text = generate_pokemon_messages(90)
        await send_coordinates(context, total_text, 90)
    except telegram.error.RetryAfter as e:
        await asyncio.sleep(e.retry_after)
        message = (
            f"The sending of coordinates has been temporarily paused due to a speed limit."
            f"It will automatically resume in {e.retry_after} seconds."
        )
        await context.bot.send_message(
            chat_id=GROUP_COORDINATES_ID,
            text=message
        )
        print(f"RetryAfter error in callback_coordinate: {e}")
        total_text_retry = generate_pokemon_messages(90)
        await send_coordinates(context, total_text_retry)
    
# NOTE : Callback coordinate iv 100
async def callback_coordinate_iv_100(context : ContextTypes.DEFAULT_TYPE):
    try:
        total_text = generate_pokemon_messages(100)
        await send_coordinates(context, total_text, 100)
    except telegram.error.RetryAfter as e:
        await asyncio.sleep(e.retry_after)
        message = (
            f"The sending of coordinates has been temporarily paused due to a speed limit."
            f"It will automatically resume in {e.retry_after} seconds."
        )
        await context.bot.send_message(
            chat_id=GROUP_COORDINATES_ID,
            text=message,
        )
        print(f"RetryAfter error in callback_coordinate: {e}")
        total_text_retry = generate_pokemon_messages(100)
        await send_coordinates(context, total_text_retry)
        
# NOTE : Start iv 100
async def start_iv_100(update : Update, context : ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # TODO : Check jika pengguna dibolehkan mengaktifkan perintah.
        if update.effective_user.id not in ALLOWED_USERS:
            await update.message.reply_text(
                "You do not have permission to activate commands."
            )
            return
        
        # TODO : Periksa apakah pesan berasal dari grup koordinat.  
        if update.effective_chat.id != GROUP_COORDINATES_ID:
            await update.message.reply_text(
                "Commands can only be activated in the group @top100galaxy1."
            )
            return
        
        job_iv_90 = context.chat_data.get("callback_coordinate_iv_100")
        
        if job_iv_90:
            await update.message.replay_text(
                "IV 100 coordinates are already being sent. If you want to stop the sending, type /stop"
            )
        else:
            coordinates_list_size = len(fetch_pokemon_data(100))
            waiting_time = 1 + coordinates_waiting_time(coordinates_list_size)
            await update.message.reply_animation(
                f"n {waiting_time:.2f} seconds the coordinates will be sent.."
            )
            job_iv_100 = context.job_queue.run_repeating(
                callback_coordinate_iv_100, interval=PERIOD * 60, first=1
            )
            context.chat_data["callback_coordinate_iv_100"] = job_iv_100
            
    except telegram.error.TelegramError as e:
        print(f"Telegram Error: {e}")
        await update.message.reply_text(
             "An error occurred while executing the /iv100 command. Please report this error to the bot administrator so it can be fixed as soon as possible."
        )
        
    except Exception as e:
        print(f"Error in start: {e}")
        await update.message.reply_text(
            "I'm sorry, an error has occurred with the bot. Please report this error to the bot administrator so that it can be fixed as soon as possible"
        )

async def start_iv_90(update : Update, context : ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # TODO : Periksa apakah pengguna diizinkan untuk mengaktifkan perintah
        if update.effective_user.id not in ALLOWED_USERS:
            await update.message.reply_text(
                "You do not have permission to activate commands"
            )
            return
    
        # TODO : Periksa apakah pesan berasal dari grup koordinat
        if update.effective_chat.id != GROUP_COORDINATES_ID:
            await update.message.reply_text(
                "Commands can only be activated in the group @top100galaxy1."
            )
            return
        
        job_iv_100 = context.chat_data.get("callback_coordinate_iv_100")
        
        if job_iv_100:
            await update.message.reply_text(
                 "IV 100 coordinates are being sent. If you want to send IV 90, type /stop and then /iv90."
            )
            return
        
        job_iv_90 = context.chat_data.get("callback_coordinate_iv_90")
        
        if job_iv_90:
            await update.message.reply_text(
                "IV 90 coordinates are already being sent. If you want to stop the sending, type /stop."
            )
        else:
            coordinates_list_size = len(fetch_pokemon_data(90))
            waiting_time = 1 + coordinates_waiting_time(coordinates_list_size)
            await update.message.reply_text(
                f"Coordinates will be sent in {waiting_time:.2f} seconds..."
            )
            job_iv_90 = context.job_queue.run_repeating(
                callback_coordinate_iv_90, interval=PERIOD
            )
            context.chat_data["callback_coordinate_iv_90"] = job_iv_90
            
    except telegram.error.TelegramError as e:
        print(f"Telegram error: {e}")
        await update.message.reply_text(
            "An error occurred while executing the /iv90 command. Please, report this error to the bot administrator so it can be fixed as soon as possible."
        )
        
    except Exception as e:
        print(f"Error in start: {e}")
        await update.message.reply_text(
            "I'm sorry, an error has occurred with the bot. Please report this error to the bot administrator so that it can be fixed as soon as possible."
        )
        
async def stop(update : Update, context : ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # TODO : Mengecek apakah pengguna diizinkan untuk menggunakan perintah tersebut.
        if update.effective_user.id not in ALLOWED_USERS:
            await update.message.reply_text(
                "You do not have permission to stop the sending of coordinates."
            )
            return
        
        # TODO : Mengecek apakah pesan berasal dari grup koordinat.
        if update.effective_chat.id != GROUP_COORDINATES_ID:
            await update.message.reply_text(
                "Commands can only be activated in the group @top100galaxy1"
            )
            return
        
        job_iv_100 = context.chat_data.get("callback_coordinate_iv_100")
        job_iv_90 = context.chat_data.get("callback_coordinate_iv_90")
        
        if job_iv_100:
            job_iv_100.schedule_removal()
            del context.chat_data["callback_coordinate_iv_100"]
            await update.message.reply_text(
                "The shipment of coordinates IV 100 has been detained."
            )
        elif job_iv_90:
            job_iv_90.schedule_removal()
            del context.chat_data["callback_coordinate_iv_90"]
            await update.message.reply_text(
                "The shipment of coordinates IV 90 has been detained."
            )
        else : 
            await update.message.reply_text(
                "It was not found any active shipment of coordinates."
            )
            
    except telegram.error.TelegramError as e:
        print("Telegram error: {e}")
        await update.message.reply_text(
            "It has occurred an error while executing the /stop command. Please, communicate this error to the bot administrator so it can be fixed as soon as possible."
        )
        
    except Exception as e:
        print("Error on stop : {e}")
        await update.message.reply_text(
            "I'm sorry, an error has occurred with the bot. Please report this error to the bot administrator so that it can be fixed as soon as possible"
        )
        
        
        