---
name: competition-setup
description: Bootstrap a new AI/ML competition project in one pass — interview and lock the competition spec, create the branch-based experiment tree (development branches hold a few exps under a per-branch quota, each exp bundles the many runs that answer one question, and branches fork when the work needs a separate line), and write the project rules file (CLAUDE.md) plus reference docs that govern the rest of the competition after this skill is done. Run this once at the start of a Kaggle, DACON, or similar leaderboard competition. This skill only does setup — it does not train models, tune hyperparameters, or debug CV-LB gaps. For modeling itself use ml-modeling or dl-modeling; for mid-competition decisions the generated CLAUDE.md and docs take over.
disable-model-invocation: true
---

# Competition Setup

대회에서 비용이 가장 큰 실패는 모델이 나쁜 것이 아니라 **되돌아가는 것**이다. Validation 설계가 틀렸다는 걸 3주차에 알면 그동안의 실험 기록이 전부 무효가 된다. 제출 형식을 마감 전날 확인하면 순위표에 남는 건 오류 메시지다. 실험 결과를 문서 아래에 계속 덧붙이기만 하면 2주 뒤에 어느 서술이 현재 상태인지 판별할 수 없다.

이 스킬은 대회 **시작 시점에 한 번** 실행되어, 그 되돌아감을 막을 구조를 프로젝트에 심는다.

## 범위

**한다**: 대회 스펙 확정, 디렉토리 생성, 줄기·실험 문서 체계 초기화, 이후 세션이 따를 규칙 파일과 참조 문서 작성.

**하지 않는다**: 모델 학습, fold 생성, 피처 엔지니어링, 하이퍼파라미터 튜닝, CV-LB 갭 진단.

이 스킬은 다시 호출되지 않는다. 세팅 이후 세션의 Claude Code는 이 스킬을 볼 수 없다. 따라서 워크플로 지식을 대화에 남기지 말고 **전부 파일로 내보내야** 한다. 그것이 6단계의 목적이며, 이 스킬의 실질적 산출물은 `CLAUDE.md`다.

또한 대회마다 분야가 다르므로 문서에 들어갈 내용이 크게 달라진다. 템플릿은 유형 무관한 추상 형태로 두고, 5단계에서 이 대회에 맞게 구체화한 뒤 내보낸다.

---

## 1단계 — 대회 스펙 인터뷰

모델링 전에 규칙을 확정한다. 여기서 놓친 항목은 마감 직전에 발견되고, 그때는 대응할 시간이 없다.

아래를 사용자에게 묻는다. 대회 페이지 URL을 받을 수 있으면 받아서 직접 확인하고 결과를 사용자에게 검토받는다. **추정해서 채우지 않는다.** 모르는 항목은 미확인으로 남긴다. 틀린 스펙은 없는 스펙보다 나쁘다.

필수 항목:

1. 대회명, 플랫폼, 과제 유형(테이블 분류/회귀, 이미지, 텍스트, 시계열, 랭킹 등)
2. **평가지표의 정확한 정의.** 이름만으로 판단하지 않는다. RMSE인지 RMSLE인지, F1이 macro/micro/weighted 중 무엇인지, AUC가 ROC인지 PR인지, MAP@K의 K가 몇인지. 공식 문구를 그대로 옮긴다
3. 제출 형식: 컬럼명, 행 수, ID 순서 요구, 확률인지 라벨인지, 인코딩
4. 제출 횟수: 일일 제한, 최종 선택 제출 개수
5. 허용 범위: 외부 데이터, 사전학습 가중치와 라이선스, 코드 공개 의무, 추론 시간·리소스 제한
6. 테스트셋 구조: public/private 비율, private가 다른 기간·분포인지
7. 마감: 팀 병합, 최종 제출, 최종 제출 선택(별도인 경우가 있다)

