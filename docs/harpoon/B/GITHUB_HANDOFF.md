# Harpoon B GitHub 인계

최신 업로드 대상은 **`Aegis_SIM_v48_WIP_HARPOON_B.html` 하나**다. A의 하푼 운용에 노즐·빈 관·짙은 연기·3.2초 부스터를 반영한 파일이며 A를 먼저 업로드할 필요가 없다.

- 크기: **15,274,780 bytes**
- HTML SHA-256: `a44a346abce0bb0e10b4cff231116171d0c13de1b8962d45820c6c6d10de98fc`
- main SHA-256: `3e5db4f820844d3301617f5c3e21e69f03619e05dba056532483954a6c88ecbf`
- 준비 branch: [harpoon-block1c-a](https://github.com/0-FLANDRE-0/Aegis_Project/tree/harpoon-block1c-a)
- 재확인한 main/branch head: `f51247496725aa8aadad69d5c8d3449c5bbc3a81`; push/admin 권한 확인. [원격 조회](evidence/remote-branch.json).

[프로젝트 지침 7.1](../../../AEGIS_PROJECT_INSTRUCTIONS.md#71-github-업로드-분담)의 “사용자가 그 HTML을 지정 브랜치에 직접 업로드하면 ChatGPT가 원격 파일의 SHA-256과 브랜치 기준을 확인한다”는 분담을 유지한다. 사용자는 최신 B를 branch 루트에 같은 파일명으로 올린다. 새 원격 HTML/support/PR/CI/병합은 아직 실행하지 않았다.

Codex는 사용자 업로드 뒤 원격 크기·SHA·Git blob·branch ancestry를 정확히 대조한다. source 변경이 섞였으면 같은 파일명만 보고 통과로 취급하지 않는다. 이후 작은 A/B 모듈·asset·검사·evidence·상태·SHA·README·지침과 B workflow를 반영한다. 기존 remote K HTML/상태/SHA는 동일 Git blob으로 archive에 이동한다.

**A HTML은 remote에 올라간 적이 없다.** 로컬 `archive/v48/WIP_HARPOON_A/`의 원본 A HTML을 새 Git blob/API 또는 Git push로 전송하지 않는다. A의 작은 status/SHA와 A 모듈은 지원 범위다. CI에서는 이미 remote에 있는 K blob과 작은 A 모듈로 원본 A를 exact 재생성해 B의 비교 기준으로 쓴다. `docs/harpoon/A/workflow-a.yml`은 준비됐던 A workflow의 역사 보존본이고 실행 workflow는 B다. 역사 A support manifest의 당시 root 경로는 변경하지 않는다. 현재 repository 검사는 B manifest를 따른다.

B workflow는 static 및 runtime/native/salvo/stage를 업로드한 동일 B bytes에서 실행한다. Actions 성공은 이후 원격 실행 결과를 보고 판정하며 로컬 결과를 원격 CI로 쓰지 않는다. 그 뒤 구체적인 PR을 만들고 현재 head의 checks를 확인한다. main 병합과 정식 승격은 새 지시가 있을 때 진행한다. 이전 PR #43 병합 지시는 K 단계에서 완료됐다.

로컬 인계 ZIP에는 최신 B, 동일 blob의 K baseline, 작은 A/B 지원 자료와 A archive의 status/SHA가 있다. 전체 A HTML은 기존 A 인계 ZIP와 로컬 archive에 동일 bytes로 남아 있다. 새 ZIP에서 비교 A는 `python docs/harpoon/A/build.py --out /tmp/harpoon-b/baseline-A.html`로 재생성하고 B는 `--baseline`으로 이를 지정한다. root B SHA와 repository support manifest를 함께 검증한다.
