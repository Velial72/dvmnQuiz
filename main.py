import os
import re


folder_path = 'quiz-questions'
files = os.listdir(folder_path)

qa_dict = {}

for file_name in files:
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'r', encoding='KOI8-R') as file:
        questions_list = file.read()

        questions_and_answers = re.findall(r'Вопрос \d+:(.*?)Ответ:(.*?)\n\n', questions_list, re.DOTALL)

        for question, answer in questions_and_answers:
            if not re.search(r'\bhttp[s]?:\/\/\S+\.(?:png|jpg|jpeg|gif)\b', question):
                qa_dict[question.strip()] = answer.strip()

for question, answer in qa_dict.items():
    print("Вопрос:", question)
    print("Ответ:", answer)
    print()