데이터가 이미 있으면 아래도 확인한다. fold 설계를 좌우하는 정보라 미리 알아두면 첫 실험 세션이 짧아진다. 다만 이건 대회 규정이 아니라 관찰이므로 `EDA.md`에 기록하고, `docs/competition-spec.md`에는 한 줄 요약만 남긴다.

8. 행 단위가 무엇인지, 같은 개체가 여러 행에 걸치는지(사용자·환자·매장·이미지 원본)
9. 시간 컬럼 유무, test가 train보다 미래인지
10. train/test ID 교집합 유무

데이터가 아직 없으면 건너뛴다. `EDA.md`는 빈 템플릿으로 생성되고 첫 세션에서 채워진다.

항목을 하나씩 묻지 말고 묶어서 제시하고, 사용자가 아는 것부터 채운다.

---

## 2단계 — 디렉토리 생성

```bash
mkdir -p data/raw data/processed src exp sub docs
printf 'data/raw/\ndata/processed/\nexp/**/ckpt/\nexp/**/*.npy\nexp/**/*.npz\nexp/**/*.log\nsub/\n__pycache__/\n*.pyc\n' > .gitignore
```

실험 폴더는 줄기 아래로 중첩되므로(`exp/<줄기>/<exp>/<실험>/`) 패턴은 `exp/**/`로 쓴다. `.gitignore`에서 대용량 산출물을 제외하되 `EDA.md`, `exp/**/BRANCH.md`, `exp/**/EXP.md`, `exp/TEMPLATE.md`는 반드시 버전 관리에 포함시킨다. 이 문서들이 기록의 단일 원천이므로 유실되면 복구할 수 없다.

기존 파일이 있는 프로젝트라면 덮어쓰지 말고 현재 구조를 먼저 보여준 뒤 무엇을 이동·생성할지 확인받는다.

---

## 3단계 — 스펙 문서화

`assets/competition-spec.template.md`를 `docs/competition-spec.md`로 복사하고 1단계 내용을 채운다. 미확인 항목은 지우지 말고 `미확인 — 확인 필요`로 남긴다. 빈칸으로 두면 확인했는지 안 했는지 구분되지 않는다.

`assets/EDA.template.md`를 프로젝트 루트에 `EDA.md`로 복사한다. 1단계 8~10번을 확인했으면 대응하는 `###` 슬롯을 채우고, 확인하지 못했으면 빈 상태로 둔다. 관측값 없이 `확인 예정` 같은 문구로 채우지 않는다.

템플릿의 `##` 범주는 테이블 데이터 기준이다. 1단계에서 확인한 과제 유형에 맞게 조정한다 — 시계열이면 정상성·계절성, 이미지면 해상도·클래스별 샘플 수를 추가하고, 해당 없는 범주는 지운다. 범주 이름은 관찰 대상을 가리켜야 하며 시점을 가리키는 이름을 쓰지 않는다.

지표 구현은 이 스킬의 범위 밖이지만, 첫 세션이 바로 이어받을 수 있도록 스텁을 만든다.

```python
# src/metric.py
def competition_metric(y_true, y_pred):
    """<공식 지표명>. docs/competition-spec.md의 정의를 따른다.

    검증: 완전 예측(y_pred=y_true)과 상수 예측(전체 평균 또는 다수 클래스)에
    대해 손으로 계산한 값과 일치하는지 확인한 뒤 사용한다.
    이 검증 전까지 CV 점수는 신뢰하지 않는다.
    """
    raise NotImplementedError
```

실험은 번호 없이 `exp/<줄기>/<exp>/<실험>/` 경로로 가리킨다. 코드와 config가 같은 방식으로 경로를 다루도록 해석기를 함께 만든다.

