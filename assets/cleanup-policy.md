# 정리 정책

세션 종료 시 수행한다.

목적은 디스크 절약이 아니라 **다음 판단을 흐리지 않는 것**이다. 어떤 산출물이 유효한 결과인지 판단하는 데 시간이 들고, 그 판단이 틀리면 잘못된 실험을 앙상블에 넣는다.

판정 값은 exp 문서(`exp/<줄기>/<exp>/EXP.md`)의 제목(exp)과 실험 항목 제목(실험)에 있다. `기준` / `채택` / `보류(유망)` / `보류(중립)` / `보류(불리)` / `기각` / `진행중`.

**기록은 지우지 않는다. 지우는 것은 산출물뿐이다.** 줄기 문서, exp 문서, 실험마다의 `config.yaml`·`metrics.json`·`curves.png` 같은 추적 파일은 그 자리에 남는다. 정리에서 지우는 것은 추적하지 않는 예측(`*.npy`)·곡선 원자료(`*.npz`)·로그·체크포인트뿐이고, 필요해지면 그 자리의 `config.yaml`로 다시 만든다.

**산출물을 남길지는 판정이 아니라 정원과 보관으로 정한다.** 판정(`기각`/`보류`/`채택` 등)은 그 방향이 효과 있었는지의 기록이고, 삭제 여부와 연결하지 않는다. 판정과 보관을 한 값에 묶으면 둘 다 망가진다. 기각하면 산출물이 지워지니 기각의 문턱이 높아지고, 효과 없는 실험이 전부 `보류`에 쌓인다. 남길 이유는 판정이 아니라 `보관:` 줄에 따로 적는다.

## 보존 정책

| 대상 | 보존 | 삭제 |
|---|---|---|
| `EDA.md`, `exp/TEMPLATE.md`, 줄기 문서 `exp/**/BRANCH.md`, exp 문서 `exp/**/EXP.md` | 전부 영구 보존. 닫은 줄기와 정원 밖 exp의 문서도 남긴다 | 삭제 금지 |
| 실험 폴더의 추적 파일(`config.yaml`, `metrics.json`, `curves.png` 등) | 전부 보존 | 삭제 금지 |
| 실험 폴더의 산출물(예측·곡선 원자료·로그·`ckpt/`) | 산출물이 남는 exp와 실험 (아래 정의) | 그 밖 |
| `ckpt/` | 산출물이 남는 실험의 best 1개 + last 1개 | 나머지 epoch 체크포인트 |
| `sub/**/*.csv` | 제출한 것, 줄기 머리의 것 | 제출하지 않은 것 전부 (절차 3) |
| `data/processed/` | 재생성 스크립트가 있으면 최신만 | 중간 산출물 |

**산출물이 남는 exp와 실험**은 줄기 `상태` 절과 exp 문서로 정한다.

| 어디서 | 산출물이 남는 것 |
|---|---|
| `작업` 줄기 | 머리·대조가 있는 exp, 진행중 exp의 실험 전부. 그리고 이 실험들의 `config.yaml`이 가리키는 것을 끝까지 따라간 전부 — 실험 경로를 가리키면 그 실험만, exp 경로를 가리키면 그 exp 전체. 의존은 어느 줄기에 있든 남는다 |
| `보존` 줄기 | 머리가 있는 exp |
| 어느 줄기든 | 머리말에 `보관:` 이유가 적힌 exp. 제목이 `진행중`인 exp와 실험(`상태` 절이 낡았어도 판정 전 것은 남긴다) |

이 집합 밖이면 판정과 무관하게 산출물을 지운다. `채택`이어도 대조에서 밀려난 옛 exp는 보관하지 않았으면 지우고, `보류(유망)`도 정원 밖이고 보관하지 않았으면 지운다. 다만 새 exp가 옛 exp의 멤버를 가져다 쓰면, 옛 exp에서 그 멤버 실험만 의존으로 남는다.

`보존` 줄기와 `보관` exp는 자기 의존을 끌고 오지 않는다. 보관한 스택 exp가 다른 exp의 멤버를 가리키면, 그 멤버의 exp에도 `보관:`을 적어야 남는다. 남길 이유를 exp마다 따로 적게 해서, 무엇을 왜 남겼는지가 각 exp에서 읽히게 하려는 것이다.

