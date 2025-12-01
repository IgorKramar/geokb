#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный скрипт для управления базой знаний по географии.

Предоставляет единую точку входа для запуска всех скриптов автоматизации.
"""

import sys
import subprocess
from pathlib import Path

# Путь к папке со скриптами
SCRIPT_DIR = Path(__file__).parent / "scripts"

# Доступные команды
COMMANDS = {
    "link-mapping": {
        "script": "build_link_mapping.py",
        "description": "Обновить маппинг ссылок в базе знаний",
        "help": "Сканирует все .md файлы в папке src/, извлекает ссылки и обновляет LINK_MAPPING.json и LINK_MAPPING.md"
    },
    "poor-content": {
        "script": "find_poor_content_geography.py",
        "description": "Найти заметки по географии с бедным контентом",
        "help": "Находит заметки с topic: География, содержащие менее 5 строк реального контента"
    },
    "broken-links": {
        "script": "find_broken_links_geography.py",
        "description": "Найти битые ссылки по географии",
        "help": "Использует LINK_MAPPING.json для поиска битых ссылок, связанных с географией"
    },
    "create-note": {
        "script": "create_note.py",
        "description": "Создать новую заметку с timestamp-именованием",
        "help": "Создает заметку в формате YYYYMMDD_name.md. Используйте: kb.py create-note -n 'название' [-t 'шаблон'] [-f 'папка']",
        "needs_args": True
    },
    "all": {
        "script": None,
        "description": "Запустить все скрипты по порядку",
        "help": "Последовательно запускает: link-mapping, poor-content, broken-links"
    }
}


def print_usage():
    """Выводит справку по использованию скрипта."""
    print("Использование: python3 kb.py <команда>")
    print("\nДоступные команды:")
    print()
    for cmd, info in COMMANDS.items():
        print(f"  {cmd:15} - {info['description']}")
        if info.get('help'):
            print(f"                 {info['help']}")
    print()
    print("Примеры:")
    print("  python3 kb.py link-mapping              # Обновить маппинг ссылок")
    print("  python3 kb.py poor-content               # Найти бедные на контент заметки")
    print("  python3 kb.py broken-links               # Найти битые ссылки")
    print("  python3 kb.py create-note -n 'russia'    # Создать заметку")
    print("  python3 kb.py all                        # Запустить все скрипты")


def run_script(script_name: str, args: list = None) -> int:
    """
    Запускает скрипт и возвращает код возврата.

    Args:
        script_name: Имя скрипта
        args: Дополнительные аргументы для скрипта
    """
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        print(f"Ошибка: скрипт {script_name} не найден в {SCRIPT_DIR}")
        return 1

    try:
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            check=False
        )
        return result.returncode
    except Exception as e:
        print(f"Ошибка при запуске скрипта {script_name}: {e}")
        return 1


def main():
    """Основная функция скрипта."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command not in COMMANDS:
        print(f"Ошибка: неизвестная команда '{command}'")
        print()
        print_usage()
        sys.exit(1)

    cmd_info = COMMANDS[command]

    if command == "all":
        # Запускаем все скрипты по порядку
        print("Запуск всех скриптов...\n")

        scripts_order = [
            ("link-mapping", "build_link_mapping.py"),
            ("poor-content", "find_poor_content_geography.py"),
            ("broken-links", "find_broken_links_geography.py")
        ]

        for cmd_name, script_name in scripts_order:
            print(f"[{cmd_name}] Запуск {script_name}...")
            result = run_script(script_name)
            if result != 0:
                print(f"[{cmd_name}] Ошибка при выполнении (код: {result})")
                sys.exit(result)
            print()

        print("Все скрипты выполнены успешно!")
    else:
        # Запускаем один скрипт
        script_name = cmd_info["script"]
        print(f"Запуск: {cmd_info['description']}")
        print(f"Скрипт: {script_name}\n")

        # Если скрипт требует аргументы, передаем их
        args = None
        if cmd_info.get("needs_args") and len(sys.argv) > 2:
            args = sys.argv[2:]

        result = run_script(script_name, args)
        if result != 0:
            sys.exit(result)


if __name__ == "__main__":
    main()

