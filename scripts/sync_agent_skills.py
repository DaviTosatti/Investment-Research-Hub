"""Sincroniza as skills de desenvolvimento entre os agentes.

Fonte canônica: `.agents/skills` (lida por Antigravity e Codex).
Espelho: `.claude/skills` (lido pelo Claude Code).
Também gera `skills-lock.json` com o hash de cada skill.

Uso:
    python scripts/sync_agent_skills.py          # sincroniza e atualiza o lock
    python scripts/sync_agent_skills.py --check  # falha se espelho/lock divergirem
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "skills"
MIRROR = ROOT / ".claude" / "skills"
REFS = ROOT / ".agents" / "references"  # skills apontam para ../../references
REFS_MIRROR = ROOT / ".claude" / "references"
LOCK = ROOT / "skills-lock.json"

ORIGINS = {
    "reverse-engineer-anything": ("morluto/rea", "dc7594e85f6193b1da0cda9c858bcd3ca923ef56"),
}
DEFAULT_ORIGIN = ("addyosmani/agent-skills", "301b02b12bff98e4688e6984af6556802322bbde")


def digest(folder: Path) -> str:
    """Hash estável do conteúdo (caminhos relativos + bytes, EOL normalizado)."""
    h = hashlib.sha256()
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        h.update(path.relative_to(folder).as_posix().encode())
        h.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def skills() -> list[Path]:
    return sorted(p for p in SOURCE.iterdir() if p.is_dir() and (p / "SKILL.md").exists())


def build_lock() -> dict:
    entries = {}
    for folder in skills():
        source, commit = ORIGINS.get(folder.name, DEFAULT_ORIGIN)
        entries[folder.name] = {
            "source": source,
            "sourceType": "github",
            "commit": commit,
            "skillPath": f".agents/skills/{folder.name}/SKILL.md",
            "computedHash": digest(folder),
        }
    return {"version": 1, "skills": entries}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    check = parser.parse_args().check
    lock = build_lock()
    problems: list[str] = []

    expected = {f.name for f in skills()}
    present = {p.name for p in MIRROR.iterdir() if p.is_dir()} if MIRROR.exists() else set()
    for name in sorted(expected | present):
        src, dst = SOURCE / name, MIRROR / name
        if name not in expected:
            problems.append(f"espelho sem origem: {name}")
            if not check:
                shutil.rmtree(dst)
        elif not dst.exists() or digest(src) != digest(dst):
            problems.append(f"espelho desatualizado: {name}")
            if not check:
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)

    if not REFS_MIRROR.exists() or digest(REFS) != digest(REFS_MIRROR):
        problems.append("referências desatualizadas")
        if not check:
            shutil.rmtree(REFS_MIRROR, ignore_errors=True)
            shutil.copytree(REFS, REFS_MIRROR)

    current = json.loads(LOCK.read_text("utf-8")) if LOCK.exists() else None
    if current != lock:
        problems.append("skills-lock.json desatualizado")
        if not check:
            LOCK.write_text(json.dumps(lock, indent=2) + "\n", "utf-8")

    if check and problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"{len(expected)} skills; {'divergências: ' + str(len(problems)) if problems else 'ok'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
