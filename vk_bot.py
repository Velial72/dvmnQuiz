import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from time import sleep
import requests.exceptions
import logging

from settings import SetEnv
from get_question import get_question, get_correct_answer, question_exists

logger = logging.getLogger('Logger')


#получаем новый вопрос
def get_new_question(user_id: int, setting):
    question = get_question(json_file_path=setting.json_file_path)
    if not question_exists(user_id=user_id, question=question):
        setting.redis_client.hset(f'user:{user_id}', 'questions', question)
        return question
    question = get_question(json_file_path=setting.json_file_path)
    return question


#получаем ответ
def get_answer(user_id: int, setting, flag=True):
    last_question_list = setting.redis_client.hmget(f"user:{user_id}", "questions")
    last_question = last_question_list[0]
    return get_correct_answer(question=last_question, json_file_path=setting.json_file_path, flag=flag)


#получаем результат
def get_score(user_id: int, setting):
    score, user_give_up = setting.redis_client.hmget(f"user:{user_id}", "score", "give_up")
    return score, user_give_up


def main():
    setting = SetEnv()

    logger.setLevel(logging.WARNING)
    logger.warning("VK_bot запущен")

    vk_token = setting.vk_token
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    while True:
        try:
            longpoll = VkLongPoll(vk_session)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_id = event.user_id
                    message_text = event.text.lower()

                    #Общая клавиатура
                    keyboard_all = VkKeyboard(one_time=True)
                    keyboard_all.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
                    keyboard_all.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
                    keyboard_all.add_line()
                    keyboard_all.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

                    #клавиатура для окна "сдаться/правильный ответ"
                    keyboard_give_up = VkKeyboard(one_time=True)
                    keyboard_give_up.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
                    keyboard_give_up.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

                    #клавиатура для окна "счет"
                    keyboard_score = VkKeyboard(one_time=True)
                    keyboard_score.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)

                    if not setting.redis_client.hexists(f"user:{user_id}", "questions"):
                        setting.redis_client.hset(f"user:{user_id}",
                                                  mapping={"questions": "", "score": 0, "give_up": 0})
                        vk_api.messages.send(
                            user_id=user_id,
                            random_id=get_random_id(),
                            message='Привет! Я твой новый бот. Отвечай на вопросы! Чем больше ответов, тем выше шанс '
                                    'победить!\nТы всегда можешь сдаться и повторить через годик.',
                            keyboard=keyboard_all.get_keyboard(),
                        )

                    if message_text == "новый вопрос":
                        vk_api.messages.send(
                            user_id=user_id,
                            random_id=get_random_id(),
                            message=f'{get_new_question(user_id=user_id, setting=setting)}',
                            keyboard=keyboard_all.get_keyboard(),
                        )

                    elif message_text == "сдаться":
                        setting.redis_client.hincrby(f"user:{user_id}", "give_up", 1)
                        vk_api.messages.send(
                            user_id=user_id,
                            random_id=get_random_id(),
                            message=f'Вот тебе правильный ответ: {get_answer(user_id=user_id, setting=setting, flag=False)}\nЧтобы продолжить '
                                    f'нажми "новый вопрос"',
                            keyboard=keyboard_give_up.get_keyboard(),
                        )

                    elif message_text == "мой счет":
                        user_score, give_up = get_score(user_id=user_id, setting=setting)
                        vk_api.messages.send(
                            user_id=user_id,
                            random_id=get_random_id(),
                            message=f'Правильных ответов: {user_score}\nПропущено: {give_up}',
                            keyboard=keyboard_score.get_keyboard(),
                        )

                    elif message_text == get_answer(user_id=user_id, setting=setting, flag=True):
                        setting.redis_client.hincrby(f"user:{user_id}", "score", 1)
                        vk_api.messages.send(
                            user_id=user_id,
                            random_id=get_random_id(),
                            message='Правильно!.\nЧтобы продолжить нажми "новый вопрос"',
                            keyboard=keyboard_give_up.get_keyboard(),
                        )

                    else:
                        vk_api.messages.send(
                            user_id=user_id,
                            random_id=get_random_id(),
                            message='Не верный ответ или команда',
                            keyboard=keyboard_all.get_keyboard(),
                        )

        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            logging.exception("VK_bot упал с ошибкой")
            sleep(120)


if __name__ == '__main__':
    main()
