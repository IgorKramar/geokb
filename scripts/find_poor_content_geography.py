#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для поиска заметок по географии с бедным контентом.

Скрипт сканирует все .md файлы в папке src/, находит заметки с флагом topic: География
и определяет, какие из них содержат менее указанного количества строк реального 
контента (не считая заголовки и frontmatter).

Результат сохраняется в system/GEOGRAPHY_POOR_CONTENT.md
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Пути (относительно корня проекта)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
SYSTEM_DIR = PROJECT_ROOT / "system"
OUTPUT_FILE = SYSTEM_DIR / "GEOGRAPHY_POOR_CONTENT.md"
MIN_CONTENT_LINES = 5  # Минимальное количество строк контента


def extract_yaml_frontmatter(content: str) -> dict:
    """Извлекает YAML frontmatter из начала файла."""
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[1].strip()
            for line in yaml_content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter


def find_poor_content_files():
    """
    Находит все заметки по географии с бедным контентом.

    Возвращает словарь: количество_строк -> список файлов
    """
    poor_content_files = defaultdict(list)

    if not SRC_DIR.exists():
        print(f"Папка {SRC_DIR} не существует!")
        return poor_content_files

    for file_path in SRC_DIR.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Проверяем наличие topic: География
            if 'topic: География' not in content:
                continue

            # Убираем frontmatter
            lines = content.split('\n')
            in_frontmatter = False
            content_lines = []

            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                if not in_frontmatter:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        content_lines.append(stripped)

            # Считаем количество строк с реальным контентом (не только заголовки)
            non_header_lines = [l for l in content_lines if not l.startswith('#')]

            # Если меньше указанного количества строк контента, считаем бедной
            if len(non_header_lines) < MIN_CONTENT_LINES:
                rel_path = file_path.relative_to(SRC_DIR)
                poor_content_files[len(non_header_lines)].append(str(rel_path))
        except Exception as e:
            print(f"Ошибка при обработке {file_path}: {e}")

    return poor_content_files


def generate_output(poor_content_files: dict) -> str:
    """Генерирует Markdown файл с результатами."""
    output_lines = []
    output_lines.append("# Заметки по географии с бедным контентом\n")
    output_lines.append(
        f"Список заметок, содержащих менее {MIN_CONTENT_LINES} строк реального контента "
        "(не считая заголовки и frontmatter).\n"
    )
    output_lines.append("Отсортировано по количеству строк контента (от меньшего к большему).\n")

    total_files = sum(len(files) for files in poor_content_files.values())
    output_lines.append(f"\n**Всего найдено: {total_files} заметок**\n")

    # Сортируем по количеству строк контента
    for lines_count in sorted(poor_content_files.keys()):
        files = sorted(poor_content_files[lines_count])
        count = len(files)
        word = "строка" if lines_count == 1 else "строки" if lines_count < 5 else "строк"
        output_lines.append(f"\n## {lines_count} {word} контента ({count} заметок)\n")
        for file in files:
            output_lines.append(f"- `{file}`")

    return "\n".join(output_lines)


def main():
    """Основная функция скрипта."""
    print("Поиск заметок по географии с бедным контентом...")
    poor_content_files = find_poor_content_files()

    total_files = sum(len(files) for files in poor_content_files.values())
    print(f"Найдено заметок с бедным контентом: {total_files}")

    if total_files == 0:
        print("Заметок с бедным контентом не найдено!")
        return

    # Генерируем вывод
    print(f"Генерация {OUTPUT_FILE}...")
    output_content = generate_output(poor_content_files)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f"OK: {OUTPUT_FILE} обновлен")
    print("\nГотово!")


if __name__ == "__main__":
    main()