남길 산출물을 `상태` 절로 정하므로, 그것이 낡은 채 정리하면 필요한 산출물이 지워진다. 머리·대조·진행중이 바뀔 때 바로 고치고, 정리 전에 한 번 더 본다. 아래 점검 스크립트는 `상태` 절과 exp 제목이 어긋나는 곳(제목은 `진행중`인데 `상태` 절의 진행중에 없는 exp 등)을 알려 준다.

## 절차

md 파싱은 취약하다. **자동 삭제하지 않고 후보 목록을 만들어 사용자 확인을 받는다.** 유효한 산출물을 파싱 오류로 지우는 것이 정리를 안 하는 것보다 나쁘다.

### 0. 점검 스크립트

1~3절의 목록을 한 번에 만든다. 프로젝트 루트에서 실행한다.

```bash
python - <<'EOF'
import os, re
from pathlib import Path

QUOTA = 4                                  # 작업 줄기의 진행중 exp 정원 (CLAUDE.md `정원과 보관` 절)
DROP = ('.npy', '.npz', '.log')            # 정리 때 지우는 산출물 확장자. 이 대회의 모델 파일 확장자가 있으면 더한다
NAME = re.compile(r'[a-z0-9][a-z0-9-]*')
STATE_KEYS = ('갈라진 곳', '상태', '머리', '대조', '진행중', '변동폭')
SECTIONS = ['구조', '상태', '다음 후보']   # 줄기 문서의 `##` 고정 스키마
exp = Path('exp')
rel = lambda p: p.relative_to(exp).as_posix()
problems, unlogged = [], []

# 줄기 = BRANCH.md가 있는 폴더, exp = 줄기 바로 아래의 줄기가 아닌 폴더, 실험 = exp 바로 아래 폴더
bdirs = {d.parent for d in exp.rglob('BRANCH.md')}
exps, runs = {}, {}
for b in bdirs:
    for p in sorted(b.iterdir()):
        if p.is_dir() and p not in bdirs:
            exps[rel(p)] = p
            runs.update({rel(q): q for q in p.iterdir() if q.is_dir() and q.name != 'ckpt'})
for p in exp.iterdir():
    if p.is_dir() and p not in bdirs:
        problems.append(f'{rel(p)}: exp/ 바로 아래인데 줄기 문서가 없음')
for d in exp.rglob('EXP.md'):
    if d.parent.parent not in bdirs:
        problems.append(f'{rel(d.parent)}: 줄기 문서가 없는 곳의 exp')

def resolve(token, exact=False):
    """경로 문자열 → ('run', 실험 경로) / ('exp', exp 경로) / None. exact가 아니면 뒤에 붙은 파일 경로를 떼고 맞춘다"""
    t = token.strip().removeprefix('./').removeprefix('exp/').rstrip('/')
    parts = t.split('/')
    for k in (range(len(parts), 1, -1) if not exact else [len(parts)]):
        s = '/'.join(parts[:k])
        if s in runs:
            return ('run', s)
        if s in exps:
            return ('exp', s)
    return None

def parse_exp(path):
    """제목, 머리말(첫 `##` 위)의 `- 키: 값`, 실험 항목별 판정, 결과에 LB가 적힌 실험"""
    title, head, items, lb, cur = None, {}, {}, set(), None
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('# ') and title is None:
            title = line
        elif line.startswith('## '):
            m = re.match(r'^## `([a-z0-9][a-z0-9-]*)`(?:.*·\s*(\S+))?\s*$', line)
            cur = m.group(1) if m else None
            items[cur or line[:40]] = m.group(2) if m else None
        elif not items and line.startswith('- '):
            k, _, v = line[2:].partition(':')
            head[k.strip()] = v.strip()
        elif cur and line.startswith('- 결과:') and re.search(r'LB\s*[0-9]', line):
            lb.add(cur)
    return title, head, items, lb

