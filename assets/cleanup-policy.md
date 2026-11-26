# 정리 정책

세션 종료 시 수행한다.

목적은 디스크 절약이 아니라 **다음 판단을 흐리지 않는 것**이다. 어떤 산출물이 유효한 결과인지 판단하는 데 시간이 들고, 그 판단이 틀리면 잘못된 실험을 앙상블에 넣는다.

판정 값은 `exp/<축>.md` 항목 제목에 있다. `기준` / `채택` / `보류(유망)` / `보류(중립)` / `보류(불리)` / `기각` / `진행중`.

**삭제 기준은 판정이 아니라 의존이다.** 실험 디렉토리 `exp/<exp_id>/`는 지금 무엇이 그것을 쓰는지로 남길지 정한다. 판정(`기각`/`보류`/`채택` 등)은 그 방향이 효과 있었는지의 기록이고, 삭제 여부와 연결하지 않는다.

판정과 보관을 한 값에 묶으면 둘 다 망가진다. 기각하면 산출물이 지워지니 기각의 문턱이 높아지고, 효과 없는 실험이 전부 `보류`에 쌓여 디렉토리가 줄지 않는다. 쓰이지 않는 디렉토리가 쌓이면 어느 것이 유효한지 판단하는 비용이 커진다 — 이 정책의 목적과 반대다.

실험의 내용은 지워지지 않는다. 결과와 해석은 `exp/<축>.md` 항목에 있고, 디렉토리 안의 추적 파일(`config.yaml`, `metrics.json`, `curves.png`, `importance.csv` 등)은 git 이력에 남는다. 지우면 사라지는 것은 추적하지 않는 예측(`*.npy`)·곡선 원자료(`*.npz`)·로그·체크포인트뿐이고, 필요해지면 git 이력의 `config.yaml`로 다시 만든다.

## 보존 정책

| 대상 | 보존 | 삭제 |
|---|---|---|
| `EDA.md`, `exp/*.md`(축 파일), `pipelines/*.md` | 전부 영구 보존 | 삭제 금지 |
| `exp/<exp_id>/` 디렉토리 | 쓰이는 실험 (아래 정의) | 어디에도 쓰이지 않는 실험의 디렉토리 전체. 추적 파일은 git 이력에 남는다 |
| `ckpt/` | 쓰이는 실험의 best 1개 + last 1개 | 나머지 epoch 체크포인트 |
| `sub/*.csv` | 제출한 것, 줄기 머리의 것 | 제출하지 않은 것 전부. 실험 디렉토리를 지운 실험의 것도 포함한다 (절차 3) |
| `data/processed/` | 재생성 스크립트가 있으면 최신만 | 중간 산출물 |

**쓰이는 실험**은 살아 있는 줄기에서 정한다. 개발은 한 줄로만 가지 않는다. git branch처럼 여러 줄기가 동시에 살아 있을 수 있다 — 채택된 구조를 비교 기준으로 세워 둔 채 그 위에 멤버를 쌓는 줄기를 키우고, 합성 흔적 피처 없이 가는 줄기를 최종 제출의 짝으로 남겨 두는 식이다. `pipelines/*.md` `현재 상태`의 `줄기:` 줄이 각 줄기의 머리(그 줄기의 최신 실험)와 상태를 적는다.

| 머리 상태 | 뜻 | 남기는 디렉토리 |
|---|---|---|
| `작업` | 다음 실험이 이 머리를 확장하거나 다시 만든다 | 머리, 그리고 머리의 `config.yaml`이 가리키는 실험을 끝까지 따라간 전부(앙상블·스태킹의 `members`, 다른 실험의 파일을 읽는 키 `feature_keep.from` 등) |
| `고정` | 결과만 쓴다 — 비교 기준으로 세운 채택 구조, 제출해 둔 최종 후보 | 머리 디렉토리만. 머리의 `oof.npy`·`pred.npy`·`metrics.json`이면 비교와 최종 선택에 충분하다 |

여기에 두 가지를 더한다.

- `기준:` 줄의 실험 — 디렉토리만
- 판정 전 실험(`진행중`, `진행중(멤버)`) — `작업` 머리처럼 참조를 끝까지 남긴다. 판정하면서 다시 분석할 수 있다

