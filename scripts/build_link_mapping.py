#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического обновления маппинга ссылок в базе знаний по географии.

Скрипт сканирует все .md файлы в папке src/, извлекает ссылки и обновляет:
- system/LINK_MAPPING.json - структурированный маппинг в формате JSON
- system/LINK_MAPPING.md - человекочитаемый маппинг в формате Markdown

Этот скрипт используется другими скриптами для работы с битыми ссылками.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Путь к папке с заметками (относительно корня проекта)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
SYSTEM_DIR = PROJECT_ROOT / "system"
LINK_MAPPING_JSON = SYSTEM_DIR / "LINK_MAPPING.json"
LINK_MAPPING_MD = SYSTEM_DIR / "LINK_MAPPING.md"


def extract_yaml_frontmatter(content: str) -> Dict[str, str]:
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


def extract_links(content: str) -> List[Tuple[str, str]]:
    """
    Извлекает все ссылки из markdown контента.
    Возвращает список кортежей (текст ссылки, имя файла).
    """
    links = []

    # Паттерн для ссылок в формате [текст](./filename.md) или [текст](filename.md)
    # Поддерживает относительные пути
    pattern = r'\[([^\]]+)\]\(\.?/?([^\)]+\.md)\)'

    for match in re.finditer(pattern, content):
        link_text = match.group(1)
        file_path = match.group(2)

        # Извлекаем только имя файла (без пути)
        filename = os.path.basename(file_path)

        # Нормализуем имя файла (убираем ./ если есть)
        filename = filename.replace("./", "")

        links.append((link_text, filename))

    return links


def scan_notes() -> Tuple[Dict[str, str], Dict[str, List[str]], Dict[str, List[str]], Dict[str, Set[str]]]:
    """
    Сканирует все заметки в папке src/.

    Возвращает:
    - existing_notes: словарь название -> имя файла
    - all_links: словарь имя файла -> список всех вариантов ссылок на него
    - broken_links: словарь имя файла (несуществующего) -> список вариантов названий
    - files_linking_to: словарь имя файла -> множество файлов, которые на него ссылаются
    """
    existing_notes = {}
    all_links = defaultdict(list)
    broken_links = defaultdict(list)
    files_linking_to = defaultdict(set)

    # Получаем список всех существующих файлов
    existing_files = set()
    if SRC_DIR.exists():
        for file_path in SRC_DIR.glob("*.md"):
            existing_files.add(file_path.name)

    # Сканируем все файлы
    if SRC_DIR.exists():
        for file_path in SRC_DIR.glob("*.md"):
            filename = file_path.name

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Ошибка при чтении {file_path}: {e}")
                continue

            # Извлекаем title из YAML frontmatter
            frontmatter = extract_yaml_frontmatter(content)
            title = frontmatter.get("title", "")

            if title:
                existing_notes[title] = filename

            # Извлекаем все ссылки из файла
            links = extract_links(content)

            for link_text, linked_filename in links:
                # Добавляем вариант ссылки
                all_links[linked_filename].append(link_text)

                # Отслеживаем, какие файлы ссылаются на какие
                files_linking_to[linked_filename].add(filename)

                # Проверяем, существует ли файл
                if linked_filename not in existing_files:
                    broken_links[linked_filename].append(link_text)

    # Удаляем дубликаты в списках
    for key in all_links:
        all_links[key] = list(dict.fromkeys(all_links[key]))  # Сохраняет порядок

    for key in broken_links:
        broken_links[key] = list(dict.fromkeys(broken_links[key]))

    # Преобразуем sets в lists для JSON сериализации
    files_linking_to_serializable = {
        key: sorted(list(value)) for key, value in files_linking_to.items()
    }

    return existing_notes, dict(all_links), dict(broken_links), files_linking_to_serializable


