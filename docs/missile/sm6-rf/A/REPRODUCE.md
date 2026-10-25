# 재현

원본 kit는 `kit/`에 그대로 있다.5파일 MANIFEST와 최초 ZIP의 SHA는 `input-provenance.json`을 따른다. 기준 저장소 `launch-handoff-a@99c2ef33e5256acbfb3aa557a01065669404de89`의 원본 HTML/지원 파일이 필요하다. 이 보고서 ZIP 자체가 독립 게임 실행 파일은 아니다.

저장소 루트에서 첨부 README 순서로 실행한다. 출력은 비어 있는 **새 폴더**여야 한다.

```sh
python docs/missile/sm6-rf/A/kit/probe_sm6_240km_rf.py --repo "$PWD" --output /tmp/sm6-native-check --native-only
```

양쪽 `nativeObserverExact:true`와 기존 전체 반환값 동등성을 확인한 뒤:

```sh
python docs/missile/sm6-rf/A/kit/probe_sm6_240km_rf.py --repo "$PWD" --output /tmp/sm6-three-modes
```

게임 파일을 편집하지 않는다. NATIVE 결과가 다르면 분석을 중단한다. 다른 HTML을 허용하려고 pin이나 비교 기준을 조용히 바꾸지 않는다. 반사실을 제품에 이식하지 않는다.

이번 기록의 `native-first/`와 `all-modes/`는 위의 선행2발/이후6발이다. kit Python/JS는 수정하지 않았다. `analyze_rf.py`, `compare_prefix.py`는 저장된 raw를 읽는 별도 분석기다.같은 구조의 출력 폴더를 복사한 별도 작업 사본에서 파생 분석을 다시 생성할 수 있다. 분석기 실행은 파생 CSV/그림을 쓰므로 기존 증거 사본을 먼저 보존한다.

```sh
python docs/missile/sm6-rf/A/analyze_rf.py
python docs/missile/sm6-rf/A/compare_prefix.py
```

Python3.12, Node24(stub), Playwright/Chromium, matplotlib를 사용했다. 실행 환경의 원래 `browser_tools.py`와 CPU Canvas2D backend/SwiftShader를 그대로 재사용했다. 실제 폰 성능을 측정하지 않았다. 새로운 프로파일/PN/추진/공력/RNG/신관 모델은 없다.

관찰기는 PRE_DYNAMICS의 동일 경계에서 상대 추정 오차를 계산한다. `lastNisCached`는 캐시, `nisFresh`는 현재 association 호출의 값이다. `ekfFresh/ekfAccepted`와 전/후 상태를 함께 보아야 한다. PN/APN/ZEM의 옛 캐시 값을 현재 활성 명령이라고 읽지 않는다.

`analysis/first-differences.json`은 첫 실제 차이를 전/후 경계별로 분리한다. `analysis.json`의 문턱은 복수 진단 기준이며 게임 계수가 아니다. 항력 일은 기록된 native 힘의 진단 적분이며 새 비행 모델이나 완전 에너지 결산이 아니다.

`provenance.py`는 폐기 가능한 페이지에서 live 함수 text/hash를 수집한다. v1은 부분 함수 메타데이터, v2는14개 확장 메타데이터이며 새 비행 횟수로 세지 않았다. `source-equivalence.json`은 그 실제 text가 선택 HTML의 압축 해제 main에 존재하는지도 검사한다. 오래된 첫 동명 선언만으로 실행 경로를 추정하지 않는다.
