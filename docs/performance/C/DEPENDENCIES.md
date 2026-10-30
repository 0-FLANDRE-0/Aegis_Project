# PERF_C 검증 의존성

- Python 3.12, `docs/bunkerhill/K/requirements.txt`의 Playwright 1.62.0.
- Chromium 151.0.7922.173, `AEGIS_CHROMIUM_EXECUTABLE=/usr/bin/chromium`.
- Node 24.19.0, acorn 8.19.0, eslint-scope 9.1.2. `package-lock.json`으로 고정한다.
- `node_modules`, Python 캐시와 실행 scratch는 저장소 반영 대상에서 제외한다.
- headless 브라우저의 네트워크/socket 실행 권한과 WebGL 검사는 SwiftShader를 사용했다. GPU/모바일 FPS 인증은 아니다.
