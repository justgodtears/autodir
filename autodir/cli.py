import argparse
from pathlib import Path

from .scanner import find_project_root, scan_project_tree
from .naming import resolve_collisions
from .generator import build_file_content

OUTPUT_FILENAME = "autodir_paths.py"


def generate() -> None:
    """
    Pełny pipeline: wykrywa root, skanuje projekt (pomijając własny
    plik wynikowy), rozwiązuje kolizje nazw, buduje zawartość pliku
    i zapisuje go w roocie projektu.
    """
    root = find_project_root(Path.cwd())
    ignored_files = load_ignore_patterns(root)
    paths = scan_project_tree(root, ignored_files)
    filtered_paths = [p for p in paths if p != root / OUTPUT_FILENAME]
    entries = resolve_collisions(filtered_paths, root)
    content = build_file_content(entries)
    (root / OUTPUT_FILENAME).write_text(content)
    print(f"Generated {OUTPUT_FILENAME} with {len(entries)} entries")


IGNORE_FILENAME = ".autodirignore"

IGNORE_FILE_TEMPLATE = (
    "# Add extra file/folder names to ignore during autodir scanning.\n"
    "# One pattern per line. Lines starting with # are comments.\n"
    "# Example:\n"
    "# my_secret_folder\n"
    "# temp_data\n"
)

def init() -> None:
    """
    Tworzy plik .autodirignore w roocie projektu z domyślnym szablonem,
    jeśli jeszcze nie istnieje. Nie nadpisuje istniejącego pliku.
    """
    root = find_project_root(Path.cwd())
    ignore_path = root / IGNORE_FILENAME

    if ignore_path.exists():
        print("File already exists, skipping init command.")
        return


    ignore_path.write_text(IGNORE_FILE_TEMPLATE)
    print(f"Created {IGNORE_FILENAME} successfully.")

def load_ignore_patterns(root: Path) -> set[str]:
    """
    Wczytuje dodatkowe wzorce ignorowania z pliku .autodirignore
    w roocie projektu. Pomija puste linie i komentarze (linie
    zaczynające się od '#'). Zwraca pusty zbiór, jeśli plik nie istnieje.
    """
    ignore_path = root / IGNORE_FILENAME
    if not ignore_path.exists():
        return set()

    text = ignore_path.read_text()
    text_lines = text.splitlines()
    lines = set()
    for line in text_lines:
        line = line.strip()

        if line.startswith("#") or len(line) == 0:
            continue

        lines.add(line)

    return lines

def main() -> None:
    """
    Punkt wejścia CLI. Obsługuje komendę `autodir generate`.
    """
    parser = argparse.ArgumentParser(prog="autodir")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("generate")
    subparsers.add_parser("init")

    args = parser.parse_args()

    if args.command == "init":
        init()

    if args.command == "generate":
        generate()

    if args.command is None:
        parser.print_help()