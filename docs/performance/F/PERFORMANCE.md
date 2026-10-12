# PERF_F 최종 검증 결과

최종 HTML SHA `4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5`. 원본 1817/1817 PASS, 38 suites, 오류0. CG 체인 텍스처의 owner retirement 누락도 보완했다. E에서 unique texture1/dispose0을 재현했고 F는 per-presenter ownedTextures Set으로 한 번 해제하며 DDG 공유 factory textures는 유지한다.

## 두 번째 피격 표시

E/F 원본 native RAF/THREE/SwiftShader LOW640×480에서 x12/z4 첫 구멍의 실제 anchor 제출 직후 x25/z4 두 번째 detached 피격을 추가했다. 두 함종 각2회, 반대 AB/BA, 총4쌍/8pages, 전체 회귀/카메라 종료 후 직렬이다. job drainage/fake clock 없음. 현재6ms render allowance와 fixed simulation은 그대로다. 실제 cut keys·GL0·physical snapshot/RNG 고정을 확인했다. 보존된 측정 전 snapshot과 RNG도 모든 E/F 쌍에서 exact였으며 native-paired-state.json에 별도로 남긴다.

| 자함 | E 두 번째 cut 제출 평균 초 | F 평균 초 | 관측 지연 감소 |
|---|---:|---:|---:|
| CG_52_LATE_TICONDEROGA | 162.882 | 2.716 | 98.3% |
| DDG_119_LATE_FLIGHT_IIA | 25.841 | 0.215 | 99.2% |

이 값은 host CPU submission 시간이다. hardware GPU 완료나 phone FPS가 아니다. 첫 actual anchor 다음 새 피격을 넣는 제어 조건이므로 모든 피격 위치·자연 다발 피격 성능을 일반화하지 않는다. 완료 후 최종 geometry는 별도 original THREE fixture에서 exact다. CG 개별 F 제출은 0.0333/5.3977초, DDG는0.4117/0.0173초였다. 두 번의 짧은 반복 편차를 평균만으로 숨기지 않는다.

## 부하와 자원

두 함종 각각24×300 =7200fixed ticks(120 simulated seconds), 세 함정, CG64/DDG16native Kh32 diagnostic workload에서 E/F 각24개 전체 authoritative snapshot, RNG/entity counts를 비교한다. host performance/profiler/lastBuildMs/lastAssessmentMs만 제외하고 raw states를 보존한다. post-GC JS heap은 계측 범위에서 급증하지 않는지 확인한다. 실제 수시간 플레이·VRAM 측정은 아니다. 기능 검사의 소요 시간은 성능 수치로 사용하지 않는다. CG F heap은 초기96.04MiB에서 마지막127.17MiB였으며 마지막8구간127.17〜133.35MiB였다. DDG는101.32→117.35MiB, 마지막8구간116.68〜117.80MiB였다. 초기 데이터/전투 기록이 늘어난 만큼의 증가를 숨기거나 메모리가 전혀 늘지 않았다고 주장하지 않는다. 최종 유효 snapshot import preflight도 네 페이지 모두 통과했다.

Native import/reset 8회×2함종에서1200smoke와4Kh32의 실제 GPU geometry/texture 회수, pool/maps 청소, warm-up 이후 GPU resource count를 확인한다. pending quick-cut 외부 함정의 실제 runtime replacement 후 presenter/root/originals/live geometry가 dispose되는지 확인한다. combat sinking 자체 시험은 아니다.

## 누적 최적화 수치의 기준

현재 F는 표시용 queue 선점과 CG 전용 텍스처 회수만 바꿨고 physics CPU·연기shader/model은 E와 같다. [E의 직접 H4A→E 누적 측정](../E/PERFORMANCE.md)은 당시 최종 E 원본의 기록으로 유지한다. F를 다시 누적 측정했다고 주장하지 않는다. 그 기록의64발 host CPU 감소는 자함34.8%, 세 함정42.7%였으며 일부 idle 조건은 증가했다. 단계별 개선율은 더하지 않는다.

계획한 마지막 최적화 검증 범위는 완료했다. 실제 장치 FPS/수시간 soak는 미실행이다. 다음 기능은 헬기/초수평선 탐지, 이후 RGM-109E Block Va다. Actions dispatch/CI PASS 주장은 없다.