# 줄기 문서: `## 구조`·`## 상태`·`## 다음 후보` 세 절, `상태` 절의 고정 줄
branches = {}
for b in sorted(bdirs):
    lines = (b / 'BRANCH.md').read_text(encoding='utf-8').splitlines()
    kv = {}
    for l in lines:
        k, _, v = l[2:].partition(':')
        if l.startswith('- ') and k.strip() in STATE_KEYS:
            kv[k.strip()] = v.strip()
    name = rel(b)
    br = {'name': name, 'state': (kv.get('상태', '').split() or [None])[0]}
    for key in ('머리', '대조', '진행중'):
        br[key] = []
        for t in re.findall(r'`([^`]+)`', kv.get(key, '')):
            r = resolve(t, exact=True)
            want = 'exp' if key == '진행중' else 'run'
            if r and r[0] == want:
                br[key].append(r[1])
            else:
                problems.append(f'{name}: {key} `{t}`의 {"exp" if want == "exp" else "실험"} 폴더가 없음')
    branches[b] = br
    if [l[3:].strip() for l in lines if l.startswith('## ')] != SECTIONS:
        problems.append(f'{name}: 줄기 문서의 `##`이 {SECTIONS}이 아님')
    if not kv.get('변동폭'):
        problems.append(f'{name}: 변동폭 줄이 없음 (못 쟀으면 `미측정`)')
    if br['state'] not in ('작업', '보존', '닫힘'):
        problems.append(f'{name}: 상태 줄을 읽지 못함 ({br["state"]})')
    if br['state'] == '작업' and len(br['진행중']) > QUOTA:
        problems.append(f'{name}: 진행중 exp {len(br["진행중"])}개 > 정원 {QUOTA}')
    if br['state'] in ('보존', '닫힘') and br['진행중']:
        problems.append(f'{name}: {br["state"]} 줄기에 진행중 exp가 있음 {br["진행중"]}')
    long = [f'{k}: {v[:30]}' for k, v in kv.items() if len(v) > 200]
    if long:
        problems.append(f'{name}: 상태 줄에 서술이 쌓임 {long}')

# exp 문서
info = {}
for e, p in exps.items():
    if not (p / 'EXP.md').exists():
        unlogged.append(e)
        continue
    title, head, items, lb = parse_exp(p / 'EXP.md')
    m = re.match(r'^# `([a-z0-9][a-z0-9-]*)`.*·\s*(\S+)\s*$', title or '')
    names = {q.name for q in p.iterdir() if q.is_dir() and q.name != 'ckpt'}
    d = {'path': p, 'branch': branches.get(p.parent), 'verdict': m.group(2) if m else None,
         'head': head, 'items': items, 'lb': {f'{e}/{r}' for r in lb}}
    info[e] = d
    if not m or m.group(1) != p.name:
        problems.append(f'{e}: EXP.md 제목에서 이름·판정을 읽지 못함 (제목의 이름은 폴더 이름과 같아야 한다)')
    if not NAME.fullmatch(p.name) or any(not NAME.fullmatch(n) for n in names):
        problems.append(f'{e}: 이름 규칙(짧은 소문자·하이픈) 밖의 폴더가 있음')
    if names - set(items):
        unlogged.append(f'{e}/{{{",".join(sorted(names - set(items)))}}}')
        d['unlogged_run'] = True
    if '보관' in head and not head['보관']:
        problems.append(f'{e}: `보관:` 줄에 이유가 비어 있음')

for b in branches.values():
    wip_title = {e for e, d in info.items() if d['branch'] is b and d['verdict'] == '진행중'}
    if wip_title != set(b['진행중']):
        problems.append(f'{b["name"]}: 제목만 진행중 {sorted(wip_title - set(b["진행중"]))}, '
                        f'상태 절에만 진행중 {sorted(set(b["진행중"]) - wip_title)}')

# 산출물이 남는 exp와 실험
whole, runs_kept, only = set(), set(), set()    # whole: 의존까지 따라가는 exp / only: 그 exp만
for b in branches.values():
    head_exps = [r.rsplit('/', 1)[0] for r in b['머리']]
    if b['state'] == '작업':
        whole |= set(head_exps + [r.rsplit('/', 1)[0] for r in b['대조']] + b['진행중'])
    elif b['state'] == '보존':
        only |= set(head_exps)