```python
# src/paths.py
import re
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent / 'exp'
NAME = re.compile(r'[a-z0-9][a-z0-9-]*')        # 줄기·exp·실험 이름: 짧은 소문자와 하이픈
TIMEWORD = re.compile(r'(^|-)(v\d+|new|old|tmp|final)(-|$)')   # 시점·순번 이름


def run_dir(ref: str) -> Path:
    """'<줄기>/.../<exp>/<실험>' 경로(exp/ 아래)를 실험 폴더로 바꾼다.

    config와 코드는 실험을 이 경로로 가리킨다. 번호를 쓰지 않으므로 경로가 곧 이름이다.
    """
    path = EXP / ref.removeprefix('exp/').strip('/')
    if not path.is_dir() or not (path.parent / 'EXP.md').exists():
        raise FileNotFoundError(f'{ref}: 실험 폴더가 없다 (exp/<줄기>/<exp>/<실험>)')
    return path


def _check_name(name: str) -> None:
    if not NAME.fullmatch(name) or TIMEWORD.search(name):
        raise ValueError(f'{name}: 이름은 짧은 소문자·하이픈이고, 시점·순번(v2, new, old, final)을 쓰지 않는다')


def new_exp_dir(branch: str, name: str) -> Path:
    """줄기 아래에 새 exp 폴더를 만든다. branch는 exp/ 아래 경로('stack', 'stack/nested').
    EXP.md 머리말(시작·구성·대조·조건)은 만든 쪽이 바로 쓴다 (CLAUDE.md `기록`)."""
    _check_name(name)
    root = EXP / branch
    if not (root / 'BRANCH.md').exists():
        raise FileNotFoundError(f'{branch}: 줄기 문서가 없다. 줄기를 먼저 연다 (CLAUDE.md `줄기 · exp · 실험`)')
    path = root / name
    path.mkdir()          # 이미 있으면 FileExistsError — 같은 이름이면 그 exp의 실험이 아닌지 먼저 본다
    return path


def new_run_dir(ref: str) -> Path:
    """'<exp 경로>/<실험>' 실험 폴더를 그 exp 안에 만든다."""
    exp_path, _, run = ref.removeprefix('exp/').strip('/').rpartition('/')
    _check_name(run)
    root = EXP / exp_path
    if not (root / 'EXP.md').exists():
        raise FileNotFoundError(f'{exp_path}: EXP.md가 없다. exp 머리말을 먼저 쓴다')
    path = root / run
    path.mkdir()          # 이미 있으면 FileExistsError — 같은 이름을 다시 쓰지 않는다
    return path
```

---

## 4단계 — 줄기 생성

### 최상위 줄기 후보

1단계에서 확인한 과제 유형과 데이터 구조에 근거해 최상위 줄기(대략적인 모델 구조) 후보 **2~3개**를 제안하고 사용자가 고르게 한다. 임의로 정하지 않는다.

후보는 서로 **입력 표현이나 모델 구조가 다른 것**으로 구성한다. 하이퍼파라미터나 피처 몇 개 차이는 별도 줄기가 아니라 같은 줄기의 exp다. 이 구분을 세팅 시점에 잘못 잡으면 이후 줄기가 불필요하게 늘어난다.

과제 유형별 예시:

- 테이블: 단일 GBDT / 선형·정규화 모델 / 신경망(임베딩 기반). 멤버가 모이면 이들을 결합하는 스택 줄기가 따로 생긴다
- 이미지: 사전학습 CNN 파인튜닝 / ViT 계열 / 도메인 특화 전처리 + 경량 모델
- 텍스트: 사전학습 트랜스포머 파인튜닝 / 임베딩 + GBDT / 규칙·통계 피처 기반
- 시계열: 통계 모델 / lag 피처 + GBDT / 시퀀스 모델

### 줄기 · exp · 실험

실험 기록과 산출물은 모델 구조를 따라 나뉜다. 규칙 전체는 `CLAUDE.md` `줄기 · exp · 실험`과 `정원과 보관` 절에 있다. 아래 설명은 예시이고, 무엇을 줄기·exp·실험으로 나눌지는 사용자가 명시하면 그대로, 아니면 대회 중에 판단한다.