`고정` 머리의 멤버는 `작업` 머리나 판정 전 실험이 함께 쓸 때만 남는다. 그래서 줄기가 여럿이면, 고정 줄기만 쓰던 멤버(채택 구조에는 들어 있지만 작업 줄기에서는 뺀 멤버)는 지워진다. 고정 머리를 다시 키우려면 `작업`으로 바꾸고, 지워진 멤버를 git 이력의 config로 다시 만든다. 머리를 `고정`으로 둘지는 그 줄기를 다시 확장할 가능성과 멤버 재학습 비용을 비교해 사용자와 정한다.

이 집합 밖이면 판정과 무관하게 지운다. `채택`이어도 대체된 옛 구조는 지우고, `보류(유망)`도 지금 쓰이지 않으면 지운다. 다시 볼 때는 축 파일의 기록을 읽고 git 이력에서 config를 꺼내 재실행한다.

남길 디렉토리를 판정 대신 `줄기:` 줄로 정하므로, 이 줄이 낡은 채 정리하면 필요한 디렉토리가 지워진다. 줄기를 열고 닫거나 머리가 바뀔 때 바로 고치고, 정리 전에 한 번 더 본다. 아래 스크립트는 `줄기:`·`기준:`에 적혔는데 디렉토리가 없는 실험도 알려 준다 — 이미 지워진 실험을 머리로 가리키고 있다는 뜻이다.

## 절차

md 표·제목 파싱은 취약하다. **자동 삭제하지 않고 후보 목록을 만들어 사용자 확인을 받는다.** 유효한 산출물을 파싱 오류로 지우는 것이 정리를 안 하는 것보다 나쁘다.

### 1. 실험 문서에 기록되지 않은 디렉토리 탐지

기록 없이 만들어진 실험을 찾는다. 이런 디렉토리는 기록 규칙이 지켜지지 않았다는 신호다.