for e, d in info.items():
    if d['verdict'] == '진행중':
        whole.add(e)
    if d['head'].get('보관'):
        only.add(e)
    runs_kept |= {f'{e}/{r}' for r, v in d['items'].items() if v == '진행중' and f'{e}/{r}' in runs}
def deps(path):
    out = set()
    for c in path.rglob('config.yaml'):
        text = '\n'.join(l.split('#')[0] for l in c.read_text(encoding='utf-8').splitlines())  # 주석은 의존이 아니다
        out |= {r for t in re.findall(r'[A-Za-z0-9_./-]*/[A-Za-z0-9_./-]+', text) if (r := resolve(t))}
    return out
stack = [exps[e] for e in whole]
while stack:
    for kind, key in deps(stack.pop()):
        if kind == 'exp' and key not in whole:
            whole.add(key)
            stack.append(exps[key])
        elif kind == 'run' and key.rsplit('/', 1)[0] not in whole and key not in runs_kept:
            runs_kept.add(key)
            stack.append(runs[key])
keep_exp = whole | only

print('== 1. 기록·상태 점검')
print('기록 없는 exp·실험:', unlogged or '없음')
for p in problems:
    print('  -', p)
if not problems:
    print('상태·위치 문제 없음')

print('\n== 2. 지울 산출물 (정원 밖, 보관 안 함, 의존 아님)')
total, n = 0, 0
for e in sorted(set(info) - keep_exp):
    d = info[e]
    if d.get('unlogged_run'):
        continue                           # 기록 전 실험이 섞인 exp는 건드리지 않는다
    kept = sorted(r.rsplit('/', 1)[1] for r in runs_kept if r.rsplit('/', 1)[0] == e)
    files = [f for f in d['path'].rglob('*') if f.is_file()
             and (f.suffix in DROP or 'ckpt' in f.relative_to(d['path']).parts)
             and f.relative_to(d['path']).parts[0] not in kept]
    if not files:
        continue                           # 이미 정리된 exp
    size = sum(f.stat().st_size for f in files) / 1e6
    total, n = total + size, n + 1
    note = f' · 남기는 실험 {kept}' if kept else ''
    print(f'{size:8.1f} MB  exp/{e}  ({d["verdict"]}{note})')
print(f'통째로 남기는 exp {len(keep_exp)}개 · 실험만 남기는 것 '
      f'{len([r for r in runs_kept if r.rsplit("/", 1)[0] not in keep_exp])}개 · 지울 exp {n}개 · 합계 {total:.1f} MB')

print('\n== 3. 제출하지 않은 제출 파일')
keep = set().union(*(d['lb'] for d in info.values()))
keep |= {r for b in branches.values() if b['state'] in ('작업', '보존') for r in b['머리']}
kept, skipped, total = [], [], 0
for f in sorted(Path('sub').rglob('*.csv')) if Path('sub').is_dir() else []:
    key = f.relative_to('sub').with_suffix('').as_posix()
    e = key.rsplit('/', 1)[0]
    if key in keep:
        kept.append(key)
    elif key not in runs:
        print(f'          {f.as_posix()}  (실험 경로와 맞지 않음 — 4절에서 본다)')
    elif e not in info or key.rsplit('/', 1)[1] not in info[e]['items']:
        skipped.append(key)                # 기록 전 실험
    else:
        size = f.stat().st_size / 1e6
        total += size
        has = key in runs and any(runs[key].glob('pred*'))
        print(f'{size:6.1f} MB  {f.as_posix()}  ({"테스트 예측 있음" if has else "테스트 예측 없음 — 다시 만들려면 재학습"})')
print(f'남기는 것 {len(kept)}개: {kept} · 지울 합계 {total:.1f} MB')
if skipped:
    print('기록 전이라 후보에서 뺀 파일:', skipped)
