# 환경 세팅 및 실행 계획 (Plan.md)

본 문서는 `D19_GRADIO_3LABS_04` 프로젝트(LAB 4 · Complete RAG)를 로컬 환경에서 올바르게 설정하고 실행하기 위한 단계별 계획서입니다.

---

## 📋 1. 사전 요구 사항 (Prerequisites)
- **Python 버전**: Python 3.10 이상 권장
- **필요 라이브러리**: `gradio` (그 외 표준 라이브러리 `json`, `re`, `urllib.request`, `pathlib` 사용)
- **API Key**: Gemini API Key 발급 필요

---

## 🛠️ 2. 환경 세팅 단계 (Step-by-Step)

### Step 1: 필수 패키지 설치
터미널에서 Gradio 라이브러리를 설치합니다.
```bash
pip install gradio
```
*(또는 프로젝트에 `requirements.txt`가 있는 경우 `pip install -r requirements.txt`)*

### Step 2: API Key 설정 확인
`app.py` 파일 내에 Gemini API Key가 올바르게 설정되어 있는지 확인합니다.
```python
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```
* 보안상 `.env` 파일이나 환경 변수로 분리하여 관리할 수도 있습니다. (현재 `app.py`에는 직접 입력되어 있거나 기본값이 설정되어 있음)

### Step 3: RAG 파라미터 설정 (`settings.py`)
실험 목적에 맞게 `settings.py` 값을 확인 및 수정합니다.
- `TOP_K`: 검색할 문서 개수 (기본값: `3`)
- `MIN_SCORE`: 최소 검색 점수 (기본값: `1`)
- `USE_GEMINI`: Gemini AI 생성 사용 여부 (`True` 또는 `False`)

---

## 🚀 3. 실행 및 테스트 (Execution)

### 방법 A: 스크립트 실행
- **Windows**: `run_windows.bat` 더블 클릭 또는 터미널에서 실행
- **macOS / Linux**: 터미널에서 실행 권한 부여 후 실행
  ```bash
  chmod +x run_mac.command
  ./run_mac.command
  ```

### 방법 B: 직접 파이썬 실행
```bash
python app.py
```

### 접속 방법
터미널에 출력되는 로컬 주소(예: `http://127.0.0.1:7860`)를 웹 브라우저에 입력하여 챗봇 UI 접속 및 테스트 수행.

---

## 🧪 4. 검증 및 실험 계획 (Verification & Experiments)
1. **기본 동작 확인**: 예시 질문("이미 출발했는데 환불되나요?") 입력 후 정상적인 RAG 응답 및 출처 확인
2. **실험 1 (`TOP_K`)**: `settings.py`에서 `TOP_K`를 `1`과 `3`으로 변경하며 답변의 풍부함 비교
3. **실험 2 (`USE_GEMINI`)**: `USE_GEMINI`를 `False`로 설정하여 규칙 기반(원문 출력) 모드 테스트
4. **실험 3 (`MIN_SCORE`)**: `MIN_SCORE`를 `3`으로 올려 엄격한 검색 조건에서의 동작 테스트
