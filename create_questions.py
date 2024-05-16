import os
from pathlib import Path
import re
import json
from environs import Env


def clean_text(text):
    text = re.sub(r'[\n\\]+', ' ', text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def main():
    env = Env()
    env.read_env()

    BASE_DIR = Path(__file__).resolve().parent

    folder_path = env.str('QUESTION_PATH', default=os.path.join(BASE_DIR / 'quiz-questions'))
    files = os.listdir(folder_path)
    json_file_path = env.str('JSON_PATH', default=os.path.join(BASE_DIR / 'quiz-questions/questions_and_answers.json'))

    qa_dict = {}

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r', encoding='KOI8-R') as file:
            questions_list = file.read()

            questions_and_answers = re.findall(r'Вопрос \d+:(.*?)Ответ:(.*?)\n\n', questions_list, re.DOTALL)

            for question, answer in questions_and_answers:
                if not re.search(r'\bhttp[s]?:\/\/\S+\.(?:png|jpg|jpeg|gif)\b', question):
                    question = clean_text(question)
                    answer = clean_text(answer)
                    qa_dict[question.strip()] = answer.strip()

    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(qa_dict, json_file, ensure_ascii=False, indent=4)

    print("Данные успешно записаны в JSON файл.")


if __name__ == '__main__':
    main()
