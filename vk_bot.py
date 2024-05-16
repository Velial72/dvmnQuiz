import random

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from environs import Env




# def send_answer(answer, user_id, vk_api):
#     vk_api.messages.send(
#         user_id=user_id,
#         message=answer,
#         random_id=random.randint(1,1000)
#     )


def main():
    env = Env()
    env.read_env()
    vk_token = 'vk1.a.9Z4GpQAwHGD_c9OmM5aFrtfhodlQyGIi3k8PfgYcwcQvo2L7hQUAX-VFKbJ5U6N9vWcCD_uCYg8Egz41Xscup7tdbEUXdEfg9BBH1SJMbJv_bdVw6A6LdJXRmC1tkNwfSNdNXFqN6L1FymZTOMjp6CRGquJTbUWH9zYWhEF48MNltuBsgEIcU5zjZfwOnpYVNwX3wUsAKCqLAAoh3rYAkw'
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message_text = event.text.lower()

            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_line()
            keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

            # vk_api.messages.send(
            #     user_id=user_id,
            #     random_id=get_random_id(),
            #     message='Пример клавиатуры',
            #     keyboard=keyboard.get_keyboard(),
            # )

            # if message_text == "привет":
            #     vk_api.messages.send(
            #     user_id=user_id,
            #     random_id=get_random_id(),
            #     message='Привет! Как я могу помочь?',
            #     keyboard=keyboard.get_keyboard(),
            # )

            if message_text == "новый вопрос":
                vk_api.messages.send(
                user_id=user_id,
                random_id=get_random_id(),
                message='Вот ваш новый вопрос...',
                keyboard=keyboard.get_keyboard(),
            )
            elif message_text == "сдаться":
                vk_api.messages.send(
                user_id=user_id,
                random_id=get_random_id(),
                message='Не сдавайтесь! Попробуйте еще раз.',
                keyboard=keyboard.get_keyboard(),
            )

            elif message_text == "мой счет":
                vk_api.messages.send(
                user_id=user_id,
                random_id=get_random_id(),
                message='Ваш счет: 0',
                keyboard=keyboard.get_keyboard(),
            )

            else:
                vk_api.messages.send(
                user_id=user_id,
                random_id=get_random_id(),
                message='Не понял ваш запрос. Пожалуйста, используйте кнопки.',
                keyboard=keyboard.get_keyboard(),
            )


if __name__ == '__main__':
    main()