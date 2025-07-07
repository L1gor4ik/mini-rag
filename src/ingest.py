"""
Скачивает FAQ Rust (рус/англ) из живого источника и сохраняет data/rust_faq.csv
Если все URL недоступны — останавливается с понятным RuntimeError.
"""
import csv, requests, sys
from pathlib import Path
from bs4 import BeautifulSoup

# ────────────────────────────────────────────────────────────────────────────────
URLS = [
    # 1) FAQ-Markdown в книге Rust ― main raw URL
    "https://raw.githubusercontent.com/rust-lang/book/main/src/appendix-07-faq.md",   # 200 OK

    # 2) Html-страница той же книги (если raw-домен вдруг режется)
    "https://rust-lang.github.io/book/appendix-07-faq.html",                         # 200 OK

    # 3) Старая learn/faq (иногда 404, но пусть будет запас)
    "https://www.rust-lang.org/learn/faq/",                                          # 301→200 OK

    # 4) /faq/ со слэшем — CDN отдаёт 200 (без слэша даёт 422)
    "https://www.rust-lang.org/faq/",                                                # 200 OK
]



HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; mini-rag/0.1)"}
TIMEOUT  = 30

OUT = Path("data/rust_faq.csv")
OUT.parent.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────────────────────
def fetch_first_alive(urls):
    """Вернуть (url, BeautifulSoup) первой реально открывшейся страницы"""
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if resp.ok:
                print(f"✅  Беру FAQ отсюда: {url}")
                return url, BeautifulSoup(resp.text, "html.parser")
            print(f"⚠️  {url} → HTTP {resp.status_code}")
        except requests.RequestException as e:
            print(f"⚠️  {url} → {e.__class__.__name__}")
    raise RuntimeError(
        "Ни один из FAQ-URL не открылся. "
        "Проверьте интернет / корпоративный прокси."
    )

# ────────────────────────────────────────────────────────────────────────────────
def parse_rows(url, soup):
    """Вернуть список словарей id/question/answer под конкретную разметку"""
    rows = []

    if "/learn/faq" in url:                       # <details><summary> … </details>
        for i, det in enumerate(soup.select("details"), 1):
            summary = det.find("summary")
            if not summary:
                continue
            q = summary.get_text(" ", strip=True)
            a = det.get_text(" ", strip=True).replace(q, "", 1).strip()
            rows.append({"id": i, "question": q, "answer": a})

    elif url.rstrip("/").endswith("/faq"):        # <dl class="faq"><dt>/<dd>
        for i, dt in enumerate(soup.select("dl.faq dt"), 1):
            dd = dt.find_next_sibling("dd")
            if not dd:
                continue
            rows.append({
                "id": i,
                "question": dt.get_text(" ", strip=True),
                "answer":   dd.get_text(" ", strip=True)
            })

    elif url.endswith("faq.md") or url.endswith("faq.html"):
        # Для .md берём чистый текст, для .html сначала вытащим текст из <body>
        text_block = soup.get_text(" ", strip=True)
        import re
        sections = re.split(r"###\\s+", text_block)   # в Markdown/HTML FAQ каждый Q начинается с ### Вопрос
        for i, chunk in enumerate(sections[1:], 1):   # [0] — вводный текст до первого ###
            q, *a = chunk.splitlines()
            rows.append({
                "id": i,
                "question": q.strip(),
                "answer":   "\n".join(a).strip(),
            })

    if not rows:
        raise RuntimeError(
            "Парсер не нашёл ни одного вопроса: "
            "вероятно снова изменилась структура HTML."
        )
    return rows

# ────────────────────────────────────────────────────────────────────────────────
def main():
    url, soup = fetch_first_alive(URLS)
    rows      = parse_rows(url, soup)
    print("Найдено вопросов:", len(rows))

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"💾  Сохранено в {OUT}")

# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit(f"🛑  {e}")
