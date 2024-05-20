import os
from pathlib import Path
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User, CallbackQuery, Message, ContentType
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.media import StaticMedia
from time import sleep

from settings import SetEnv
from get_question import get_question, get_correct_answer, question_exists


base_dir = Path(__file__).resolve().parent
setting = SetEnv()

class QuizSG(StatesGroup):
    start = State()
    question = State()
    mistake = State()
    give_up = State()
    score = State()
    score_back = State()


#геттеры
#получаем имя пользователя
async def get_name(event_from_user: User, **kwargs):
    return {'name': event_from_user.username or 'Путник', "extended": True}


#получаем новый вопрос из файла
async def get_new_question(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    question = get_question(json_file_path=setting.json_file_path)
    if not question_exists(user_id=event_from_user.id, question=question):
        setting.redis_client.hset(f"user:{event_from_user.id}", "questions", question)
        return {'question': question}
    question = get_question(json_file_path=setting.json_file_path)
    return {'question': question}

#получаем результат пользователя из базы
async def get_score(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    score, user_give_up = setting.redis_client.hmget(f"user:{event_from_user.id}", "score", "give_up")
    return {'good_answer': score, 'user_give_up': user_give_up}


#получаем правильный ответ
async def get_answer(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    last_question_list = setting.redis_client.hmget(f"user:{event_from_user.id}", "questions")
    last_question = last_question_list[0]
    correct_answer = get_correct_answer(question=last_question, json_file_path=setting.json_file_path, flag=False)
    setting.redis_client.hincrby(f"user:{event_from_user.id}", "give_up", 1)
    return {'correct_answer': correct_answer}


#получаем старый вопрос из базы
async def repeat_question(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    last_question_list = setting.redis_client.hmget(f"user:{event_from_user.id}", "questions")
    last_question = last_question_list[0]
    return {'re_question': last_question}


#хендлеры
#переходим в окно нового вопроса
async def send_question(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=QuizSG.question)


#проверяем введенный ответ с правильным из файла
async def correct_user_answer(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    last_question_list = setting.redis_client.hmget(f"user:{message.chat.id}", "questions")
    last_question = last_question_list[0]
    if message.text == get_correct_answer(question=last_question, json_file_path=setting.json_file_path, flag=True):
        await message.answer(text=f'Это правильный ответ!')
        setting.redis_client.hincrby(f"user:{message.chat.id}", "score", 1)
        sleep(1)
        await dialog_manager.switch_to(state=QuizSG.question)
    else:
        await message.answer(text=f'Ты ошибся! Попробуй снова')
        await dialog_manager.switch_to(state=QuizSG.mistake)


#переходим в счет пользователя
async def go_to_score(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=QuizSG.score)


#переходим в счет пользователя
async def go_to_score_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=QuizSG.score_back)


#возвращаемся в окно ошибки
async def back_to_question(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(QuizSG.mistake)


#возвращаемся к вопросу
async def back_button(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


#переходим в окно "сдаться"
async def give_up(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=QuizSG.give_up)


start_dialog = Dialog(
    Window(
        Format('{name}, что тебя интересует?'),
        Row(
            Button(
                text=Const('Новый вопрос'),
                id='new_question',
                on_click=send_question,
            ),
            Button(
                text=Const('Сдаться'),
                id='kill',
                on_click=give_up,
                when=F["extended"],
            ),
        ),
        Button(
            text=Const('Мой счет'),
            id='score',
            on_click=go_to_score,
        ),
        getter=get_name,
        state=QuizSG.start,

    ),
    Window(
        Format('Вопрос: {question}'),
        TextInput(
            id='user_answer',
            on_success=correct_user_answer,
        ),
        Row(
            Button(
                text=Const('Сдаться'),
                id='kill',
                on_click=give_up,
            ),
            Button(
                text=Const('Мой счет'),
                id='score',
                on_click=go_to_score_back,
            ),
        ),
        getter=get_new_question,
        state=QuizSG.question,
    ),
    Window(
        Format('Вопрос: {re_question}'),
        TextInput(
            id='user_answer',
            on_success=correct_user_answer,
        ),
        Row(
            Button(
                text=Const('Сдаться'),
                id='kill',
                on_click=give_up,
            ),
            Button(
                text=Const('Мой счет'),
                id='score',
                on_click=go_to_score_back,
            ),
        ),
        getter=repeat_question,
        state=QuizSG.mistake,
    ),
    Window(
        StaticMedia(
            path=os.path.join(base_dir / "media", 'sad.jpg'),
            type=ContentType.PHOTO
        ),
        Format('Вот тебе правильный ответ: {correct_answer}'),
        Row(
            Button(
                text=Const('Новый вопрос'),
                id='new_question',
                on_click=send_question,
            ),
            Button(
                text=Const('Мой счет'),
                id='score',
                on_click=go_to_score,
            ),
        ),
        getter=get_answer,
        state=QuizSG.give_up
    ),
    Window(
        Format('Твой счет:\nПравильных ответов: {good_answer}\nПропущено: {user_give_up}'),
        Button(
            text=Const('Назад'),
            id='back',
            on_click=back_button,
        ),
        getter=get_score,
        state=QuizSG.score
    ),
    Window(
        Format('Твой счет:\nПравильных ответов: {good_answer}\nПропущено: {user_give_up}'),
        Button(
            text=Const('Назад'),
            id='back_to_question',
            on_click=back_to_question,
        ),
        getter=get_score,
        state=QuizSG.score_back
    )
)