EOF
```

### 1. 기록·상태 점검

`== 1` 출력을 먼저 처리한다. 여기가 비어 있지 않으면 2·3절의 목록을 믿을 수 없다.

- **기록 없는 exp·실험** — `EXP.md`가 없는 exp 폴더나, `EXP.md`에 항목이 없는 실험 폴더다. 기록 규칙이 지켜지지 않았다는 신호다. 삭제 전에 `metrics.json`을 읽어 소급 기록할 수 있는지 먼저 확인한다. 유효한 실험을 기록 누락 때문에 버리는 것이 가장 큰 손실이다. 여러 세션이 동시에 일하면 다른 세션이 실험을 돌리는 중이라 기록 전일 수 있으므로, 만든 세션이 끝났는지 확인하기 전에는 지우지 않는다. 그래서 이런 exp는 2·3절 후보에서 빠진다. 줄기를 가르다가 `BRANCH.md`를 만들지 않은 하위 줄기도 여기 exp로 잡힌다
- **줄기 문서가 없는 곳** — exp가 줄기 밖(`exp/` 바로 아래 등)에 있다. 맞는 줄기로 옮기거나 줄기 문서를 만든다(승인 필요). 옮긴 뒤에는 옛 경로를 가리키던 config와 문서를 고친다
- **머리·대조·진행중의 폴더가 없음** — 경로가 틀렸거나 이미 없어진 것을 가리킨다. `상태` 절을 고치거나 그 자리의 config로 다시 만든다
- **`##`이 `구조`·`상태`·`다음 후보`가 아님, 변동폭 줄이 없음, 제목과 `상태` 절의 진행중이 어긋남, 정원 초과, 상태 줄에 쌓인 서술, 비어 있는 `보관:`, 이름 규칙 밖의 폴더** — 문서를 먼저 고친다. 정원을 넘은 줄기는 2-1절의 판정 세션을 열어 진행중 exp를 줄인다

### 2. 산출물 삭제

`== 2` 목록을 사용자에게 보여주고 확인받은 뒤 지운다. 각 줄 끝의 괄호는 그 exp의 판정과 의존으로 남기는 실험이다. 판정은 참고로만 보여 준다 — 남길지는 정원과 보관으로 이미 정해졌다. 목록에 남기고 싶은 exp가 있으면 지우지 말고 그 exp 머리말에 `보관:` 이유를 적은 뒤 스크립트를 다시 돌린다.

지우는 것은 목록의 exp 안에서 `DROP` 확장자 파일과 `ckpt/`뿐이고, 괄호에 적힌 남기는 실험은 건드리지 않는다(모두 비추적이라 git 작업이 없다). 추적 파일과 문서는 남으므로 exp 폴더 자체는 없어지지 않는다. 다시 필요해지면 그 실험 폴더의 `config.yaml`로 다시 실행한다.

### 2-1. 판정 세션

세션 종료는 판정을 모아서 하기 좋은 시점이다. exp와 구성을 바꿔 본 실험은 `진행중`으로 기록되므로 여기서 확정한다.

판정 세션은 세션 종료 외에도 열린다. **새 exp를 열기 전에는 그 exp가 딛는 exp의 진행중 실험을**, **줄기의 진행중 exp가 정원(4개)을 채웠을 때는 그 exp들을** 판정한다. `CLAUDE.md`의 `실험을 시작하기 전` 참조. 대회 후반에는 제출도 정리도 강제성이 없어져 판정이 밀리므로, 실험 시작이라는 확실히 오는 시점을 트리거로 함께 쓴다.

```bash
grep -rH "^#\{1,2\} .*진행중" exp/ --include=EXP.md
grep -rH "^#\{1,2\} .*보류" exp/ --include=EXP.md
grep -rH "^- 보관:" exp/ --include=EXP.md
```

진행중인 실험과 exp마다 세 신호가 어느 방향인지, 엇갈린다면 어디서 엇갈리는지, 판정을 가를 축과 그 비용을 정리해 사용자에게 제시하고 결정을 받는다. 신호가 명백히 한쪽인 것만 단독으로 판정하고, 그 경우에도 무엇을 근거로 그렇게 판정했는지 함께 보고한다.

실험을 판정할 때는 그 변경을 다음 exp의 구성에 가져갈지를 함께 정한다. exp를 판정할 때는 세 가지를 함께 정하고 그대로 문서에 적는다.

- 그 exp의 실험을 줄기 머리로 올릴지(다음 exp를 그 위에 쌓을지)
- 정원 밖으로 나가면 산출물을 남길 이유가 있는지(`보관:`)
- `결론`

