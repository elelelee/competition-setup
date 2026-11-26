"""실험 폴더 경로. 실험은 번호 없이 exp/<줄기>/<exp>/<실험>/ 경로로 가리킨다.

config와 코드는 이 모듈로 경로를 다룬다. 이름 규칙과 줄기·exp 문서가 있는지를 여기서 확인한다
(규칙은 CLAUDE.md `줄기 · exp · 실험`, `명명과 산출물`).
"""
import re
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent / 'exp'
NAME = re.compile(r'[a-z0-9][a-z0-9-]*')        # 줄기·exp·실험 이름: 짧은 소문자와 하이픈
TIMEWORD = re.compile(r'(^|-)(v\d+|new|old|tmp|final)(-|$)')   # 시점·순번 이름


def run_dir(ref: str) -> Path:
    """'<줄기>/.../<exp>/<실험>' 경로(exp/ 아래)를 실험 폴더로 바꾼다."""
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
