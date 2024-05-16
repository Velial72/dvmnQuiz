import os
import json
import random
from pathlib import Path

from redis_client import redis_client


BASE_DIR = Path(__file__).resolve().parent.parent
json_file_path = os.path.join(BASE_DIR / 'quiz-questions/questions_and_answers.json')

#получаем случайный вопрос из json файла
def get_question():
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        qa_dict = json.load(json_file)

    random_key = random.choice(list(qa_dict.keys()))
    random_value = qa_dict[random_key]

    print("Ответ на вопрос:", random_value)
    return random_key, random_value

# Получение ответа по ключу (вопросу)
def get_correct_answer(question: str, flag = True):
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
        print(short_answer)
        return short_answer
    else:
        return answer

#добавляем вопрос в базу
def add_question_to_user(user_id: int, question: str):
    redis_client.hset(f"user:{user_id}", "questions", question)

#проверяем был ли вопрос
def question_exists(user_id: int, question: str) -> bool:
    existing_question = redis_client.hget(f"user:{user_id}", "questions")
    return existing_question == question