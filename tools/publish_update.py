import ast
import base64
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_FILE = REPO_ROOT / "src" / "zapret_manager_gui.py"
DOWNLOADS = Path.home() / "Downloads"
CANDIDATE_DIRS = [DOWNLOADS, REPO_ROOT]

SETUP_RE = re.compile(r"ZapretManager_Setup_v([0-9][0-9A-Za-z_.-]*)\.py$", re.IGNORECASE)
GUI_RE = re.compile(r"zapret_manager_gui(?:_v([0-9][0-9A-Za-z_.-]*))?\.py$", re.IGNORECASE)
VERSION_RE = re.compile(r'APP_VERSION\s*=\s*"([^"]+)"')
SOURCE_RE = re.compile(r'APP_SOURCE_B64\s*=\s*"([^"]+)"')


def normalize_version(value: str):
    value = value.strip().lstrip("vV").replace("_", ".")
    parts = []
    for part in re.split(r"[.-]", value):
        if part.isdigit():
            parts.append(int(part))
        else:
            m = re.match(r"(\d+)([A-Za-z]+)?(\d+)?", part)
            if m:
                parts.append(int(m.group(1)))
                if m.group(2):
                    parts.append(ord(m.group(2).lower()[0]) - 96)
                if m.group(3):
                    parts.append(int(m.group(3)))
            elif part:
                parts.append(0)
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:8])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def get_app_version(source: str) -> str | None:
    match = VERSION_RE.search(source)
    return match.group(1) if match else None


def extract_source_from_setup(path: Path) -> str | None:
    text = read_text(path)
    match = SOURCE_RE.search(text)
    if not match:
        return None
    return base64.b64decode(match.group(1)).decode("utf-8")


def candidate_source(path: Path) -> tuple[str, str] | None:
    if SETUP_RE.match(path.name):
        source = extract_source_from_setup(path)
        if not source:
            return None
        version = get_app_version(source)
        if not version:
            return None
        return version, source

    if GUI_RE.match(path.name):
        source = read_text(path)
        version = get_app_version(source)
        if not version:
            return None
        return version, source

    return None


def find_candidates():
    found = []
    for folder in CANDIDATE_DIRS:
        if not folder.exists():
            continue
        for path in folder.glob("*.py"):
            item = candidate_source(path)
            if item:
                version, source = item
                found.append((normalize_version(version), version, path, source))
    found.sort(reverse=True, key=lambda x: (x[0], x[2].stat().st_mtime))
    return found


def run(cmd):
    print(">", " ".join(cmd))
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def git_available():
    try:
        subprocess.run(["git", "--version"], cwd=REPO_ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False


def main():
    print("ZapretManager publisher")
    print("Repo:", REPO_ROOT)
    print("Downloads:", DOWNLOADS)

    if not git_available():
        print("ERROR: git не найден. Установи Git for Windows или открой через Git Bash.")
        input("Enter для выхода...")
        return 1

    current_source = read_text(SRC_FILE) if SRC_FILE.exists() else ""
    current_version = get_app_version(current_source) or "0.0.0"
    print("Current repo version:", current_version)

    candidates = find_candidates()
    if not candidates:
        print("Новых файлов не найдено. Положи ZapretManager_Setup_vX.py или zapret_manager_gui_vX.py в Downloads.")
        input("Enter для выхода...")
        return 0

    best_norm, best_version, best_path, best_source = candidates[0]
    print("Best candidate:", best_path)
    print("Best candidate version:", best_version)

    if normalize_version(best_version) <= normalize_version(current_version):
        print("Публиковать нечего: найденная версия не новее текущей.")
        input("Enter для выхода...")
        return 0

    SRC_FILE.parent.mkdir(parents=True, exist_ok=True)
    SRC_FILE.write_text(best_source, encoding="utf-8")
    print("Updated:", SRC_FILE)

    run(["git", "status", "--short"])
    run(["git", "add", "src/zapret_manager_gui.py"])
    run(["git", "commit", "-m", f"Update Zapret Manager to v{best_version}"])
    run(["git", "push"])

    print("Готово. GitHub Actions должен сам собрать релиз.")
    print("Actions: https://github.com/MisterFD131/zm-ultra-terminal-v1p1/actions")
    print("Releases: https://github.com/MisterFD131/zm-ultra-terminal-v1p1/releases")
    input("Enter для выхода...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
