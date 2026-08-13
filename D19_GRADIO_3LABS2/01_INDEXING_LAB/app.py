import json, re
from pathlib import Path
import gradio as gr

FAQ_PATH = Path(__file__).with_name("faq.json")

def tokens(text):
    return set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))

def retrieve(question):
    faqs=json.loads(FAQ_PATH.read_text(encoding="utf-8"))
    q=tokens(question)
    ranked=[]
    for faq in faqs:
        score=len(q & tokens(faq["title"]+" "+faq["text"]))
        ranked.append((score,faq))
    ranked.sort(key=lambda x:(-x[0],x[1]["title"]))
    return ranked[0] if ranked else (0,None)

def chat(message, history):
    score,faq=retrieve(message)
    if not faq or score==0:
        return "등록된 FAQ에서 확인할 수 없습니다.\n\n출처: 없음"
    return f"{faq['text']}\n\n출처: {faq['title']}"

demo=gr.ChatInterface(fn=chat,title="LAB 1 · Indexing",description="FAQ 지식을 하나 추가한 뒤 같은 질문을 다시 실행합니다.",examples=["오늘 점심은 무엇인가요?","이미 출발했는데 환불되나요?"])
if __name__=="__main__": demo.launch()
