# HELI_F2_0 — EMCON 방사 없는 수동 지정 (0번 단독 단계)

HELI_CG_B `273c36f` 위 `helicopter-emcon-f2-0`. ISAR1번 이후는 이 단계에 포함하지 않는다.

ARM → LOCK은 EMCON 중에도 표시 가능한 트랙을 커서로 지정한다. selectedLockId만 수신 트랙을 가리키고 SPY mode는 TWS/pdTracking=false를 유지한다. 버튼과 알림은 `지정 (EMCON · 방사 없음)`이다. EMCON 중에는 기존 SPY 섹터 제한을 적용하지 않고, 표시 불가 트랙까지 되살리지는 않는다.

EMCON ON 전환은 PD만 끝내고 지정을 남긴다. 이전 AUTO/SEMI의 lock 소유권을 해제해 자동 추천 없음 처리로 운용자 지정을 지우지 않는다. EMCON OFF는 지정된 표시 트랙이 기존 SPY 섹터 검사에 통과하면 PD로 이어지고, 밖이면 지정만 유지한다. 개별 버튼/전단 group EMCON/진단 setter가 같은 전환 함수를 사용한다. fixed-step updateRadar는 EMCON 중 PD=true가 남지 않도록 방어한다. MODE 버튼은 EMCON 중 PD를 켜지 않는다.

지정 직후 기존 하푼 UI를 갱신한다. 품질 관문이나 무장 권한을 우회하지 않고 이전 NO_TRACK 표시가 남는 것을 없앤다. 하푼 F1 관문·수동 권한·10초·예측 바스켓·손상·사거리·발사 자세·좌표 발사·무DL 정책은 변경하지 않는다.

VLS 버튼과3D 발사/3D AUTO LOCK/AUTO TGT의 EMCON 차단, SPG-62 조사·자동교전 차단은 보존한다. SM-2 native AUTO_RADIATE와 ESSM BLOCK_FIRE 등 기존 내부 정책 자체도 변경하지 않는다. Hawklink/Link16은 기존처럼 레이더 EMCON과 독립이다.

교전 로그에 `launchEmcon:boolean`을 넣고 복사 가능한 DEBUG 텍스트에도 표시한다. 발사 요청 시각이 아니라 최종 재검사 뒤 실제 탄약이 커밋되는 시점의 함 EMCON이다. foreign owner는 해당 함 observer의 실제 EMCON을 읽는다. 종료 기록만 AFTER_ACTION_TRUTH이며, 전술/센서/AI/유도는 로그를 읽지 않는다.

`window.__EMCON_DESIGNATION_F2__.snapshot()`은 detached 진단 값이다. 선택/PD/섹터/레이블과 기존 RF 프런트엔드의 자함 SPY 물리 방사원 개수만 읽으며 새 발사 권한을 제공하지 않는다.

검사 수와 원본 SHA는 [검증 요약](evidence/verification-summary.json)을 따른다. 실제 CG H1이300m PERI로40km 표적을 측정해 모함 Hawklink로 만든 순수OFFBOARD 트랙을 ARM 버튼으로 지정하고 실제 하푼 발사/launchEmcon=true를 확인한다.8km/450km 익명 보고는 진단 전용 섹터 경계 검사이며450km 실제 Hawklink 운용을 주장하지 않는다.390×1000/1100×800 실제 포인터의 기존 차단 버튼과 요청 후 EMCON 해제→실제 발사 로그false도 확인한다. 소프트웨어 Chromium이며 실제 기기 FPS는 측정하지 않는다.

```sh
python docs/helicopter/K/build.py archive/v48/WIP_HELI_CG_B/Aegis_SIM_v48_WIP_HELI_CG_B.html /tmp/HELI_F2_0.html
python docs/helicopter/K/verify_static.py archive/v48/WIP_HELI_CG_B/Aegis_SIM_v48_WIP_HELI_CG_B.html Aegis_SIM_v48_WIP_HELI_F2_0.html artifacts/static
python docs/helicopter/K/verify_native.py Aegis_SIM_v48_WIP_HELI_F2_0.html artifacts/native
python docs/helicopter/K/verify_ui.py Aegis_SIM_v48_WIP_HELI_F2_0.html artifacts/ui
python docs/helicopter/F/verify_regression.py archive/v48/WIP_HELI_CG_B/Aegis_SIM_v48_WIP_HELI_CG_B.html Aegis_SIM_v48_WIP_HELI_F2_0.html artifacts/regression --baseline-only
```

기존 HTML 네 파일/과거 A–J 소스·증거/stable을 동일 bytes로 보존한다. 원본 직접 GitHub 업로드 및 독립 decoded blob readback. Actions dispatch/main·이전 브랜치 병합/새 PR은 하지 않는다. 다음은 사용자 요청1번부터의 ISAR다.
