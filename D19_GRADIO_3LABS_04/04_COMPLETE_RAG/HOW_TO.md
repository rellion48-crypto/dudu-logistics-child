# LAB 4 - Complete RAG

## 준비
`app.py`에서 `GEMINI_API_KEY = ""`에 LAB 3에서 발급한 키를 넣습니다.

## 바꿀 것
`settings.py`의 세 변수를 조합해서 바꿉니다.

### 실험 1: TOP_K 비교
```python
TOP_K = 1   # FAQ 1개만 보고 답함
TOP_K = 3   # FAQ 3개를 보고 답함
```

### 실험 2: Gemini vs 규칙
```python
USE_GEMINI = True    # AI가 자연어로 답함
USE_GEMINI = False   # FAQ 원문 그대로
```

### 실험 3: MIN_SCORE 올리기
```python
MIN_SCORE = 1   # 느슨하게 검색
MIN_SCORE = 3   # 엄격하게 검색
```

## 질문 3개
1. "TOP_K를 올리면 Gemini 답변이 어떻게 달라지나?"
2. "Gemini를 끄면 어떤 점이 불편한가?"
3. "MIN_SCORE를 올리면 어떤 질문이 답을 못 받나?"
