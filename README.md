# 🎯 Mini-RAG (offline demo)

Мини-репо, показывающее, как собрать Retrieval-Augmented-Generation **без** внешних сервисов.
> 🔒 Модель OpenAI отключена заглушкой — никаких секретов, запускается офлайн.

## Установка
```bash
git clone https://github.com/<user>/mini-rag.git
cd mini-rag
python -m venv venv && . venv/Scripts/activate      # Win
pip install -r requirements.txt
pytest -q      # 10 тестов на BERTScore (офлайн)
