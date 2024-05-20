import json
import random

from settings import SetEnv

setting = SetEnv()


#получаем случайный вопрос из json файла
def get_question(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        qa_dict = json.load(json_file)

    random_key = random.choice(list(qa_dict.keys()))
    random_value = qa_dict[random_key]

    return random_key


# Получение ответа по ключу (вопросу)
def get_correct_answer(question: str, json_file_path, flag=True):
    with open(json_file_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    answer = data[question].lower()
    if flag:
        if '(' in answer:
            short_answer = answer.split(' (')[0]
        elif '.' in answer:
            short_answer = answer.split('.')[0]
            if short_answer.endswith('.'):
                short_answer = short_answer[:-1]
        else:
            short_answer = answer
        if short_answer.startswith('"') and short_answer.endswith('"'):
            short_answer = short_answer[1:-1]
        return short_answer
    return answer


#проверяем был ли вопрос
def question_exists(user_id: int, question: str) -> bool:
    existing_question = setting.redis_client.hget(f"user:{user_id}", "questions")
    return existing_question == question