def generate_json_mapping(existing_notes: Dict[str, str],
                         all_links: Dict[str, List[str]],
                         broken_links: Dict[str, List[str]],
                         files_linking_to: Dict[str, List[str]]) -> Dict:
    """Генерирует структуру для JSON файла."""
    return {
        "existing_notes": existing_notes,
        "broken_links": broken_links,
        "all_links": all_links,
        "files_linking_to": files_linking_to,
        "statistics": {
            "total_existing_notes": len(existing_notes),
            "total_linked_files": len(all_links),
            "total_broken_links": len(broken_links),
            "total_broken_link_mentions": sum(len(links) for links in broken_links.values())
        }
    }


def generate_markdown_mapping(existing_notes: Dict[str, str],
                              all_links: Dict[str, List[str]],
                              broken_links: Dict[str, List[str]],
                              files_linking_to: Dict[str, List[str]]) -> str:
    """Генерирует Markdown файл с маппингом ссылок."""
    lines = [
        "# Маппинг ссылок в базе знаний",
        "",
        "Этот файл содержит полный маппинг всех ссылок в базе знаний:",
        "- Существующие заметки с их названиями",
        "- Все ссылки на заметки (существующие и несуществующие)",
        "- Варианты названий, которые ссылаются на одну и ту же заметку",
        "",
        "---",
        "",
        "## Существующие заметки",
        "",
        "| Название | Имя файла | Количество ссылок | Файлов ссылается |",
        "|----------|-----------|-------------------|------------------|"
    ]

    # Сортируем заметки по названию
    sorted_notes = sorted(existing_notes.items(), key=lambda x: x[0])

    for title, filename in sorted_notes:
        link_count = len(all_links.get(filename, []))
        files_count = len(files_linking_to.get(filename, []))
        status = "[OK]" if link_count > 0 else "[!]"
        lines.append(f"| {title} | `{filename}` | {link_count} {status} | {files_count} |")

    # Раздел с битыми ссылками
    if broken_links:
        lines.extend([
            "",
            "---",
            "",
            "## Битые ссылки (несуществующие файлы)",
            "",
            "| Имя файла | Варианты названий |",
            "|-----------|-------------------|"
        ])

        sorted_broken = sorted(broken_links.items(), key=lambda x: x[0])
        for filename, link_texts in sorted_broken:
            unique_texts = list(dict.fromkeys(link_texts))
            texts_str = ", ".join(f"`{text}`" for text in unique_texts[:5])
            if len(unique_texts) > 5:
                texts_str += f" ... (+{len(unique_texts) - 5} еще)"
            lines.append(f"| `{filename}` | {texts_str} |")

    # Статистика
    lines.extend([
        "",
        "---",
        "",
        "## Статистика",
        "",
        f"- Всего существующих заметок: {len(existing_notes)}",
        f"- Всего файлов со ссылками: {len(all_links)}",
        f"- Всего битых ссылок: {len(broken_links)}",
        f"- Всего упоминаний битых ссылок: {sum(len(links) for links in broken_links.values())}"
    ])

    return "\n".join(lines)


def main():
    """Основная функция скрипта."""
    print("Сканирование заметок...")
    existing_notes, all_links, broken_links, files_linking_to = scan_notes()

    print(f"Найдено заметок: {len(existing_notes)}")
    print(f"Найдено файлов со ссылками: {len(all_links)}")
    print(f"Найдено битых ссылок: {len(broken_links)}")

    # Генерируем JSON
    print("Генерация LINK_MAPPING.json...")
    json_mapping = generate_json_mapping(existing_notes, all_links, broken_links, files_linking_to)

    with open(LINK_MAPPING_JSON, "w", encoding="utf-8") as f:
        json.dump(json_mapping, f, ensure_ascii=False, indent=2)

    print("OK: LINK_MAPPING.json обновлен")

    # Генерируем Markdown
    print("Генерация LINK_MAPPING.md...")
    md_content = generate_markdown_mapping(existing_notes, all_links, broken_links, files_linking_to)

    with open(LINK_MAPPING_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("OK: LINK_MAPPING.md обновлен")
    print("\nГотово!")


if __name__ == "__main__":
    main()

