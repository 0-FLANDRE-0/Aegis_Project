# WIP12E REV4 수동 업로드 절차

대상 repository는 `0-FLANDRE-0/Aegis_Project`, 대상 branch는 `feat/v48-wip12e-compartment-blast`다. 작업 번호는 **WIP12E**이며 `REV4`는 브라우저 캐시 우회용 파일 식별자다.

## 업로드 파일

- 로컬 파일과 branch 경로: `Aegis_SIM_v48_WIP12E_REV4_BLAST_DAMAGE_COUPLING_FIX.html`
- 크기: `3,212,922 bytes`
- SHA-256: `856ec05e4acd6c7a04bb9da580a46c550cb33341cb82e6b5cb086237930fa3a3`
- 이전 REV3 SHA-256 `0a512fbd406977513a293a15a7c4682e9eec22692fb1836c19808b8772f91842`는 이번 시험에 사용하지 않는다.

## 절차

1. GitHub UI 또는 정상 인증된 `git` 전송을 사용한다.
2. branch가 `feat/v48-wip12e-compartment-blast`인지 확인한다.
3. REV4 파일을 이름을 바꾸지 않고 repository 루트에 추가한다.
4. 원격 파일을 다시 내려받아 SHA-256과 크기를 검증한다.
5. REV4 계약 테스트와 Playwright 4개를 실행한다.
6. 실제 브라우저가 REV4 title/contract를 읽는 것을 확인한 뒤에만 필요 시 canonical `Aegis_SIM_v48_WIP12E.html`로 승격한다.
7. 그 다음 `package.json`, workflow, README 및 `AEGIS_PROJECT_INSTRUCTIONS.md` 전환 commit을 만든다.

큰 HTML은 contents API, base64 또는 파일 분할 방식으로 우회 업로드하지 않는다.

## 검증 명령

```bash
sha256sum Aegis_SIM_v48_WIP12E_REV4_BLAST_DAMAGE_COUPLING_FIX.html
node tests/blast-damage-coupling-wip12e-rev4-contract.cjs
THREE_JS_PATH=/path/to/three.min.js npx playwright test tests/blast-damage-coupling-wip12e-rev4.spec.js --workers=1
```

기대 결과는 계약 `57/57 PASS`, Chromium `4/4 PASS`, console/page error `0/0`이다.
