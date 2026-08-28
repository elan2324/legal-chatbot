import json
import re
from pathlib import Path

import random_responses
from config.settings import Config


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        print(f"Loaded '{path.name}' successfully!")
        return json.load(f)


response_data = load_json(Config.BOT_DATA_PATH)


def get_response(input_string):
    input_string = (input_string or "").strip()

    if not input_string:
        return "Please type something so we can chat."

    split_message = re.split(r"\s+|[,;?!.-]\s*", input_string.lower())
    score_list = []

    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response.get("required_words", [])

        for word in split_message:
            if word in required_words:
                required_score += 1

        if required_score == len(required_words):
            for word in split_message:
                if word in response.get("user_input", []):
                    response_score += 1

        score_list.append(response_score)

    best_response = max(score_list, default=0)

    if best_response > 0:
        return response_data[score_list.index(best_response)]["bot_response"]

    return random_responses.random_string()