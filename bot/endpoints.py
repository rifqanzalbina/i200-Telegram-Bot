from fastapi import APIRouter, Request, Response
from telegram import Update
from bot.ptb import ptb
from http import HTTPStatus
from settings import config

router = APIRouter()

@router.get("/")
def home():
    return "Hello, welcome to adventure elements"

if config.DEBUG == "False":
    @router.get("/")
    def bot():
        return "Bot is running"

    @router.post("/")
    async def process_update(request : Request):
        req = await request.json()
        update = Update.de_json(req, ptb.bot)