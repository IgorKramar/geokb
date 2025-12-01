#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания заметок по географии с timestamp-именованием.

Создает заметки в формате YYYYMMDD_name.md с использованием шаблонов из .obsidian/templates/.
Автоматически добавляет флаг 'topic: География' в YAML FrontMatter.
Работает на всех платформах (Windows, Linux, macOS).
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Пути (относительно корня проекта)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / ".obsidian" / "templates"
DEFAULT_FOLDER = PROJECT_ROOT / "src"
DEFAULT_TEMPLATE = "template-evergreen"


def get_timestamp(format_str: str = "%Y%m%d") -> str:
    """
    Получает актуальный timestamp в указанном формате.

    Args:
        format_str: Формат даты (по умолчанию YYYYMMDD)

    Returns:
        Строка с timestamp
    """
    return datetime.now().strftime(format_str)


def replace_placeholders(content: str, name: str, timestamp: str) -> str:
    """
    Заменяет плейсхолдеры в шаблоне на актуальные значения.

    Args:
        content: Содержимое шаблона
        name: Название заметки
        timestamp: Timestamp в формате YYYYMMDD

    Returns:
        Содержимое с замененными плейсхолдерами
    """
    now = datetime.now()

    replacements = {
        r'\{\{title\}\}': name,
        r'\{\{date:YYYYMMDD\}\}': timestamp,
        r'\{\{date:YYYYMMDDHHmm\}\}': now.strftime("%Y%m%d%H%M"),
        r'\{\{date:YYYY\}\}': now.strftime("%Y"),
        r'\{\{date:YYYY-MM-DD\}\}': now.strftime("%Y-%m-%d"),
        r'\{\{date:MM-DD\}\}': now.strftime("%m-%d"),
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    return content


def get_default_frontmatter(name: str, template_name: str) -> str:
    """
    Создает базовый FrontMatter, если шаблон не найден.

    Args:
        name: Название заметки
        template_name: Имя шаблона (для определения типа)

    Returns:
        Строка с FrontMatter и заголовком
    """
    # Определяем type и status по имени шаблона
    note_type = "Evergreen"
    note_status = "IN PROGRESS"
    note_category = "География"

    template_lower = template_name.lower()
    if "literature" in template_lower:
        note_type = "Literature"
        note_status = "IN PROGRESS"
    elif "project" in template_lower:
        note_type = "Project"
        note_status = "IN PROGRESS"

    return f"""---
title: {name}
type: {note_type}
status: {note_status}
category: {note_category}
topic: География
---

# {name}

"""


def create_note(name: str, template: str = None, folder: Path = None) -> Path:
    """
    Создает новую заметку по географии.

    Args:
        name: Название заметки
        template: Имя шаблона (без расширения .md)
        folder: Папка для заметки (по умолчанию src/)

    Returns:
        Path к созданному файлу

    Raises:
        FileExistsError: Если файл уже существует
        FileNotFoundError: Если папка шаблонов не найдена
    """
    if folder is None:
        folder = DEFAULT_FOLDER

    # Получаем актуальный timestamp
    timestamp = get_timestamp()

    # Создаем имя файла
    filename = f"{timestamp}_{name}.md"
    filepath = folder / filename

    # Проверяем, не существует ли уже файл
    if filepath.exists():
        raise FileExistsError(f"Файл уже существует: {filepath}")

    # Создаем папку, если её нет
    folder.mkdir(parents=True, exist_ok=True)

    # Если указан шаблон, используем его
    if template:
        template_path = TEMPLATES_DIR / f"{template}.md"

        if template_path.exists():
            # Читаем шаблон
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Заменяем плейсхолдеры
            content = replace_placeholders(template_content, name, timestamp)

            # Убеждаемся, что в YAML FrontMatter есть topic: География
            if 'topic: География' not in content and 'topic:География' not in content:
                # Добавляем topic: География в frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        if 'topic:' not in frontmatter:
                            # Добавляем topic: География перед закрывающим ---
                            frontmatter = frontmatter.rstrip() + '\ntopic: География\n'
                            content = f"---{frontmatter}---{parts[2]}"

            # Записываем в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ Создана заметка с шаблоном '{template}': {filepath}")
        else:
            # Шаблон не найден, создаем базовый FrontMatter
            content = get_default_frontmatter(name, template)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"⚠ Шаблон '{template}' не найден. Создан файл с базовым FrontMatter: {filepath}")
    else:
        # Без шаблона - FrontMatter с дефолтными значениями
        content = get_default_frontmatter(name, DEFAULT_TEMPLATE)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ Создана заметка: {filepath}")

    return filepath


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Создает заметку с timestamp-именованием",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python3 create_note.py -n "russia" -t "template-evergreen"
  python3 create_note.py -n "moscow" -t "template-evergreen"
  python3 create_note.py -n "road-signs-europe" -t "template-evergreen"
  
Примечание: Флаг 'topic: География' автоматически добавляется в YAML FrontMatter.
        """
    )

    parser.add_argument(
        '-n', '--name',
        required=True,
        help='Название заметки (обязательно)'
    )

    parser.add_argument(
        '-t', '--template',
        default=DEFAULT_TEMPLATE,
        help=f'Шаблон для использования (по умолчанию: {DEFAULT_TEMPLATE})'
    )

    parser.add_argument(
        '-f', '--folder',
        default=None,
        help='Папка для заметки (по умолчанию: src/)'
    )

    args = parser.parse_args()

    try:
        folder = None
        if args.folder:
            folder = PROJECT_ROOT / args.folder

        filepath = create_note(args.name, args.template, folder)
        print(f"\nФайл готов к использованию: {filepath}")

        # Пытаемся открыть в Obsidian (опционально)
        try:
            vault_name = PROJECT_ROOT.name
            file_relative = filepath.relative_to(PROJECT_ROOT)
            obsidian_url = f"obsidian://open?vault={vault_name}&file={file_relative.as_posix()}"
            print(f"\nОткрыть в Obsidian: {obsidian_url}")
        except Exception:
            pass  # Игнорируем ошибки при открытии в Obsidian

    except FileExistsError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

