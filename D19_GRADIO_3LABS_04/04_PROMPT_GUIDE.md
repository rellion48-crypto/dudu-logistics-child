# Continue 프롬프트 가이드

AI에게 전체 앱을 다시 만들라고 하지 않습니다. 현재 실습의 변수 하나만 바꾸게 합니다.

## Gradio 설치 확인

설치 프롬프트 전체는 `00_INSTALL_GRADIO_WITH_CONTINUE.md`에 있습니다. 핵심 순서는 아래와 같습니다.

```text
현재 Python 확인
→ Gradio import 검사
→ 없을 때만 requirements.txt 설치 제안
→ 학생이 Run terminal command Accept
→ 같은 Python으로 import 재검사
→ app.py 실행
```

## 공통 프롬프트 구조

```text
현재 [파일명]에서 [변수 하나]만 바꿔줘.
그 외 파일과 동작은 변경하지 마.
변경한 줄과 예상되는 화면 변화만 설명해줘.
```

## Indexing

```text
01_INDEXING_LAB/faq.json에
제목이 "점심 메뉴 FAQ"이고 내용이 "오늘 점심 메뉴는 김치볶음밥입니다."인 FAQ 하나만 추가해줘.
기존 FAQ와 app.py는 변경하지 마.
JSON 문법이 유효한지 확인해줘.
```

## Retrieval

```text
02_RETRIEVAL_LAB/settings.py에서 TOP_K 값만 1에서 3으로 바꿔줘.
다른 파일과 코드는 변경하지 마.
```

## Generation

```text
03_GENERATION_LAB/settings.py에서 RESPONSE_STYLE 값만 "short"에서 "steps"로 바꿔줘.
다른 파일과 코드는 변경하지 마.
```

## 오류 복구 프롬프트

```text
방금 변경으로 실행 오류가 났어.
오류 메시지를 읽고, 내가 방금 바꾼 파일 하나만 최소 수정해줘.
다른 실습 폴더는 절대 변경하지 마.
수정 전에 오류 원인을 한 문장으로 말해줘.
```

## 금지 프롬프트

- 전체 프로젝트를 개선해줘
- RAG 앱을 새로 만들어줘
- 코드를 더 고급스럽게 바꿔줘
- 세 실습을 하나로 합쳐줘

이 프롬프트들은 변수 하나와 결과 하나의 관계를 볼 수 없게 만듭니다.
