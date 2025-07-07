import csv, time, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()                                 # грузим .env

API_KEY = os.getenv("OPENAI_API_KEY")
USE_LLM = bool(API_KEY)                       # True если ключ задан

if USE_LLM:
    from openai import OpenAI
    from openai.types import CompletionUsage as Usage
    openai = OpenAI(api_key=API_KEY)
else:
    # Заглушки вместо настоящих классов OpenAI
    class Usage:                               # минимальный «псевдотип»
        prompt_tokens = completion_tokens = total_tokens = 0
    openai = None




PRICES = {

    "prompt": 5.0 / 1000,

    "completion": 15.0 / 1000,

}



LOG = Path("cost_log.csv")  # путь к файлу лога

def _write(row: dict):

    write_header = not LOG.exists()

    with LOG.open("a", newline="", encoding="utf-8") as f:

        w = csv.DictWriter(f, fieldnames=row.keys())

        if write_header:

            w.writeheader()

        w.writerow(row)



def tracked_chat(prompt: str, model="gpt-3.5-turbo") -> str:
    if not USE_LLM:
        # Вернём первые 200 символов контекста как «ответ»
        return prompt.split("Вопрос:")[-1][:200] + " ..."

    # ↓ обычный код, если ключ задан
    t0 = time.time()
    resp = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    ...


    usage: Usage = resp.usage

    cost = usage.prompt_tokens * PRICES["prompt"] + usage.completion_tokens * PRICES["completion"]

    _write({"ts": t0, "model": model, **usage.model_dump(), "usd": cost})

    return resp.choices[0].message.content.strip()

