import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
_client = None

SYSTEM_PROMPT = (
    "You summarize news articles. Reply with a concise summary of about 3 sentences "
    "in plain English. No preamble, no bullet points. Use only facts from the article."
)


def _get_client():
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to .env")
        _client = Groq(api_key=key)
    return _client


def summarize_groq(text, max_tokens=200):
    response = _get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.2,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    sample = (
        "The government announced a new policy on Monday that will change how "
        "students apply for scholarships. Officials said the online portal will "
        "open next month and will reduce paperwork for applicants."
    )
    print(summarize_groq(sample))