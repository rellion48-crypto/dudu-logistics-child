# LAB 4 · Complete RAG (Gradio 실습)

본 프로젝트는 **Gradio**와 **Gemini API**를 활용하여 검색(Retrieval)과 생성(Generation)이 결합된 **Complete RAG(Retrieval-Augmented Generation)** 시스템을 구축하고 실험하는 LAB 과정입니다.

---

## 📁 프로젝트 구조

```text
D19_GRADIO_3LABS_04/
├── app.py              # Gradio 기반 RAG 챗봇 메인 애플리케이션
├── settings.py         # RAG 검색 및 생성 옵션 설정 파일 (TOP_K, MIN_SCORE, USE_GEMINI)
├── faq.json            # FAQ 데이터셋 (환불, 배송, 교환 등)
├── HOW_TO.md           # 실습 가이드 및 실험 질문 목록
├── faq.json            # FAQ 데이터
├── reset.py            # 설정 초기화 스크립트
├── run_windows.bat     # Windows 실행 스크립트
├── run_mac.command     # macOS/Linux 실행 스크립트
└── baseline/
    └── settings.py     # 초기 설정 백업 파일
```

---

## ⚙️ 주요 기능 및 설정 (`settings.py`)

`settings.py` 파일의 세 가지 핵심 변수를 조합하여 RAG 동작 방식을 실험할 수 있습니다.

1. **`TOP_K`**: 검색된 FAQ 결과 중 답변에 참고할 최대 문서 수 (기본값: `3`)
2. **`MIN_SCORE`**: 검색 매칭 점수 임계값. 이 점수 이상의 FAQ만 검색됨 (기본값: `1`)
3. **`USE_GEMINI`**: 
   - `True`: Gemini AI를 사용하여 검색된 FAQ 근거를 바탕으로 자연스러운 문장 생성 (`Gemini`)
   - `False`: 검색된 FAQ 원문 그대로 출력 (`규칙`)

---

## 🚀 실행 방법

### 1. 사전 준비
`app.py` 파일 상단의 `GEMINI_API_KEY`에 본인의 Gemini API 키가 올바르게 입력되어 있는지 확인하세요.

```python
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

### 2. 실행하기
- **Windows**: `run_windows.bat` 실행
- **macOS / Linux**: 터미널에서 `run_mac.command` 실행 (또는 직접 터미널에서 실행)
  ```bash
  python app.py
  ```

실행 후 터미널에 표시되는 로컬 URL(예: `http://127.0.0.1:7860`)을 웹 브라우저에 입력하여 챗봇 인터페이스를 사용할 수 있습니다.

---

## 🧪 실습 실험 및 질문 (`HOW_TO.md`)

### 실험 1: TOP_K 비교
- `TOP_K = 1`: FAQ 1개만 참고하여 답변
- `TOP_K = 3`: FAQ 3개를 참고하여 답변

### 실험 2: Gemini vs 규칙 기반 비교
- `USE_GEMINI = True`: AI가 자연어로 답변 생성
- `USE_GEMINI = False`: FAQ 원문 그대로 출력

### 실험 3: MIN_SCORE 조정
- `MIN_SCORE = 1`: 느슨한 검색 (더 많은 결과 매칭)
- `MIN_SCORE = 3`: 엄격한 검색 (정확도 높은 결과만 매칭)

### 💡 토론 및 점검 질문
1. "TOP_K를 올리면 Gemini 답변이 어떻게 달라지나?"
2. "Gemini를 끄면 어떤 점이 불편한가?"
3. "MIN_SCORE를 올리면 어떤 질문이 답을 못 받나?"

---

## 🔄 초기화
설정을 초기 상태로 되돌리려면 아래 명령어를 실행하세요:
```bash
python reset.py
```
