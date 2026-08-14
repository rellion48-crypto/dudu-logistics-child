import os, json, re, urllib.request
from pathlib import Path
import gradio as gr
from settings import TOP_K, MIN_SCORE, USE_GEMINI

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

FAQ_PATH = Path(__file__).with_name("faq.json")
SYNONYMS = {"늦어서": {"배송", "지연"}, "돌려받고": {"환불"}, "환불": {"환불"}, "취소": {"환불"}}

def tokens(text):
    base = set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))
    for word, extra in SYNONYMS.items():
        if word in text:
            base |= extra
    return base

def search(question):
    q = tokens(question)
    faqs = json.loads(FAQ_PATH.read_text(encoding="utf-8"))
    ranked = []
    for faq in faqs:
        score = len(q & tokens(faq["title"] + " " + faq["text"]))
        ranked.append((score, faq))
    ranked.sort(key=lambda x: (-x[0], x[1]["title"]))
    return [x for x in ranked if x[0] >= MIN_SCORE][:TOP_K]

def ask_gemini(question, faq_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({
        "contents": [{"parts": [{"text":
            f"다음 FAQ 근거만 사용해서 질문에 자연스럽게 답하세요.\n\n근거:\n{faq_text}\n\n질문: {question}"
        }]}]
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"]

def chat(message, history):
    hits = search(message)
    if not hits:
        return f"검색 근거 없음 (TOP_K={TOP_K}, MIN_SCORE={MIN_SCORE})"

    faq_text = "\n".join(f"- {faq['title']}: {faq['text']}" for _, faq in hits)

    if USE_GEMINI and GEMINI_API_KEY:
        try:
            answer = ask_gemini(message, faq_text)
            mode = "Gemini"
        except Exception as e:
            answer = f"Gemini 오류: {e}"
            mode = "오류"
    else:
        lines = []
        for i, (score, faq) in enumerate(hits):
            lines.append(f"[{i+1}] {faq['title']} (score: {score})\n{faq['text']}")
        answer = "\n\n".join(lines)
        mode = "규칙"

    source = ", ".join(faq["title"] for _, faq in hits)
    return f"{answer}\n\n출처: {source}\nTOP_K={TOP_K}, MIN_SCORE={MIN_SCORE}\n생성 방식: {mode}"

demo = gr.ChatInterface(
    fn=chat, title="LAB 4 · Complete RAG",
    description="Retrieval + Generation을 합쳐서 최적 조합을 찾습니다.",
    examples=["이미 출발했는데 환불되나요?", "배송 카드 취소"]
)
if __name__ == "__main__":
    demo.launch()
