import os
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from environs import Env

from dialog import QuizSG, start_dialog
from redis_client import redis_client


#отправляет картинку на старте
async def message_send_photo(message, image):
    file_path = os.path.join(BASE_DIR / "media", f'{image}')
    photo = FSInputFile(path=file_path, filename=f'{image}')
    await bot.send_photo(chat_id=message.chat.id, photo=photo)

#создание пользователя с начальными данными
async def create_user(user_id: int):
    redis_client.hset(f"user:{user_id}", mapping={"questions": "", "score": 0, "give_up": 0})


BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env()

bot_token = env('BOT_TOKEN')


bot = Bot(token=bot_token)
dp = Dispatcher()


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message, dialog_manager: DialogManager):
    await message.answer('Привет!\nЯ проведу викторину')
    await create_user(user_id=message.chat.id)
    await message_send_photo(message, 'test.jpg')
    await dialog_manager.start(state=QuizSG.start, mode=StartMode.RESET_STACK)


@dp.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(
        'Отвечай на вопросы! Чем больше ответов, тем выше шанс победить!\n\nТы всегда можешь сдаться и повторить через годик.'
    )


if __name__ == '__main__':
    dp.include_router(start_dialog)
    setup_dialogs(dp)
    dp.run_polling(bot)