import csv, time

from pathlib import Path

from openai import OpenAI, Usage



LOG = Path("logs/usage.csv")

LOG.parent.mkdir(exist_ok=True)

openai = OpenAI()



PRICES = {

    "prompt": 5.0 / 1000,

    "completion": 15.0 / 1000,

}



def _write(row: dict):

    write_header = not LOG.exists()

    with LOG.open("a", newline="", encoding="utf-8") as f:

        w = csv.DictWriter(f, fieldnames=row.keys())

        if write_header:

            w.writeheader()

        w.writerow(row)



def tracked_chat(prompt: str, model="gpt-4o-mini") -> str:

    t0 = time.time()

    resp = openai.chat.completions.create(

        model=model,

        messages=[{"role": "user", "content": prompt}]

    )

    usage: Usage = resp.usage

    cost = usage.prompt_tokens * PRICES["prompt"] + usage.completion_tokens * PRICES["completion"]

    _write({"ts": t0, "model": model, **usage.model_dump(), "usd": cost})

    return resp.choices[0].message.content.strip()