| 단위 | 위치 | 무엇인가 (예) |
|---|---|---|
| 줄기 | `exp/<줄기>/BRANCH.md` | 대략적인 모델 구조. 예: 3단계 스택, 단일 GBDT, CNN 파인튜닝. `구조` 절에 그 구조를, `상태` 절에 머리·대조·진행중을 둔다. 갈라지는 이유가 생기면 하위 디렉토리가 하위 줄기가 된다 |
| exp | `exp/<줄기>/<exp>/EXP.md` | 그 구조를 구체적으로 어떻게 채울지. 예: 어떤 모델을 넣고(스택이면 1단계 멤버), 어떤 피처를 쓰는지. 폴더 이름이 무엇을 하는지 말한다 |
| 실험 | `exp/<줄기>/<exp>/<실험>/` | 그 exp 안에서 돌린 것. 예: 멤버 학습, 멤버·피처 넣고 빼기, 메타 교체, 후처리·refit, 진단 |

이렇게 나누는 이유는 실험마다 번호를 주고 폴더를 만들면 폴더가 수백 개로 불어나기 때문이다. 단조 증가 번호는 "새 번호 = 새 실험"이라 하나 더 만드는 비용이 없다. 그러면 지금 무엇이 살아 있는지, 같은 구성에서 무엇을 시도했는지가 보이지 않는다. 번호 대신 무엇을 하는지 말하는 이름을 쓰면, 만들기 전에 "이미 있는 것의 일부인가"를 먼저 보게 된다. 줄기마다 **exp 정원**(머리 1·대조 1·진행중 최대 4)을 두면 판정이 밀리지 않는다. 정원은 남길 수 있는 것의 상한이 아니다. 나중에 다시 볼 이유가 있는 exp는 `보관:`으로, 줄기는 `보존 — <이유>`로 남긴다.

기록을 실험 축(무엇을 바꿨는지)으로 나누지 않는 이유도 있다. 그렇게 하면 대회 후반에 결합·스태킹 실험이 한 축 파일에 몰려, 파일을 열어도 지금 살아 있는 것이 보이지 않는다. 축은 실험 항목의 `축` 필드로 남겨 검색에 쓴다(아래 `축 목록`).

고른 후보마다 **최상위 줄기 하나**를 만든다. 이름은 그 줄기의 모델 구조를 가리킨다(`stack`, `gbdt-single`, `cnn-finetune`). 시점이나 순번(`v1`, `base`, `new`)을 이름에 쓰지 않는다. 이름을 제안하고 사용자가 확정하게 한다.

```bash
cp <skill_dir>/assets/experiment-log.template.md exp/TEMPLATE.md
mkdir -p exp/<줄기>
```

`TEMPLATE.md`는 형식 참조용이므로 5단계에서 이 대회에 맞게 확정한 뒤 그대로 둔다. 각 줄기 문서는 **템플릿을 복사하지 않고 새로 쓴다.** `구조` 절에는 1단계에서 확인한 과제와 사용자와 고른 후보로 그 줄기의 모델 구조와 왜 이 구조로 가는지를 적는다. 다음 세션이 이 절만 읽고도 무엇을 어떤 순서로 결합하는 모델인지 알 수 있어야 한다. `다음 후보`에는 세팅 대화에서 나온 첫 시도들을 적는다.

```markdown
# gbdt-single

GBDT 한 모델로 예측하는 구조. 규칙은 `CLAUDE.md`, 형식은 `exp/TEMPLATE.md`.

## 구조

원본 피처(필요하면 파생 피처)를 GBDT 하나에 넣어 확률을 낸다. 결합 단계는 없다. fold별 모델의 OOF로 검증하고, test는 전체 train으로 다시 학습한 모델로 예측한다. 테이블 이진분류에서 가장 먼저 세우는 기준 구조로, 첫 (검증 점수, LB) 쌍과 변동폭을 여기서 얻는다.

## 상태

- 갈라진 곳: 없음
- 상태: 작업
- 머리: 없음
- 대조: 없음
- 진행중: 없음
- 변동폭: 미측정

## 다음 후보

- [ ] 원본 피처 LightGBM 기준선 (수 분 / 첫 제출과 변동폭 측정)
```

