#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления существующих заметок о странах, добавляя коды и английские названия из XML.
"""

import xml.etree.ElementTree as ET
import re
from pathlib import Path

# Пути
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
XML_FILE = Path(r"c:\Users\ikramar\Downloads\Страны.xml")


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


def update_country_note(filepath: Path, country_data: dict) -> bool:
    """
    Обновляет заметку о стране, добавляя коды и английское название.
    
    Returns:
        True если файл был обновлен, False если нет
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка при чтении {filepath}: {e}")
        return False
    
    # Извлекаем title из YAML
    frontmatter = extract_yaml_frontmatter(content)
    title = frontmatter.get('title', '').strip()
    
    # Проверяем, что это заметка о нужной стране
    country_name = country_data.get('name', '').strip()
    if title != country_name:
        return False
    
    # Проверяем, есть ли уже коды
    if 'Alpha-2 код' in content or 'Название на английском' in content:
        # Коды уже есть, пропускаем
        return False
    
    # Получаем данные из XML
    english = country_data.get('english', '').strip()
    alpha2 = country_data.get('alpha2', '').strip()
    alpha3 = country_data.get('alpha3', '').strip()
    iso = country_data.get('iso', '').strip()
    
    # Формируем раздел с кодами
    codes_section = []
    if english:
        codes_section.append(f"**Название на английском:** {english}")
    if alpha2:
        codes_section.append(f"**Alpha-2 код:** {alpha2}")
    if alpha3:
        codes_section.append(f"**Alpha-3 код:** {alpha3}")
    if iso:
        codes_section.append(f"**ISO код:** {iso}")
    
    if not codes_section:
        return False
    
    codes_text = "\n".join(codes_section)
    
    # Находим раздел "Основная информация"
    info_section_pattern = r'## Основная информация\s*\n'
    match = re.search(info_section_pattern, content)
    
    if not match:
        # Раздел не найден, добавляем в конец перед "Признаки для GeoGuessr"
        features_pattern = r'## Признаки для GeoGuessr'
        features_match = re.search(features_pattern, content)
        if features_match:
            pos = features_match.start()
            before = content[:pos].rstrip()
            after = content[pos:]
            updated_content = before + f"\n\n{codes_text}\n" + after
        else:
            # Не нашли раздел, просто добавляем в конец
            updated_content = content.rstrip() + f"\n\n{codes_text}\n"
    else:
        # Находим конец раздела "Основная информация" (следующий раздел или конец)
        info_start = match.end()
        next_section_match = re.search(r'\n## ', content[info_start:])
        
        if next_section_match:
            # Есть следующий раздел
            next_section_pos = info_start + next_section_match.start()
            before = content[:next_section_pos].rstrip()
            after = content[next_section_pos:]
            updated_content = before + f"\n{codes_text}\n" + after
        else:
            # Нет следующего раздела, добавляем в конец
            updated_content = content.rstrip() + f"\n{codes_text}\n"
    
    # Записываем обновленный файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return True


def main():
    """Основная функция скрипта."""
    if not XML_FILE.exists():
        print(f"Ошибка: файл {XML_FILE} не найден!")
        return
    
    print(f"Парсинг XML файла: {XML_FILE}")
    print()
    
    # Парсим XML
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    
    # Создаем словарь стран по названию
    countries_dict = {}
    for country in root.findall('country'):
        country_data = {}
        for child in country:
            tag = child.tag
            text = child.text.strip() if child.text else ''
            text = text.replace('&#160;', ' ')
            country_data[tag] = text
        
        name = country_data.get('name', '').strip()
        if name:
            countries_dict[name] = country_data
    
    print(f"Загружено стран из XML: {len(countries_dict)}")
    print()
    
    # Обновляем все заметки о странах
    updated_count = 0
    skipped_count = 0
    
    for filepath in SRC_DIR.glob("*.md"):
        # Пропускаем MOC файлы
        if 'moc' in filepath.name.lower():
            continue
        
        # Читаем frontmatter
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        
        frontmatter = extract_yaml_frontmatter(content)
        title = frontmatter.get('title', '').strip()
        topic = frontmatter.get('topic', '').strip()
        
        # Проверяем, что это заметка о стране по географии
        if topic != 'География':
            continue
        
        # Ищем соответствующую страну в XML
        if title in countries_dict:
            country_data = countries_dict[title]
            if update_country_note(filepath, country_data):
                updated_count += 1
                print(f"  Обновлен: {filepath.name}")
            else:
                skipped_count += 1
    
    print()
    print(f"Обновлено заметок: {updated_count}")
    print(f"Пропущено (коды уже есть): {skipped_count}")
    print()
    print("Готово!")


if __name__ == "__main__":
    main()

