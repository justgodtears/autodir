import collections
import re
from dataclasses import dataclass
from pathlib import Path

def sanitize_name(name: str) -> str:
    """
    Zamienia dowolny string (nazwę pliku lub folderu) na poprawny
    identyfikator Pythona w stylu SCREAMING_SNAKE_CASE.

    Przykład: "report (final).csv" -> "REPORT_FINAL_CSV"
    Przykład: "my-data"            -> "MY_DATA"

    Zasady:
    - wszystkie znaki NIE będące literą, cyfrą ani podkreślnikiem
      zamieniamy na podkreślnik "_"
    - całość zamieniamy na wielkie litery
    - jeśli po sanityzacji zostały podwójne/wielokrotne podkreślniki
      obok siebie (np. z "report (final)" -> "REPORT__FINAL"),
      redukujemy je do pojedynczego "_"
    - usuwamy podkreślniki na początku/końcu stringa (strip)
    - jeśli wynik zaczyna się od cyfry (np. plik "2024_report.csv"
      da "2024_REPORT_CSV") -> doklejamy podkreślnik na początku,
      bo identyfikator Pythona nie może zaczynać się od cyfry
    """
    replaced_chars = re.sub(r"[^A-Za-z0-9_]", "_", name)
    to_upper = replaced_chars.upper()
    replaced_underscores = re.sub(r"_+", "_", to_upper)
    clean_text = replaced_underscores.strip("_")
    final_name = "_" + clean_text if clean_text[0].isdigit() else clean_text

    return final_name


@dataclass
class PathEntry:
    """
    Reprezentuje jeden wpis w wygenerowanym pliku ze ścieżkami:
    finalną nazwę zmiennej oraz powiązaną z nią ścieżkę.
    """
    name: str
    absolute_path: Path
    path_from_root: Path


def resolve_collisions(paths: list[Path], root: Path) -> list[PathEntry]:
    """
    Dla listy ścieżek oblicza finalne nazwy zmiennych, rozwiązując
    kolizje przez dodanie sufiksu _2, _3, ... przy powtórzeniach
    (w kolejności występowania na liście `paths`).
    Zwraca listę PathEntry.
    """
    groups: dict[str, list[Path]] = collections.defaultdict(list)
    for path in paths:
        sanitized_name = sanitize_name(path.name)
        groups[sanitized_name].append(path)

    result: list[PathEntry] = []
    for base_name, group_paths in groups.items():
        for index, path in enumerate(group_paths):
            if index == 0:
                final_name = base_name
            else:
                final_name = f"{base_name}_{(index + 1)}"

            entry = PathEntry(
                name=final_name,
                absolute_path=path,
                path_from_root=path.relative_to(root),
            )
            result.append(entry)

    return result