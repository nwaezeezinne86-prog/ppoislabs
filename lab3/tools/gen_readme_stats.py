"""Build lab3/README.md from the source code so the documentation never drifts from the code."""
from __future__ import annotations

import ast
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
PACKAGE_DIR = LAB_DIR / "fitness"
README_PATH = LAB_DIR / "README.md"
EXCEPTION_MODULE = "exceptions"
NO_LINKS = "—"

HEADER = """# Лабораторная работа №3 — Приложение для отслеживания фитнеса

Предметная область: **приложение для отслеживания фитнеса** (тренировки, кардио с GPS, пульс и сон,
питание, цели и достижения, соревнования, персональные тренеры, носимые устройства).
Реализация на Python 3.10+, без внешних зависимостей.

## Структура

- `fitness/` — объектная модель предметной области (без ввода-вывода);
- `cli.py` — консольное меню, отделённое от модели (работает через фасад `FitnessApp`);
- `tests/` — unit-тесты (`unittest`);
- `docs/` — документация Sphinx (autodoc);
- `tools/gen_readme_stats.py` — генератор этого файла.

## Запуск

```bash
python cli.py                                   # консольное меню
python -m unittest discover -s tests -t .       # тесты
coverage run -m unittest discover -s tests -t . # покрытие
coverage report --fail-under=90
python tools/gen_readme_stats.py                # перегенерировать README
pip install sphinx && python -m sphinx -b html docs docs/_build/html  # документация
```

Формат строки таблицы: Класс | число полей | число методов | связанные классы.
"""


def annotation_names(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def is_property(func: ast.FunctionDef) -> bool:
    return any(isinstance(dec, ast.Name) and dec.id == "property" for dec in func.decorator_list)


def class_info(node: ast.ClassDef) -> dict:
    fields = [item for item in node.body if isinstance(item, ast.AnnAssign)]
    methods = [item for item in node.body if isinstance(item, ast.FunctionDef)
               and not item.name.startswith("_") and not is_property(item)]
    names: set[str] = set()
    for item in fields:
        names |= annotation_names(item.annotation)
    for method in methods:
        for arg in method.args.args + method.args.kwonlyargs:
            names |= annotation_names(arg.annotation)
    return {"fields": [item.target.id for item in fields], "methods": [item.name for item in methods],
            "refs": names, "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
            "doc": ast.get_docstring(node) or ""}


def collect() -> tuple[dict[str, dict], dict[str, str]]:
    classes: dict[str, dict] = {}
    exceptions: dict[str, str] = {}
    for path in sorted(PACKAGE_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in (item for item in tree.body if isinstance(item, ast.ClassDef)):
            if path.stem == EXCEPTION_MODULE:
                exceptions[node.name] = ast.get_docstring(node) or ""
            else:
                classes[node.name] = class_info(node)
    return classes, exceptions


def related(name: str, info: dict, known: set[str]) -> list[str]:
    return sorted((info["refs"] | set(info["bases"])) & known - {name})


def summary_table(classes: dict[str, dict]) -> list[str]:
    known = set(classes)
    rows = ["| Класс | Поля | Методы | Ассоциации (связанные классы) |", "|---|---|---|---|"]
    for name in sorted(classes):
        info = classes[name]
        links = ", ".join(related(name, info, known)) or NO_LINKS
        rows.append(f"| {name} | {len(info['fields'])} | {len(info['methods'])} | {links} |")
    return rows


def detail_section(classes: dict[str, dict]) -> list[str]:
    lines = ["", "## Подробное описание классов", ""]
    for name in sorted(classes):
        info = classes[name]
        lines.append(f"### {name}")
        lines.append(info["doc"])
        lines.append(f"- **Поля:** {', '.join(info['fields']) or NO_LINKS}")
        lines.append(f"- **Методы:** {', '.join(info['methods']) or NO_LINKS}")
        lines.append("")
    return lines


def statistics(classes: dict[str, dict], exceptions: dict[str, str]) -> list[str]:
    known = set(classes)
    pairs = sum(len(related(name, info, known)) for name, info in classes.items())
    return ["", "## Итоговая статистика", "", "| Показатель | Значение | Требование |", "|---|---|---|",
            f"| Классы | {len(classes)} | ≥ 50 |",
            f"| Поля | {sum(len(i['fields']) for i in classes.values())} | ≥ 150 |",
            f"| Поведения | {sum(len(i['methods']) for i in classes.values())} | ≥ 100 |",
            f"| Ассоциации | {pairs} | ≥ 30 |",
            f"| Исключения | {len(exceptions)} | ≥ 12 |"]


def exception_section(exceptions: dict[str, str]) -> list[str]:
    lines = ["", f"## Исключения ({len(exceptions)})", ""]
    lines += [f"- `{name}` — {doc}" for name, doc in exceptions.items()]
    return lines


def main() -> None:
    classes, exceptions = collect()
    body = HEADER.splitlines() + [""] + summary_table(classes) + detail_section(classes)
    body += exception_section(exceptions) + statistics(classes, exceptions)
    README_PATH.write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"Wrote {README_PATH}")


if __name__ == "__main__":
    main()
