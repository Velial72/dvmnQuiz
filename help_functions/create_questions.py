import os
from pathlib import Path
import re
import json


BASE_DIR = Path(__file__).resolve().parent.parent

folder_path = os.path.join(BASE_DIR / 'quiz-questions')
files = os.listdir(folder_path)
json_file_path = os.path.join(BASE_DIR / 'quiz-questions/questions_and_answers.json')

qa_dict = {}


# def capitalize_first_letter(string):
#     if string and string[0].isalpha():
#         return string[0].upper() + string[1:]
#     else:
#         return string

def clean_text(text):
    #удаляем символы перевода строки, обратные косые черты и лишние пробелы
    text = re.sub(r'[\n\\]+', ' ', text).strip()
    #удаляем лишние пробелы между словами
    text = re.sub(r'\s+', ' ', text)
    return text


for file_name in files:
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'r', encoding='KOI8-R') as file:
        questions_list = file.read()

        questions_and_answers = re.findall(r'Вопрос \d+:(.*?)Ответ:(.*?)\n\n', questions_list, re.DOTALL)

        for question, answer in questions_and_answers:
            if not re.search(r'\bhttp[s]?:\/\/\S+\.(?:png|jpg|jpeg|gif)\b', question):
                # capitalize_first_letter(question)
                # capitalize_first_letter(answer)
                question = clean_text(question)
                answer = clean_text(answer)
                qa_dict[question.strip()] = answer.strip()


with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(qa_dict, json_file, ensure_ascii=False, indent=4)

print("Данные успешно записаны в JSON файл.")