규칙을 줄기 문서마다 재서술하지 않는다. 줄기가 늘어날 때마다 같은 설명이 깔리고, `CLAUDE.md`가 바뀌었을 때 전부 낡는다.

세팅 시점에는 하위 줄기도 exp도 만들지 않는다. 줄기가 쪼개질 이유와 exp의 구성은 실험을 해 봐야 생긴다. 스택처럼 여러 모델을 결합하는 구조는 단일 모델 줄기에서 멤버가 모인 뒤에 줄기로 연다. `CLAUDE.md`에 적힌 갈라지는 이유(비교 조건 변화, 최종 제출에서의 다른 역할, 같은 머리에서 두 방향)는 예시이며, 그 밖의 이유로도 가를 수 있다.

### 축 목록

무엇을 바꿨는지의 종류(**축**)는 파일이 아니라 실험 항목의 `축` 필드로 남긴다. 줄기를 가로질러 "이 축은 이미 해봤는가"를 `grep -rn "축: feature" exp/ --include=EXP.md`로 찾는 데 쓴다. 축 문자열이 제각각이면 이 검색이 안 되므로, 쓸 수 있는 값을 `exp/TEMPLATE.md`의 `축 목록`에 고정한다.

과제 유형에 맞게 축 목록을 제안하고 사용자가 확정하게 한다. 아래는 출발점이며 전부 쓸 필요도, 여기 없는 축을 못 쓸 이유도 없다:

- 공통: `data`(정제·분할), `feature`(입력 표현), `model`(구조·크기), `objective`(손실·타깃 변환), `training`(최적화·스케줄), `ensemble`
- 테이블 추가: `encoding`
- 이미지 추가: `augmentation`, `resolution`, `backbone`
- 텍스트 추가: `tokenization`, `context-length`

축을 나누는 기준은 **재조회 단위**다. "이 실험을 나중에 다시 찾을 때 무엇으로 검색할 것인가"로 나눈다. 축은 파일이 아니라 값이므로 늘리는 비용이 작다. 세팅 시점에 떠오르는 축을 넉넉히 넣는다. 목록을 확정하기 전에 빠진 축이 없는지 사용자에게 확인받는다.

## 5단계 — 문서 형식 구체화

`assets/`의 템플릿은 과제 유형에 무관한 추상 형태다. 그대로 복사하면 실제 기록 시점마다 형식이 재발명되어 앞뒤 실험을 비교할 수 없게 된다. **1단계에서 확인한 정보로 형식을 확정한 뒤 내보낸다.**

확정할 대상:

| 대상 | 확정 내용 | 예 |
|---|---|---|
| 분할 산출물 | 파일명과 형태 | `folds.npy` (5-fold 인덱스) / `split.json` (촬영 세션 단위 holdout) |
| 변동폭 정의 | 무엇의 표준편차인가 | 5-fold 평균의 시드 간 표준편차 / 동일 설정 3-run의 표준편차 |
| 판단 재료 | `결과` 필드에서 세 신호가 읽히는가 | fold별·run별 개별 점수를 남기는 형식인지 |
| exp 구성 줄 | `exp/TEMPLATE.md` exp 머리말의 구성 줄(`모델`·`피처`·`결합`) 이름과 적을 것. 과제 유형에 맞게 바꾼다 | 테이블 스택: 1단계 멤버 / 피처 그룹 / 메타 · 이미지: 백본 / 해상도·증강 / TTA·앙상블 |
| 실험 필드 | `exp/TEMPLATE.md`의 실험 항목 필드와 각 필드에 적을 것. 모델 구조는 줄기 문서가, 구성·대조·조건은 exp 머리말이 가지므로 실험 항목에는 축·바꾼 것·결과·가설·해석만 둔다 | `결과: CV ± std · fold별 [...]` / `결과: val mAP@0.5 ± std · run별 [...] · best epoch` |
| 축 목록 | `exp/TEMPLATE.md`의 `축 목록` — 실험 항목 `축` 필드에 쓸 값 | `feature`, `encoding`, `ensemble` / `augmentation`, `backbone` |
| 산출물 파일명 | 실험 폴더 `exp/<줄기>/<exp>/<실험>/` 안의 파일. 정리 정책의 `DROP` 확장자와 맞춘다 | `oof.npy`, `pred.npy` / `val_pred.npz`, `test_pred.npz` |

