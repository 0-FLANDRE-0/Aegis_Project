# Helicopter model inspector v01

완료 범위는 사용자 DDG-118 GLB에서 SH-60 정적 대체 부품을 추출하고, 격납/전개/비행 공통 asset을 만든 모델 검사다. 원본 참조용 GLB, 게임용 공유 경량 데이터와 독립 미리보기를 제작했다. 원본 삼각형과 재질을 유지하며 새 텍스처나 loader 의존성을 추가하지 않는다.

결과: lossless GLB 591,920 bytes, 경량 압축 223,419 bytes, 독립 HTML 538,238 bytes. 기존 Three를 재사용하는 게임 내 모델·로더 추가량은 301,239 bytes (+1.9176%). 원형 구조 14/14, native 비교/수명주기 13/13, 최종 scene/UI 24/24, 정적 문법 PASS. 원본과 경량본 세 자세의 native PNG를 보존했다. [상세 계약·재현·제한](README.md), [SHA](SHA256SUMS.txt).

기준은 performance-f final `4c8514596ce10dd2f00121bccf62c5b042809d3f`. Simulator PERF_F bytes/SHA, stable v48, 과거 검사 및 workflow를 보존했다. 모델 전용 `helicopter-model-a` 브랜치이며 시뮬레이터 버전 승격은 하지 않는다. §7.1의 기존 사용자 승인 범위에서 asset/검사기/지원 자료를 직접 upload하고 원격 bytes/blob를 다시 확인한다. Actions 실행과 CI PASS, PR/병합 결과를 주장하지 않는다.

미완료: 세부 SH-60 형식 확정, meter 축척 교정, 동적 로터/꼬리 animation, 장착/격납 전이, 항공 물리·센서·AI·초수평선 탐지·통신, 실제 GPU/휴대폰 성능. source에 skin/animation이 없으므로 animation은 추가로 작성해야 한다. 다음 단계는 축척·회전축 및 함정 갑판/격납고 배치와 LOD 설계다.