`보류`는 **방향별로 묶어 전부 제시한다.** `유망`만 보여주면 `불리`가 시야에서 사라져 사실상 기각과 같아진다. 산출물이 있든 없든 다시 보지 않게 되는 것이 실제 손실이다.

```
보류(유망)  3건 — 재판정 값어치 큼
보류(중립)  7건
보류(불리)  4건 — 재시도 조건이 적힌 것이 있는지 확인
```

`보류`가 많은 것 자체는 정상이다. 기각 조건이 좁으므로 대부분의 실험이 여기 머문다. 산출물 삭제가 판정과 분리돼 있으므로 보류가 많아도 산출물은 쌓이지 않는다. 다만 `보류(유망)`이 여러 개 쌓여 있으면 다음 실험을 늘리기보다 그중 하나를 해소하는 편이 낫다는 것을 알린다.

`보관:` 목록도 이때 훑는다. 이유가 사라진 것(그 구성을 다시 볼 일이 없어졌거나, 비교 기준이 다른 exp로 바뀜)은 줄을 지운다.

줄기도 이때 본다. 머리를 더 확장하지 않을 `작업` 줄기는 남길 이유가 있으면 `보존 — <이유>`로, 없으면 `닫힘`으로 바꾼다. `보존` 줄기의 이유가 사라졌으면 닫는다. `구조` 절이 지금의 모델 구조와 맞는지, `다음 후보`에 이미 연 exp나 판정에서 버린 방향이 남아 있지 않은지도 본다.

```bash
grep -rHn "^- 상태:" exp/ --include=BRANCH.md
```

### 3. 제출하지 않은 제출 파일 삭제

학습·결합 코드는 실험마다 `sub/<실험 경로>.csv`를 쓰지만 실제로 제출하는 것은 그중 일부다. **제출하지 않은 CSV는 남기지 않는다.** 테스트 예측 산출물과 같은 내용이라 따로 둘 이유가 없고, 쌓이면 어느 파일이 제출한 것인지 가려내는 비용만 생긴다.

남기는 것은 셋이다.

- 제출한 것 — 실험 항목의 `결과`에 LB 점수가 적힌 것
- `작업`·`보존` 줄기의 머리 — 아직 제출하지 않았어도 곧 제출할 수 있는 후보다
- exp 문서가 아직 없는 exp의 것 — 다른 세션이 만드는 중일 수 있다 (1절과 같은 이유)

`== 3` 목록을 사용자에게 보여주고 확인받은 뒤 지운다. `sub/`는 git이 추적하지 않으므로 지우면 파일은 돌아오지 않는다. 다시 필요해지면 실험 폴더의 테스트 예측과 test id로 다시 쓰고, 그것도 없으면 그 자리의 `config.yaml`로 다시 학습한다.

이 절차는 제출이 기록돼 있다는 전제로 돈다. 제출하고도 LB 점수를 적지 않은 실험은 제출하지 않은 것으로 잡히므로, `남기는 것` 목록이 기억하는 제출과 맞는지 먼저 본다. 맞지 않으면 지우기 전에 exp 문서부터 고친다.

### 4. 계약 밖 파일 탐지

```bash
find . -maxdepth 2 -name '*.csv' -not -path './sub/*' -not -path './data/*'
find . \( -name '*final*' -o -name '*copy*' -o -name '*_v[0-9]*' -o -name '*수정*' \) \
     -not -path './.git/*'
```

여기서 걸린 파일도 삭제 전에 목록을 보여주고 확인받는다. 사용자가 의도적으로 만든 파일일 수 있다.

### 5. 헤딩 규약 점검

헤딩이 주소 단위이므로 헤딩만 훑으면 구조 이탈이 드러난다. 개수로 판정하지 않는다. `EDA.md`의 범주는 데이터에 따라 달라지므로 개수 기준선을 두면 정당한 조정까지 위반으로 잡힌다.

**시점 기반 이름 탐지** — 언제 썼는지를 가리키는 헤딩과 폴더 이름은 예외 없이 위반이다.

