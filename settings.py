import os
from pathlib import Path
from environs import Env
import redis

base_dir = Path(__file__).resolve().parent


class SetEnv:
    def __init__(self) -> None:
        env = Env()
        env.read_env()

        self.redis_client = redis.StrictRedis(
            host=env.str('REDIS_HOST'),
            port=env.str('REDIS_PORT'),
            password=env.str('REDIS_PASSWORD'),
            decode_responses=True
        )

        self.tg_token = env.str('BOT_TOKEN')
        self.vk_token = env.str('VK_TOKEN')
        self.folder_path = env.str('QUESTION_PATH', default=os.path.join(base_dir / 'quiz-questions'))
        self.json_file_path = env.str('JSON_PATH',
                                      default=os.path.join(base_dir / 'quiz-questions/questions_and_answers.json'))
