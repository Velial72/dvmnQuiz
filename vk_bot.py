import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from environs import Env

from redis_client import redis_client
from get_question import get_question, get_correct_answer, question_exists


#добавляем пользователя в базу
def create_user(user_id: int):
    redis_client.hset(f"user:{user_id}", mapping={"questions": "", "score": 0, "give_up": 0})
    print('ok')


#получаем новый вопрос
def get_new_question(user_id: int):
    while True:
        question = get_question()
        if not question_exists(user_id=user_id, question=question):
            redis_client.hset(f'user:{user_id}', 'questions', question)
            return question


#получаем ответ
def get_answer(user_id: int, flag=True):
    last_question_list = redis_client.hmget(f"user:{user_id}", "questions")
    last_question = last_question_list[0]
    return get_correct_answer(question=last_question, flag=flag)


#получаем результат
def get_score(user_id: int):
    score, user_give_up = redis_client.hmget(f"user:{user_id}", "score", "give_up")
    return score, user_give_up


def main():
    env = Env()
    env.read_env()

    vk_token = env('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message_text = event.text.lower()
            print(message_text)

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

            if not redis_client.hexists(f"user:{user_id}", "questions"):
                create_user(user_id=user_id)
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
                    message=f'{get_new_question(user_id=user_id)}',
                    keyboard=keyboard_all.get_keyboard(),
                )

            elif message_text == "сдаться":
                redis_client.hincrby(f"user:{user_id}", "give_up", 1)
                vk_api.messages.send(
                    user_id=user_id,
                    random_id=get_random_id(),
                    message=f'Вот тебе правильный ответ: {get_answer(user_id=user_id, flag=False)}\nЧтобы продолжить '
                            f'нажми "новый вопрос"',
                    keyboard=keyboard_give_up.get_keyboard(),
                )

            elif message_text == "мой счет":
                user_score, give_up = get_score(user_id=user_id)
                vk_api.messages.send(
                    user_id=user_id,
                    random_id=get_random_id(),
                    message=f'Правильных ответов: {user_score}\nПропущено: {give_up}',
                    keyboard=keyboard_score.get_keyboard(),
                )

            elif message_text == get_answer(user_id=user_id, flag=True):
                redis_client.hincrby(f"user:{user_id}", "score", 1)
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


if __name__ == '__main__':
    main()
