# SESSION 0 - Continue로 Gradio 설치 확인

> 설치부터 하지 않습니다. Continue가 현재 Python 환경에서 Gradio가 있는지 먼저 확인합니다.

## 1. VS Code에서 폴더 열기

ZIP 압축을 푼 뒤 `D19_GRADIO_3LABS` 폴더 전체를 VS Code로 엽니다.

관측 문턱:

- Explorer 맨 위에 `D19_GRADIO_3LABS`가 보임
- 하위에 `01_INDEXING_LAB`, `02_RETRIEVAL_LAB`, `03_GENERATION_LAB`이 보임
- Continue 패널이 보임

## 2. Continue에 아래 프롬프트 붙여넣기

```text
현재 VS Code 터미널에서 실제로 사용되는 Python 명령과 버전을 먼저 확인해줘.
그 Python 환경에서 gradio를 import할 수 있는지 검사해줘.

검사에 성공하면 설치하지 말고 Gradio 버전만 보고해줘.
검사에 실패한 경우에만 이 프로젝트의 requirements.txt를 사용한 설치 명령을 제안해줘.
명령을 임의로 실행하지 말고 Run terminal command 승인 화면에서 기다려줘.
설치 후 같은 Python으로 import와 버전을 다시 검사해줘.
마지막으로 실행한 명령, 성공 여부, 다음 실행 명령을 짧게 보고해줘.
```

## 3. Continue의 Run terminal command 확인

Continue가 보여주는 명령을 읽고 `Accept`합니다.

정상적인 검사 명령 예시:

```bash
python -c "import sys; print(sys.version)"
python -c "import gradio; print(gradio.__version__)"
```

Gradio가 없을 때 정상적인 설치 명령 예시:

```bash
python -m pip install -r requirements.txt
```

Mac에서 `python`이 없고 `python3`만 있으면:

```bash
python3 -m pip install -r requirements.txt
```

## 4. 설치 PASS 화면

아래 두 가지가 모두 보여야 합니다.

```text
Python 버전
Gradio 버전
```

`ModuleNotFoundError: gradio`가 남아 있으면 PASS가 아닙니다.

## 5. 첫 앱 실행

Continue에 아래 프롬프트를 붙여넣습니다.

```text
01_INDEXING_LAB 폴더의 app.py를 현재 확인한 같은 Python으로 실행해줘.
파일을 수정하지 마.
터미널에 localhost 주소가 나오면 그 주소와 실행 성공 여부만 보고해줘.
```

정상 관측:

```text
http://127.0.0.1:7860
```

브라우저에서 이 주소를 열어 `LAB 1 · Indexing`이 보이면 설치 세션 완료입니다.

## 오류별 복구

### `No module named pip`

Continue에 다음과 같이 요청합니다.

```text
현재 Python에 pip가 없는 원인을 확인해줘. 다른 Python 실행 명령에 pip가 이미 있는지도 확인해줘. 새 Python 설치는 하지 말고, 사용할 수 있는 기존 Python과 그 명령을 보고해줘.
```

### 설치했는데 계속 `No module named gradio`

설치에 사용한 Python과 앱 실행에 사용한 Python이 다른 경우입니다.

```text
Gradio 설치에 사용한 Python 경로와 app.py 실행에 사용한 Python 경로가 같은지 확인해줘. 파일은 수정하지 말고 두 경로만 비교해줘.
```

### 결제·카드·API 키 화면

이 실습은 Gradio UI 체험이며 API 키와 결제가 필요 없습니다. 그런 화면이 나오면 진행하지 말고 강사에게 알립니다.
