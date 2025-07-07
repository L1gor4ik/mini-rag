"""Download Rust FAQ, extract Q/A pairs and save as CSV."""

import csv, requests

from bs4 import BeautifulSoup

from pathlib import Path



URL = "https://doc.rust-lang.org/faq.html"

out = Path("data/rust_faq.csv")

out.parent.mkdir(exist_ok=True)



def main():

    html = requests.get(URL, timeout=30).text

    soup = BeautifulSoup(html, "html.parser")

    rows = []

    for i, q in enumerate(soup.select("section ul li a[href^='#']"), 1):

        anchor = q["href"].lstrip("#")

        ans = soup.find(id=anchor).find_next("p").get_text(strip=True)

        rows.append({"id": i, "question": q.get_text(strip=True), "answer": ans})



    with out.open("w", newline="", encoding="utf-8") as f:

        w = csv.DictWriter(f, fieldnames=rows[0].keys())

        w.writeheader()

        w.writerows(rows)

    print(f"Saved {len(rows)} Q/A -> {out}")



if __name__ == "__main__":

    main()

