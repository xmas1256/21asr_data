from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from data.config import ADMINS

from loader import dp, bot
from ..sqlite import SQLighter

from aiogram.dispatcher.filters import Command
from aiogram.types import InputFile


db = SQLighter('/home/buxgalt1/public_html/app/db.sqlite3')



@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.full_name, message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)
    for admin in ADMINS:
        try:
            await dp.bot.forward_message(admin, message.chat.id, message.message_id)
            
        except Exception as err:
            logging.exception(err)
    photo_url = "AgACAgIAAxkBAAPqYl06gc0OntU9TDwjMZ76ZvmS-Z8AArO4MRtWBOhKlTddfVv4DEwBAAMCAAN5AAMkBA"
    await message.reply_photo(photo_url, caption="Assalomu aleykum xurmatli mijoz! Siz XXI ASR XIZMATLARI MARKAZI RASMIY BOTIGA TASHRIF BUYURDINGIZ! Murojaatingizni shu yerda yozib qoldiring! Tez orada javob qaytaramiz! \nOfis ma'lumotlar uchun :+998557012100\nMenedjer Sultonmurod +998992231112\nAvtoraqam:                         + 998992231118\nKadastr xizmatlari:            +998992231115\nKompyuter xizmatlari:     +998901962266\nTelegram manzil: @asr21bot\nBizning Manzillar: <a href='https://www.google.com/maps/place/21-ASR+Buxgalteriya+xizmatlari/@39.4178555,67.2393289,288m/data=!3m1!1e3!4m5!3m4!1s0x0:0x396e65b95616bf89!8m2!3d39.4176281!4d67.2395654'>1-ofis: Urgut Soliq inspeksiyasi ro'parasida</a>\n2-Ofis: Kompyuter xizmatlari Iqtisod kolleji kirish qismida!\n<a href='https://www.google.com/maps/place/XXI-ASR+BUXGALTERIYA/@39.4284763,67.2381326,604m/data=!3m1!1e3!4m12!1m6!3m5!1s0x0:0x396e65b95616bf89!2s21-ASR+Buxgalteriya+xizmatlari!8m2!3d39.4176281!4d67.2395654!3m4!1s0x0:0x73c169c913177a83!8m2!3d39.4287011!4d67.2387442'>3-Ofis: Urgut Davlat xizmatlari markazi ro'parasida </a>")


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def media_photo(message: types.Message):
 
    for admin in ADMINS:
        try:
            await dp.bot.forward_message(admin, message.chat.id, message.message_id)
            
        except Exception as err:
            logging.exception(err)
            
            
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def media_video(message: types.Message):

    for admin in ADMINS:
        try:
            await dp.bot.forward_message(admin, message.chat.id, message.message_id)
            
        except Exception as err:
            logging.exception(err)
            
            
@dp.message_handler(content_types=types.ContentType.AUDIO)
async def media_audio(message: types.Message):

    for admin in ADMINS:
        try:
            await dp.bot.forward_message(admin, message.chat.id, message.message_id)
            
        except Exception as err:
            logging.exception(err)
            
            
@dp.message_handler(content_types=types.ContentType.VOICE)
async def media_voice(message: types.Message):

    for admin in ADMINS:
        try:
            await dp.bot.forward_message(admin, message.chat.id, message.message_id)
            
        except Exception as err:
            logging.exception(err)
            
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def media_document(message: types.Message):

    for admin in ADMINS:
        try:
            await dp.bot.forward_message(admin, message.chat.id, message.message_id)
            
        except Exception as err:
            logging.exception(err)
            
    