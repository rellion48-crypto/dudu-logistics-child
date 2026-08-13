import gradio as gr
from settings import RESPONSE_STYLE

FACT="발송 후에는 반품 접수와 상품 회수 확인 뒤 환불됩니다."
SOURCE="환불 FAQ"

def chat(message,history):
    if RESPONSE_STYLE=="steps":
        answer="1. 주문번호를 확인해 주세요.\n2. 반품을 접수해 주세요.\n3. 상품 회수 확인 뒤 환불됩니다.\n\n주문번호를 알려주시겠어요?"
    else:
        answer=FACT
    return f"{answer}\n\n출처: {SOURCE}"

demo=gr.ChatInterface(fn=chat,title="LAB 3 · Generation",description="답변 규칙 한 줄만 바꾸고 같은 근거를 전달하는 방식을 비교합니다.",examples=["이미 출발했는데 환불되나요?"])
if __name__=="__main__": demo.launch()