**변동폭은 세팅 시점에 확정하지 못할 수 있다.** 학습 1회에 얼마나 걸리는지 모르는 상태에서 "3-run 표준편차"로 정해두면, 나중에 1 run이 6시간이라는 걸 알게 됐을 때 측정 자체를 안 하게 된다. 측정하지 않으면 판정 신호 하나가 통째로 빠진다.

이 경우 값을 강제로 정하지 말고 **결정 규칙**을 적는다. 예: "첫 학습 후 1 run 소요 시간을 재고, 1시간 미만이면 3-run 표준편차, 이상이면 fold 간 표준편차를 대용으로 쓴다." `{{VARIATION}}`에 이 규칙을 넣고 첫 세션이 확정하게 한다.

fold 간 표준편차를 대용으로 쓸 때의 한계도 함께 적는다 — 데이터 분할 차이는 반영하지만 학습 자체의 무작위성은 반영하지 않아 실제 변동폭보다 작게 나올 수 있다.

확정안을 사용자에게 제시하고 검토받는다. 임의로 정하지 않는다.

확정한 실험 필드가 아래 다섯 조건을 만족하는지 자체 점검하고, 미충족 항목이 있으면 무엇이 부족한지 보고한다.

1. **비교 가능성** — 두 실험의 결과를 나란히 놓고 우열을 판정할 수 있는가
2. **판단 재료** — 세 신호(개선폭 대 변동폭, 일관성, 분산 변화)가 `결과` 필드에서 모두 읽히는가
3. **재현 정보** — 그 수치를 다시 만들 수 있는 정보가 있는가
4. **대조 명시** — 무엇에서 무엇을 바꿨는지 한 줄로 읽히는가
5. **해석** — 왜 그렇게 나왔는지에 대한 판단이 들어갈 자리가 있는가

2번이 특히 중요하다. 판정은 세션 종료 시 여러 실험을 모아 사용자와 함께 하는데, 그때 재실행 없이 판단하려면 기록에 신호가 남아 있어야 한다. 평균만 적는 형식으로 확정하면 일관성과 분산 변화를 볼 수 없다. **fold별 또는 run별 개별 점수가 남는 형식이어야 한다.**

확정한 필드 형식을 `exp/TEMPLATE.md`에 반영하고, 예시도 이 대회의 지표와 검증 방식으로 바꿔 쓴다. 템플릿에 남아 있는 다른 유형의 예시는 지운다.

줄기 문서에는 형식을 재서술하지 않는다. 모든 줄기가 `TEMPLATE.md`의 형식 하나를 따른다 — 줄기마다 형식이 다르면 줄기를 가로지르는 비교와 검색이 안 된다.

정리 정책(`docs/cleanup-policy.md`)은 실험 디렉토리에서 `DROP` 확장자(기본 `.npy`·`.npz`·`.log`)와 `ckpt/`만 산출물로 지운다. 이 대회의 예측·모델 파일 확장자가 다르면 복사한 뒤 `DROP`을 맞춘다. `config.yaml`처럼 다시 만드는 데 필요한 파일이 `DROP`에 들지 않는지도 확인한다.

