from aiogram import types

from loader import dp
from data.config import ADMINS


            


# Echo bot
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    for admin in ADMINS:
        if int(admin) == int(message.from_user.id):
            if message.reply_to_message:
                await dp.bot.send_message(message.reply_to_message.forward_from.id, f"{message.text}")
            else:
                try:
                    await dp.bot.send_message(admin, f"{message.text}")
                except Exception as err:
                    logging.exception(err)
        else:
            try:
                await dp.bot.forward_message(admin, message.chat.id, message.message_id)
            except:
                logging.exception(err)
            
                
            
