import pandas as pd, pytest

from bert_score import score

from rag_pipeline import answer



df = pd.read_csv("data/rust_faq.csv").sample(10, random_state=42)



@pytest.mark.parametrize("q,a", df[["question", "answer"]].values.tolist())

def test_rag(q, a):

    pred = answer(q)

    P, R, F1 = score([pred], [a], lang="ru")

    assert F1.item() > 0.60, f"F1={F1.item():.2f} < 0.60"

