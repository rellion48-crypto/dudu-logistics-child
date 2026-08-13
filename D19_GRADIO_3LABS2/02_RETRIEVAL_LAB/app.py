import json,re
from pathlib import Path
import gradio as gr
from settings import TOP_K

FAQ_PATH=Path(__file__).with_name("faq.json")
SYNONYMS={"늦어서":{"배송","지연"},"돌려받고":{"환불"},"환불":{"환불"},"취소":{"환불"}}
def tokens(text):
    base=set(re.findall(r"[가-힣A-Za-z0-9]+",text.lower()))
    for word,extra in SYNONYMS.items():
        if word in text: base|=extra
    return base

def search(question):
    q=tokens(question); faqs=json.loads(FAQ_PATH.read_text(encoding="utf-8")); ranked=[]
    for faq in faqs:
        # Check keywords if present, combined with title and text tokens
        faq_tokens = tokens(faq["title"]+" "+faq["text"])
        if "keywords" in faq:
            for kw in faq["keywords"]:
                faq_tokens.update(tokens(kw))
        score=len(q & faq_tokens)
        ranked.append((score,faq))
    ranked.sort(key=lambda x:(-x[0],x[1]["title"]))
    return [x for x in ranked if x[0]>0][:TOP_K]

def chat(message,history):
    hits=search(message)
    if not hits: return f"검색 근거 없음\n\nTOP_K = {TOP_K}"
    lines=[f"{i+1}. {faq['title']}" for i,(score,faq) in enumerate(hits)]
    return f"TOP_K = {TOP_K}\n\n가져온 근거:\n"+"\n".join(lines)

demo=gr.ChatInterface(fn=chat,title="LAB 2 · Retrieval",description="TOP_K 한 줄만 바꾸고 같은 질문의 검색 출처를 비교합니다.",examples=["배송이 늦어서 환불하고 싶어요."])
if __name__=="__main__": demo.launch()
