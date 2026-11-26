"""exp/ 트리 점검. 정리 정책(docs/cleanup-policy.md)의 1~3절 목록을 만든다.

프로젝트 루트에서 실행한다. 아무것도 지우지 않는다 — 출력된 목록을 사용자에게 보여주고 확인받은 뒤 지운다.

    python src/check_exp.py           # 1. 기록·상태 점검  2. 지울 산출물  3. 지울 제출 파일
    python src/check_exp.py --slots   # 문서의 헤딩별 분량도 함께 본다
"""
import os
import re
import sys
from pathlib import Path

QUOTA = 4                                  # 작업 줄기의 진행중 exp 정원 (CLAUDE.md `정원과 보관`)
DROP = ('.npy', '.npz', '.log')            # 정리 때 지우는 산출물 확장자. 이 대회의 모델 파일 확장자가 있으면 더한다
NAME = re.compile(r'[a-z0-9][a-z0-9-]*')   # 줄기·exp·실험 이름
TIMEWORD = re.compile(r'(^|-)(v\d+|new|old|tmp|final)(-|$)|\d+차')
TIME_HEADING = re.compile(r'^#{2,3} .*(요약|현황|총평|변경|추가 분석|업데이트|\d차|재검토|기타)')
STATE_KEYS = ('갈라진 곳', '상태', '머리', '대조', '진행중', '변동폭')
SECTIONS = ['구조', '상태', '다음 후보']   # 줄기 문서의 `##` 고정 스키마
EXP = Path('exp')


def rel(p):
    return p.relative_to(EXP).as_posix()


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


def main(slots=False):
    problems, unlogged = [], []

    # 줄기 = BRANCH.md가 있는 폴더, exp = 줄기 바로 아래의 줄기가 아닌 폴더, 실험 = exp 바로 아래 폴더
    bdirs = {d.parent for d in EXP.rglob('BRANCH.md')}
    exps, runs = {}, {}
    for b in bdirs:
        for p in sorted(b.iterdir()):
            if p.is_dir() and p not in bdirs:
                exps[rel(p)] = p
                runs.update({rel(q): q for q in p.iterdir() if q.is_dir() and q.name != 'ckpt'})
    for p in EXP.iterdir():
        if p.is_dir() and p not in bdirs:
            problems.append(f'{rel(p)}: exp/ 바로 아래인데 줄기 문서가 없음')
    for d in EXP.rglob('EXP.md'):
        if d.parent.parent not in bdirs:
            problems.append(f'{rel(d.parent)}: 줄기 문서가 없는 곳의 exp')
    for p in [*bdirs, *exps.values(), *runs.values()]:
        if TIMEWORD.search(p.name):
            problems.append(f'{rel(p)}: 시점·순번을 가리키는 이름')

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

    # 줄기 문서
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
            want = 'exp' if key == '진행중' else 'run'
            for t in re.findall(r'`([^`]+)`', kv.get(key, '')):
                r = resolve(t, exact=True)
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

    # 헤딩: 줄기·exp 문서의 `###`, 시점 기반 헤딩
    for f in [Path('EDA.md'), *sorted(EXP.rglob('BRANCH.md')), *sorted(EXP.rglob('EXP.md'))]:
        if not f.exists():
            continue
        for i, l in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            if l.startswith('### ') and f.name != 'EDA.md':
                problems.append(f'{f.as_posix()}:{i}: `###` — 하위 서술이 자랐다. 필드로 압축하거나 실험으로 나눈다')
            if TIME_HEADING.match(l):
                problems.append(f'{f.as_posix()}:{i}: 시점 기반 헤딩 `{l[:40]}`')

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
            whole.add(e)                     # 상태 절이 낡았어도 판정 전 exp는 남긴다
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
        print('상태·위치·이름·헤딩 문제 없음')

    print('\n== 2. 지울 산출물 (정원 밖, 보관 안 함, 의존 아님)')
    total, n = 0, 0
    for e in sorted(set(info) - keep_exp):
        d = info[e]
        if d.get('unlogged_run'):
            continue                         # 기록 전 실험이 섞인 exp는 건드리지 않는다
        kept = sorted(r.rsplit('/', 1)[1] for r in runs_kept if r.rsplit('/', 1)[0] == e)
        files = [f for f in d['path'].rglob('*') if f.is_file()
                 and (f.suffix in DROP or 'ckpt' in f.relative_to(d['path']).parts)
                 and f.relative_to(d['path']).parts[0] not in kept]
        if not files:
            continue                         # 이미 정리된 exp
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
            skipped.append(key)              # 기록 전 실험
        else:
            size = f.stat().st_size / 1e6
            total += size
            has = any(runs[key].glob('pred*'))
            print(f'{size:6.1f} MB  {f.as_posix()}  ({"테스트 예측 있음" if has else "테스트 예측 없음 — 다시 만들려면 재학습"})')
    print(f'남기는 것 {len(kept)}개: {kept} · 지울 합계 {total:.1f} MB')
    if skipped:
        print('기록 전이라 후보에서 뺀 파일:', skipped)

    if slots:
        print('\n== 문서별 헤딩 분량')
        for f in [Path('EDA.md'), *sorted(EXP.rglob('BRANCH.md')), *sorted(EXP.rglob('EXP.md'))]:
            if not f.exists():
                continue
            lines = f.read_text(encoding='utf-8').split('\n')
            idx = [i for i, l in enumerate(lines) if re.match(r'^#{2,3} ', l)]
            if idx:
                print(f'\n{f.as_posix()}  (항목 {len(idx)}개)')
                for a, b in zip(idx, idx[1:] + [len(lines)]):
                    print(f'  {b - a:4d}줄  {lines[a][:60]}')


if __name__ == '__main__':
    main(slots='--slots' in sys.argv)