`docs/`로 복사되는 참조 문서(`validation-design.md`, `cv-lb-diagnosis.md`)는 **전 유형 내용을 그대로** 복사한다. 대회 도중 접근이 바뀔 수 있고, 그때 필요한 내용이 문서에 있어야 한다.

---

## 6단계 — 규칙 내보내기

**복사할 파일** — `assets/`에서 그대로 복사한다. 요약하거나 줄이지 않는다. 이 문서들은 필요한 시점(fold 설계 시, 갭 발생 시, 정리 시)에 읽히도록 설계되어 있다.

```bash
cp <skill_dir>/assets/validation-design.md  docs/
cp <skill_dir>/assets/cv-lb-diagnosis.md    docs/
cp <skill_dir>/assets/cleanup-policy.md     docs/
```

**생성할 파일** — `assets/CLAUDE.md.template`를 프로젝트 루트에 `CLAUDE.md`로 복사하고 자리표시자를 치환한다.

| 자리표시자 | 값 |
|---|---|
| `{{COMP_NAME}}` | 대회명 |
| `{{PLATFORM}}` | 플랫폼 |
| `{{METRIC}}` | 지표명 (상세는 docs 참조로 두므로 한 줄) |
| `{{SUB_LIMIT}}` | 제출 제한 |
| `{{DEADLINE}}` | 최종 제출 마감 |
| `{{EXTERNAL_DATA}}` | 외부 데이터·사전학습 허용 여부 |
| `{{OPEN_ITEMS}}` | 1단계에서 확인하지 못한 항목 목록 |
| `{{SPLIT_ARTIFACT}}` | 5단계에서 확정한 분할 산출물 파일명 |
| `{{VARIATION}}` | 5단계에서 확정한 변동폭 정의 |
| `{{ARTIFACT_FILES}}` | 5단계에서 확정한 산출물 파일명 목록 |

치환하지 못한 자리표시자가 남아 있으면 안 된다. 값이 없으면 `미확인`으로 채운다.

줄기는 대회 도중 자주 열고 닫으므로 `CLAUDE.md` 하단 mermaid 다이어그램에 개별 줄기를 넣지 않는다(`EXP` 아래는 `<줄기>/` 일반형 그대로 둔다). 다이어그램은 Mermaid 문법으로 직접 작성하며, 외부 도구나 커넥터를 호출하지 않는다.

`CLAUDE.md`는 Claude Code가 이후 세션마다 자동으로 읽는 파일이므로 이 스킬의 규칙을 지속시키는 유일한 경로다. 길게 만들지 않는다. 규칙과 포인터만 두고 상세는 `docs/`에 맡긴다.

---

## 7단계 — 완료 보고

사용자에게 아래를 제시한다.

1. 생성된 파일 목록
2. **미확인 항목 목록.** 사용자가 대회 페이지에서 확인해야 할 것들. 이게 가장 중요한 출력이다
3. 다음 세션의 첫 세 작업, 순서를 바꾸지 않도록 강조한다
   - `src/metric.py` 구현 및 상수 예측으로 검증
   - `docs/validation-design.md` 0절의 관측 항목을 `EDA.md`에 채운 뒤 split 전략 결정 → 분할 산출물 생성·고정 → 변동폭 측정
   - 최소 베이스라인 학습 후 **실제 제출**하여 (검증 점수, LB) 첫 쌍 확보

분할을 고정하기 전에 실험을 시작하면 그 실험들은 나중에 비교 대상이 되지 못한다.

---

## 참고

`assets/`의 문서들은 이 스킬이 읽을 참조가 아니라 **프로젝트로 복사될 산출물**이다. 다만 5단계에서 형식을 구체화해야 하므로 `experiment-log.template.md`는 읽는다. `docs/`로 가는 참조 문서 세 개는 그대로 복사한다. 사용자가 내용을 물으면 그때 해당 파일을 읽고 답한다.
