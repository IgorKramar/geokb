#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для поиска битых ссылок по географии.

Скрипт использует LINK_MAPPING.json, созданный build_link_mapping.py,
и фильтрует битые ссылки, связанные с географией (файлы в src/).

Результат сохраняется в system/GEOGRAPHY_BROKEN_LINKS.md
"""

import json
from pathlib import Path

# Пути к файлам (относительно корня проекта)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SYSTEM_DIR = PROJECT_ROOT / "system"
SRC_DIR = PROJECT_ROOT / "src"
LINK_MAPPING_JSON = SYSTEM_DIR / "LINK_MAPPING.json"
OUTPUT_FILE = SYSTEM_DIR / "GEOGRAPHY_BROKEN_LINKS.md"


def find_broken_links_geography():
    """
    Находит все битые ссылки по географии из LINK_MAPPING.json.

    Возвращает словарь: имя_файла -> список вариантов названий
    """
    if not LINK_MAPPING_JSON.exists():
        print(f"Файл {LINK_MAPPING_JSON} не найден!")
        print("Сначала запустите build_link_mapping.py для создания маппинга ссылок.")
        return {}

    # Читаем JSON файл
    with open(LINK_MAPPING_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Получаем список всех существующих файлов в src/
    existing_files = set()
    if SRC_DIR.exists():
        for file_path in SRC_DIR.glob("*.md"):
            existing_files.add(file_path.name)

    # Фильтруем битые ссылки (те, которых нет в src/)
    broken_links_geography = {}
    for filename, link_texts in data.get("broken_links", {}).items():
        # Проверяем, что файл должен быть в src/ (не в других папках)
        if filename not in existing_files:
            broken_links_geography[filename] = link_texts

    return broken_links_geography


def generate_output(broken_links_geography: dict) -> str:
    """Генерирует Markdown файл с результатами."""
    # Сортируем по количеству упоминаний
    sorted_broken = sorted(
        broken_links_geography.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    total_links = len(broken_links_geography)
    total_mentions = sum(len(links) for links in broken_links_geography.values())

    output_lines = [
        "# Битые ссылки по географии",
        "",
        "Список заметок, на которые есть ссылки в базе знаний, но сами файлы не существуют.",
        "",
        f"**Статистика:**",
        f"- Всего битых ссылок: {total_links}",
        f"- Всего упоминаний битых ссылок: {total_mentions}",
        "",
        "---",
        "",
        "## Битые ссылки (отсортировано по количеству упоминаний)",
        "",
        "| Имя файла | Количество упоминаний | Варианты названий |",
        "|-----------|----------------------|-------------------|"
    ]

    for filename, link_texts in sorted_broken:
        unique_texts = list(dict.fromkeys(link_texts))
        texts_str = ", ".join(f"`{text}`" for text in unique_texts[:10])
        if len(unique_texts) > 10:
            texts_str += f" ... (+{len(unique_texts) - 10} еще)"
        count = len(link_texts)
        output_lines.append(f"| `{filename}` | {count} | {texts_str} |")

    return "\n".join(output_lines)


def main():
    """Основная функция скрипта."""
    print("Поиск битых ссылок по географии...")

    # Проверяем, существует ли маппинг
    if not LINK_MAPPING_JSON.exists():
        print(f"Файл {LINK_MAPPING_JSON} не найден!")
        print("Сначала запустите build_link_mapping.py для создания маппинга ссылок.")
        return

    broken_links_geography = find_broken_links_geography()

    total_links = len(broken_links_geography)
    total_mentions = sum(len(links) for links in broken_links_geography.values())

    print(f"Найдено битых ссылок по географии: {total_links}")
    print(f"Всего упоминаний битых ссылок: {total_mentions}")

    if total_links == 0:
        print("Битых ссылок по географии не найдено!")
        return

    # Генерируем вывод
    print(f"Генерация {OUTPUT_FILE}...")
    output_content = generate_output(broken_links_geography)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"OK: {OUTPUT_FILE} обновлен")
    print("\nГотово!")


if __name__ == "__main__":
    main()