```bash
python - <<'EOF'
import re, glob, os
logged = set()
for f in [x for x in glob.glob('exp/*.md') if not x.endswith('TEMPLATE.md')]:
    for line in open(f):
        m = re.match(r'^## `([^`]+)`', line)
        if m:
            logged.add(m.group(1))
dirs = {d for d in os.listdir('exp') if os.path.isdir(f'exp/{d}')}
missing = sorted(dirs - logged)
print('기록 없는 실험 디렉토리:', missing or '없음')
EOF
```

결과가 있으면 삭제 전에 `metrics.json`을 읽어 실험 문서에 소급 기록할 수 있는지 먼저 확인한다. 유효한 실험을 기록 누락 때문에 버리는 것이 가장 큰 손실이다.

### 2. 쓰이지 않는 실험 디렉토리 목록 생성

```bash
python - <<'EOF'
import re, glob, os
ID = re.compile(r'\b(\d{3}-[a-z0-9-]+)')
HEAD = re.compile(r'`(\d{3}-[a-z0-9-]+)`\s*\((작업|고정)')
exps = {d for d in os.listdir('exp') if os.path.isdir(f'exp/{d}')}
roots, frozen = set(), set()  # roots: 참조를 끝까지 따라간다 / frozen: 디렉토리만 남긴다
for f in [x for x in glob.glob('pipelines/*.md') if not x.endswith('TEMPLATE.md')]:
    sec = None
    for line in open(f, encoding='utf-8'):
        if line.startswith('## '):
            sec = line.strip()
        elif sec == '## 현재 상태' and line.startswith('- 줄기:'):
            for e, state in HEAD.findall(line):
                (roots if state == '작업' else frozen).add(e)
        elif sec == '## 현재 상태' and line.startswith('- 기준:'):
            frozen |= set(ID.findall(line))
logged = set()
for f in [x for x in glob.glob('exp/*.md') if not x.endswith('TEMPLATE.md')]:
    for line in open(f, encoding='utf-8'):
        m = re.match(r'^## `([^`]+)`', line)
        if m:
            logged.add(m.group(1))
        m = re.match(r'^## `([^`]+)`.*·\s*진행중', line)
        if m:
            roots.add(m.group(1))
gone = sorted((roots | frozen) - exps)
used, stack = roots & exps, list(roots & exps)
while stack:  # config.yaml에 적힌 exp_id(members, feature_keep.from 등)를 따라간다
    p = f'exp/{stack.pop()}/config.yaml'
    if os.path.exists(p):
        text = '\n'.join(l.split('#')[0] for l in open(p, encoding='utf-8'))  # 주석의 exp_id는 의존이 아니다
        for r in set(ID.findall(text)) & exps - used:
            used.add(r)
            stack.append(r)
used |= frozen & exps
unlogged = sorted(exps - logged)  # 기록 전: 다른 세션이 지금 만드는 중일 수 있다. 지우지 않는다
unused = sorted(exps - used - set(unlogged))
total = 0
for e in unused:
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(f'exp/{e}') for f in fs) / 1e6
    total += size
    print(f'{size:7.1f} MB  exp/{e}')
print(f'작업 머리·판정 전 {len(roots)}개 · 고정 머리·기준 {len(frozen)}개 · 남길 디렉토리 {len(used)}개')
print(f'쓰이지 않는 실험 {len(unused)}개 · 합계 {total:.1f} MB')
if gone:
    print('줄기·기준에 적혔는데 디렉토리가 없음:', gone)
if unlogged:
    print('기록 전이라 후보에서 뺀 디렉토리:', unlogged)
EOF
```

출력된 목록을 사용자에게 보여주고 확인받은 뒤 지운다. 축 파일에 아직 기록되지 않은 디렉토리는 후보에서 빠진다 — 여러 세션이 동시에 일하면 다른 세션이 실험을 돌리는 중이라 기록 전일 수 있다. 이런 디렉토리는 1절(기록 누락 탐지)로 따로 다루고, 만든 세션이 끝났는지 확인하기 전에는 지우지 않는다. 추적 파일은 `git rm -r exp/<exp_id>`로, 남은 비추적 파일은 디렉토리째 지운다. 지운 실험을 되살릴 때는 `git checkout $(git rev-list -n 1 HEAD -- exp/<exp_id>/config.yaml)^ -- exp/<exp_id>`로 추적 파일을 꺼내고 그 config로 다시 실행한다.

### 2-1. 판정 세션

세션 종료는 판정을 모아서 하기 좋은 시점이다. 실험 직후에는 `진행중`으로만 기록되므로 여기서 확정한다.

판정 세션은 세션 종료 외에 **`진행중`이 5개 이상일 때 새 실험을 시작하기 전에도** 열린다. `CLAUDE.md`의 `실험을 시작하기 전` 참조. 대회 후반에는 제출도 정리도 강제성이 없어져 판정이 밀리므로, 실험 시작이라는 확실히 오는 시점을 트리거로 함께 쓴다.

```bash
grep -Hn "^## .*진행중" $(ls exp/*.md | grep -v TEMPLATE)
grep -Hn "^## .*보류" $(ls exp/*.md | grep -v TEMPLATE)
```

`진행중` 항목마다 세 신호가 어느 방향인지, 엇갈린다면 어디서 엇갈리는지, 판정을 가를 축과 그 비용을 정리해 사용자에게 제시하고 결정을 받는다. 신호가 명백히 한쪽인 항목만 단독으로 판정하고, 그 경우에도 무엇을 근거로 그렇게 판정했는지 함께 보고한다.

`보류` 항목은 **방향별로 묶어 전부 제시한다.** `유망`만 보여주면 `불리`가 시야에서 사라져 사실상 기각과 같아진다. 디렉토리가 있든 없든 다시 보지 않게 되는 것이 실제 손실이다.

```
보류(유망)  3건 — 재판정 값어치 큼
보류(중립)  7건
보류(불리)  4건 — 재시도 조건이 적힌 것이 있는지 확인
```

`보류`가 많은 것 자체는 정상이다. 기각 조건이 좁으므로 대부분의 실험이 여기 머문다. 삭제가 판정과 분리돼 있으므로 보류가 많아도 디렉토리는 쌓이지 않는다. 다만 `보류(유망)`이 여러 개 쌓여 있으면 다음 실험을 늘리기보다 그중 하나를 해소하는 편이 낫다는 것을 알린다.

### 3. 제출하지 않은 제출 파일 목록 생성

학습·결합 코드는 실험마다 `sub/<exp_id>.csv`를 쓰지만 실제로 제출하는 것은 그중 일부다. **제출하지 않은 CSV는 남기지 않는다.** `exp/<exp_id>/pred.npy`와 같은 내용이라 따로 둘 이유가 없고, 쌓이면 어느 파일이 제출한 것인지 가려내는 비용만 생긴다. 실험 디렉토리를 이미 지운 실험의 CSV도 같이 지운다 — 쓰이지 않아 정리한 실험의 test 예측만 따로 보관할 이유가 없다.

남기는 것은 셋이다.

- 제출한 실험 — 축 파일 항목의 `결과` 필드에 LB 점수가 적힌 것. `pipelines/`의 `현재 상태`에 `LB:` 줄을 두었으면 거기 적힌 것도 포함한다
- 줄기 머리 — 아직 제출하지 않았어도 곧 제출할 수 있는 후보다
- 축 파일에 아직 기록되지 않은 실험 — 다른 세션이 만드는 중일 수 있다 (1절과 같은 이유)

```bash
python - <<'EOF'
import re, glob, os
HEAD = re.compile(r'`(\d{3}-[a-z0-9-]+)`\s*\((작업|고정)')
ID = re.compile(r'\b(\d{3}-[a-z0-9-]+)')
keep, logged, cur = set(), set(), None
for f in [x for x in glob.glob('exp/*.md') if not x.endswith('TEMPLATE.md')]:
    for line in open(f, encoding='utf-8'):
        m = re.match(r'^## `([^`]+)`', line)
        if m:
            cur = m.group(1)
            logged.add(cur)
        elif cur and line.startswith('- 결과:') and re.search(r'LB\s*[0-9]', line):
            keep.add(cur)  # 결과에 LB 점수가 적힌 실험 = 제출한 실험
for f in [x for x in glob.glob('pipelines/*.md') if not x.endswith('TEMPLATE.md')]:
    sec = None
    for line in open(f, encoding='utf-8'):
        if line.startswith('## '):
            sec = line.strip()
        elif sec == '## 현재 상태' and line.startswith('- 줄기:'):
            keep |= {e for e, _ in HEAD.findall(line)}
        elif sec == '## 현재 상태' and line.startswith('- LB:'):
            keep |= set(ID.findall(line))
files = sorted(os.path.splitext(f)[0] for f in os.listdir('sub') if f.endswith('.csv'))
unlogged = [e for e in files if e not in logged]
cand = [e for e in files if e not in keep and e in logged]
total = 0
for e in cand:
    size = os.path.getsize(f'sub/{e}.csv') / 1e6
    total += size
    note = 'pred.npy 있음' if os.path.exists(f'exp/{e}/pred.npy') else 'pred.npy 없음 — 다시 만들려면 재학습'
    print(f'{size:6.1f} MB  sub/{e}.csv  ({note})')
print(f'남길 파일 {len(files) - len(cand)}개 · 제출하지 않은 파일 {len(cand)}개 · 합계 {total:.1f} MB')
print('남기는 것:', [e for e in files if e in keep])
if unlogged:
    print('기록 전이라 후보에서 뺀 파일:', unlogged)
EOF
```

출력된 목록을 사용자에게 보여주고 확인받은 뒤 지운다. `sub/`는 git이 추적하지 않으므로 지우면 파일은 돌아오지 않는다. 다시 필요해지면 `exp/<exp_id>/pred.npy`와 test id로 다시 쓰고, `pred.npy`도 없으면 git 이력의 `config.yaml`로 다시 학습한다.

이 절차는 제출이 기록돼 있다는 전제로 돈다. 제출하고도 `결과` 필드에 LB 점수를 적지 않은 실험은 제출하지 않은 것으로 잡히므로, `남기는 것` 목록이 기억하는 제출과 맞는지 먼저 본다. 맞지 않으면 지우기 전에 축 파일부터 고친다.

### 4. 계약 밖 파일 탐지

```bash
find . -maxdepth 2 -name '*.csv' -not -path './sub/*' -not -path './data/*'
find . \( -name '*final*' -o -name '*copy*' -o -name '*_v[0-9]*' -o -name '*수정*' \) \
     -not -path './.git/*'
```

여기서 걸린 파일도 삭제 전에 목록을 보여주고 확인받는다. 사용자가 의도적으로 만든 파일일 수 있다.

### 5. 헤딩 규약 점검

헤딩이 주소 단위이므로 헤딩만 훑으면 구조 이탈이 드러난다. 개수로 판정하지 않는다. `EDA.md`의 범주는 데이터에 따라 달라지므로 개수 기준선을 두면 정당한 조정까지 위반으로 잡힌다.

**시점 기반 헤딩 탐지** — 언제 썼는지를 가리키는 이름은 예외 없이 위반이다.

```bash
grep -n "^#\{2,3\} .*\(요약\|현황\|총평\|변경\|추가 분석\|업데이트\|[0-9]차\|재검토\|기타\)" \
     EDA.md exp/*.md pipelines/*.md
```

**스키마 이탈 탐지** — `pipelines/`는 다섯 개 이름이 고정이고, `pipelines/`·`exp/`는 `###`을 쓰지 않는다.

```bash
for f in pipelines/*.md; do
  [ "$(basename $f)" = TEMPLATE.md ] && continue
  echo "--- $f"
  diff <(grep '^## ' $f) <(printf '## 목적·가설\n## 입력 표현\n## 모델\n## 현재 상태\n## 다음 후보\n')
  grep -n '^### ' $f
done
for f in exp/*.md; do
  [ "$(basename $f)" = TEMPLATE.md ] && continue
  grep -Hn '^### ' $f
done
```

`diff` 출력이나 `###` 검출이 있으면 위반이다. `exp/`에서 `###`이 나오면 실험 항목 안에 하위 서술이 자란 것이므로 확정된 필드로 압축하거나 별도 실험으로 분리한다.

**중복 범주·축 탐지** — `EDA.md`의 헤딩 목록과 문서 파일 목록을 훑어 의미가 겹치는 것이 있는지 본다. 자동 판정이 어려우므로 눈으로 확인한다. `feature.md`와 `encoding.md`처럼 경계가 모호한 쌍이 생길 수 있다.

문서 파일은 사용자 승인 없이 만들 수 없으므로, 목록에 기억나지 않는 파일이 있으면 규칙이 지켜지지 않은 것이다. 사용자에게 확인한다.

```bash
grep -n "^#\{2,3\} " EDA.md
ls exp/*.md pipelines/*.md docs/*.md *.md
```

**슬롯 분량 확인** — 특정 슬롯에만 서술이 누적됐는지 본다.

```bash
python - <<'EOF'
import re, glob
for f in ['EDA.md'] + [x for x in glob.glob('pipelines/*.md') + glob.glob('exp/*.md')
                       if not x.endswith('TEMPLATE.md')]:
    lines = open(f).read().split('\n')
    idx = [i for i, l in enumerate(lines) if re.match(r'^#{2,3} ', l)]
    if not idx:
        continue
    print(f'\n{f}')
    for a, b in zip(idx, idx[1:] + [len(lines)]):
        n = b - a
        print(f'  {n:4d}줄  {lines[a][:60]}')
EOF
```

다른 슬롯 대비 유독 긴 것이 있으면 그 안에 서술이 누적된 것이다. 현재 상태만 남기고 나머지는 삭제하거나 `exp/`로 옮긴다. 마지막 슬롯이 유독 길면 헤딩 없는 꼬리 문단이 붙은 경우가 많다. 절대 기준선은 두지 않는다 — 문서마다 정당한 분량이 다르므로 슬롯 간 상대 비교로 판단한다.

## 완료 조건

- 실험 문서에 없는 `exp/<exp_id>/` 디렉토리가 없다
- 계약 밖 경로에 결과 파일이 없다
- 어디에도 쓰이지 않는 실험 디렉토리가 (확인 후) 정리됐다
- 제출하지 않은 `sub/*.csv`가 (확인 후) 정리됐다
- `진행중` 항목이 사용자와 함께 판정됐거나, 판정에 필요한 정보가 제시됐다
- `현재 상태`의 `줄기:` 줄이 지금 살아 있는 줄기와 일치한다 (닫은 줄기가 남아 있거나 연 줄기가 빠져 있지 않다)
- 줄기 머리·기준의 디렉토리와, `작업` 머리·판정 전 실험이 참조하는 실험의 디렉토리가 전부 남아 있다
- `보류` 목록이 방향별로 전부 제시됐다
- 시점 기반 헤딩이 없다
- `pipelines/*.md`의 `##`이 스키마 다섯 개와 일치하고, `pipelines/`·`exp/`에 `###`이 없다
