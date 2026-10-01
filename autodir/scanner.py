import os
from pathlib import Path

MARKERS = (".git", "pyproject.toml", "setup.py", "requirements.txt")
IGNORED_DIRS = {".venv", "venv", "__pycache__", ".git", "node_modules", ".idea"}


def find_project_root(start: Path) -> Path:
    """
    Idzie w górę drzewa katalogów od `start`, aż znajdzie folder
    zawierający jeden z MARKERS.
    Zwraca Path do tego folderu.
    Jeśli dojdzie do korzenia dysku i nic nie znajdzie -> podnosi wyjątek.
    """
    current = start if start.is_dir() else Path(start).parent

    while True:
        # Jeśli jesteśmy w korzeniu dysku, ex
        if current.parent == current:
            raise FileNotFoundError()

        # sprawdzamy czy istnieje jakikolwiek marker
        # w obecnym folderze
        for marker in MARKERS:
            it_is_root = (current / marker).exists()
            if it_is_root:
                return current

        # jesli nie znajdziemy rozszerzenia z MARKERS
        # idziemy o poziom wyżej
        current = current.parent


def _should_ignore(name: str, extra_ignored: set[str]) -> bool:
    """
    Sprawdza, czy dana nazwa (pliku lub folderu) powinna być pominięta
    podczas skanowania - na podstawie IGNORED_DIRS, wzorca *.egg-info
    oraz wzorców użytkownika z extra_ignored.
    """
    if name in IGNORED_DIRS:
        return True
    if name.endswith(".egg-info"):
        return True
    if name in extra_ignored:
        return True
    return False


def scan_project_tree(root: Path, extra_ignored: set[str] = None) -> list[Path]:
    """
    Rekurencyjnie przechodzi drzewo katalogów od `root`, pomijając
    foldery z IGNORED_DIRS (i nie wchodząc w ich podkatalogi).
    Zwraca listę Path do wszystkich znalezionych plików ORAZ folderów
    (bez samego roota).
    """
    if extra_ignored is None:
        extra_ignored = set()
    found: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not _should_ignore(d, extra_ignored)]
        filenames[:] = [f for f in filenames if not _should_ignore(f, extra_ignored)]

        for dirname in dirnames:
            found.append(Path(dirpath) / dirname)

        for filename in filenames:
            found.append(Path(dirpath) / filename)

    return found