```bash
grep -rn "^#\{2,3\} .*\(요약\|현황\|총평\|변경\|추가 분석\|업데이트\|[0-9]차\|재검토\|기타\)" \
     EDA.md exp/ --include=*.md
find exp -type d | grep -E '/(v[0-9]+|new|old|tmp|final|[0-9]+차)(-|/|$)|[-_]v[0-9]+(/|$)'
```

**스키마 이탈 탐지** — 줄기 문서는 `구조`·`상태`·`다음 후보` 세 절이 고정이다(0절 스크립트가 본다). 줄기 문서와 exp 문서는 `###`을 쓰지 않는다.

```bash
grep -rHn '^### ' exp/ --include=EXP.md --include=BRANCH.md
```

`###` 검출이 있으면 위반이다. exp 문서에서 `###`이 나오면 실험 항목 안에 하위 서술이 자란 것이므로 확정된 필드로 압축하거나 별도 실험으로 분리한다.

**중복 범주·줄기·exp 탐지** — `EDA.md`의 헤딩 목록, 줄기 목록, exp 제목을 훑어 의미가 겹치는 것이 있는지 본다. 자동 판정이 어려우므로 눈으로 확인한다. 구성이 같은 exp가 둘이면 구성을 바꾸지 않는 실험에 exp를 연 것이다 — 다음부터 그 exp의 실험으로 둔다. 같은 조건으로 비교되는 exp가 두 줄기에 나뉘어 있으면 `갈라진 곳`의 이유를 본다.

문서 파일은 사용자 승인 없이 만들 수 없으므로, 목록에 기억나지 않는 줄기나 문서가 있으면 규칙이 지켜지지 않은 것이다. 사용자에게 확인한다.

```bash
grep -n "^#\{2,3\} " EDA.md
find exp -name BRANCH.md | sort
grep -rH "^# " exp/ --include=EXP.md | sort
ls docs/*.md *.md
```

**슬롯 분량 확인** — 특정 슬롯에만 서술이 누적됐는지 본다.

```bash
python - <<'EOF'
import re
from pathlib import Path
files = [Path('EDA.md')] + sorted(Path('exp').rglob('BRANCH.md')) + sorted(Path('exp').rglob('EXP.md'))
for f in files:
    lines = f.read_text(encoding='utf-8').split('\n')
    idx = [i for i, l in enumerate(lines) if re.match(r'^#{2,3} ', l)]
    if not idx:
        continue
    print(f'\n{f.as_posix()}  (항목 {len(idx)}개)')
    for a, b in zip(idx, idx[1:] + [len(lines)]):
        print(f'  {b - a:4d}줄  {lines[a][:60]}')
EOF
```

다른 슬롯 대비 유독 긴 것이 있으면 그 안에 서술이 누적된 것이다. 현재 상태만 남기고 나머지는 삭제하거나 exp 문서로 옮긴다. 마지막 슬롯이 유독 길면 헤딩 없는 꼬리 문단이 붙은 경우가 많다. 절대 기준선은 두지 않는다 — 문서마다 정당한 분량이 다르므로 슬롯 간 상대 비교로 판단한다. exp 하나에 실험이 많은 것 자체는 정상이다. 다만 진행중 실험이 쌓였는데 새 exp가 열리지 않고 있으면, 가져갈 변경을 모아 새 exp를 열 때가 된 것이다.

## 완료 조건

- 점검 스크립트의 `== 1`에 기록 없는 exp·실험과 상태·위치 문제가 없다
- 계약 밖 경로에 결과 파일이 없다
- 정원 밖이고 보관하지 않았고 의존도 아닌 산출물이 (확인 후) 정리됐다
- 제출하지 않은 `sub/**/*.csv`가 (확인 후) 정리됐다
- 진행중인 exp와 실험이 사용자와 함께 판정됐거나, 판정에 필요한 정보가 제시됐다
- 모든 `작업` 줄기의 진행중 exp가 정원 안이다
- 줄기의 `구조` 절이 지금의 모델 구조와 맞고, `보관:`과 `보존` 이유가 아직 유효하다
- `보류` 목록이 방향별로 전부 제시됐다
- 시점 기반 헤딩과 시점 기반 폴더 이름이 없다
- 줄기 문서의 `##`이 `구조`·`상태`·`다음 후보`이고, 줄기·exp 문서에 `###`이 없다
