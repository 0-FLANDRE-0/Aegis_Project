# v48 WIP MULTI SHIP E — 5C/5D 방어 AUTO·항공기 스폰

HTML `Aegis_SIM_v48_WIP_MULTI_SHIP_E.html`, 15,609,329 bytes, SHA `d1aa4b1876bea2739aec17f6f2c4e421e5ecef9957aa28113fab14d4117d0af2`. decoded main SHA `446f96c11279970cda4d9e5542137dad96ba86ee155f3f503cbf83fa51f2c105`. 기준 D head `c6da52b960b447d8b4eadb6cac904b9c0ebff730`, D HTML SHA `babac7fba08e4d59628c25245b1c657a87516f6774f6ec505c2314b1e3c1bf6e`.

## 구현

배치 적함의 원본 AUTO/BDA/alias 67개 함수를 기존 owner 무장 closure에 결속했다. 기본 방어 AUTO, 측정 acceleration/CPA/NEZ·식별/hostile intent·ROE·사각·장비·탄약·조명·salvo를 기존 커널로 평가하고 release 직전에도 재검사한다. 독립 C55 확인 관측으로 RAM/Phalanx 동의를 갱신하여 실제 근접방어/연속 burst를 실행한다. CG는 양현 Phalanx이며 RAM 미설치다.

무장효과와 후속 관측에 따른 BDA/재평가, DIRECT 지원 해제와 FUZE→DIRECT 시각 갱신, 검증된 같은-frame alias의 owner key/지원 이관을 사용한다. 외국 local track ID를 자함 BDA로 전달하지 않는다. real breakup 잔해는 공통 physical collector로 처리한다. 실제 alive/truth로 격추 확정하지 않는다. offline SPG reset의 mutable binding·metadata shape도 원본 계약으로 교정했다.

함선 선택/적재의 출항 전 적 항공기 ON/OFF를 동기화했다. ON 기본은 기존 조건, OFF는 정상 초기/주기/reset/새 해역·delayed spawn을 막는다. E_1 strict boolean codec, legacy A_1→ON migration, atomic 거부와 저장/복원을 지원한다. 출항 후 선택 잠금. 함정 inventory는 유지하고 BDA/비행/pending 살보는 transient다.

공통 world1회·owner1회·60/120/20Hz, 원본 asset0~12와 profile/module revision, stable v48은 유지한다. renderer는 read-only이며 foreign 무장 telemetry를 자함 목록에 넣지 않는다. Harpoon DL=0/INS/ARH와 원본 물리·피해를 유지한다.

## 검증과 한계

최종 같은 SHA 직접 검사 **660/660 PASS**. 직접 결과는 [verification-summary](docs/multiship/E/evidence/verification-summary.json), 실행 계약은 [README](docs/multiship/E/README.md), 측정 조건은 [PERFORMANCE](docs/multiship/E/PERFORMANCE.md)다. initial candidate와 탐색 방향 실험은 최종 PASS에 합산하지 않는다. 최신 head CI는 E static+18 browser와 기존 smoke의 PR checks를 따른다.

실제 자연20m Kh-35U에서 DDG RAM/CG Phalanx 자동발사, 실제8km Harpoon에서 DDG ESSM2발을 확인한다. 해당 Harpoon seed에서는 접촉도 발생한다. CG 저고도 Harpoon은 확인된 ASM 관측 없이 발사0이며 검출 문턱이나 사각을 억지로 바꾸지 않는다. 격추율·검출 보장, 신규120~140km 함정간 battle·모바일 FPS 인증은 아니다. measured/effect fixture와 자연 실탄·native RAF/WebGL을 구분한다.

receiver별 EW, 공격/기동 AI와 헬기·다수 함정 성능/얇은 장비 contact는 [다음 단계](docs/multiship/E/DEPENDENCIES.md)다. D 세트/workflow를 동일 bytes archive에 보존했고 stable v48 SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83` 유지. §7.1에 따라 원본 HTML 업로드/readback을 수행하고 D 위 PR을 만든다. main/A/B/C/D는 미병합 유지한다.
