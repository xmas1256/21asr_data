from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InputFile

from loader import dp, bot

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def media_photo(message: types.Message):
    await message.reply_photo(message.photo[-1].file_id)