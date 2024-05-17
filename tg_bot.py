import os
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from environs import Env
from time import sleep
import requests.exceptions
import logging

from dialog import QuizSG, start_dialog
from redis_client import redis_client


#создание пользователя с начальными данными
async def create_user(user_id: int):
    redis_client.hset(f"user:{user_id}", mapping={"questions": "", "score": 0, "give_up": 0})


BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger('Logger')


def main():
    env = Env()
    env.read_env()

    bot_token = env('BOT_TOKEN')
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    logger.setLevel(logging.WARNING)
    logger.warning("TG_bot запущен")
    

    @dp.message(Command(commands=["start"]))
    async def process_start_command(message: Message, dialog_manager: DialogManager):
        await message.answer('Привет!\nЯ проведу викторину')
        await create_user(user_id=message.chat.id)
        file_path = os.path.join(BASE_DIR / "media", 'test.jpg')
        photo = FSInputFile(path=file_path, filename='test.jpg')
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        await dialog_manager.start(state=QuizSG.start, mode=StartMode.RESET_STACK)

    @dp.message(Command(commands=['help']))
    async def process_help_command(message: Message):
        await message.answer(
            'Отвечай на вопросы! Чем больше ответов, тем выше шанс победить!\n\nТы всегда можешь сдаться и повторить '
            'через годик.'
        )
    while True:
        try:
            dp.include_router(start_dialog)
            setup_dialogs(dp)
            dp.run_polling(bot)
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            logging.exception("TG_bot упал с ошибкой")
            sleep(120)

if __name__ == '__main__':
    main()
