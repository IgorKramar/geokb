#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания заготовок заметок о странах из XML файла.

Парсит XML файл со списком стран и создает заготовки заметок для каждой страны.
"""

import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Пути
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
XML_FILE = Path(r"c:\Users\ikramar\Downloads\Страны.xml")
TIMESTAMP = datetime.now().strftime("%Y%m%d")


def transliterate_to_filename(name: str) -> str:
    """
    Преобразует название страны в имя файла.
    Использует английское название, если доступно, иначе транслитерирует русское.
    """
    # Убираем специальные символы и приводим к нижнему регистру
    name = name.lower().strip()
    # Заменяем пробелы и специальные символы на дефисы
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name.strip('-')


def create_country_note(country_data: dict, timestamp: str) -> Path:
    """
    Создает заготовку заметки о стране.
    
    Args:
        country_data: Словарь с данными о стране
        timestamp: Timestamp для имени файла
    
    Returns:
        Path к созданному файлу
    """
    # Используем английское название для имени файла
    english_name = country_data.get('english', '').strip()
    if not english_name:
        # Если английского названия нет, используем русское
        russian_name = country_data.get('name', '').strip()
        filename_base = transliterate_to_filename(russian_name)
    else:
        filename_base = transliterate_to_filename(english_name)
    
    # Создаем имя файла
    filename = f"{timestamp}_{filename_base}.md"
    filepath = SRC_DIR / filename
    
    # Проверяем, существует ли файл с другим timestamp (старая заметка)
    # Ищем файлы с таким же названием страны
    existing_file = None
    if not filepath.exists():
        # Ищем существующие файлы с похожим названием
        for existing_path in SRC_DIR.glob(f"*_{filename_base}.md"):
            existing_file = existing_path
            break
    
    # Получаем данные
    name = country_data.get('name', '').strip()
    fullname = country_data.get('fullname', '').strip()
    english = country_data.get('english', '').strip()
    alpha2 = country_data.get('alpha2', '').strip()
    alpha3 = country_data.get('alpha3', '').strip()
    iso = country_data.get('iso', '').strip()
    location = country_data.get('location', '').strip()
    location_precise = country_data.get('location-precise', '').strip()
    
    # Определяем категорию на основе location
    category = "География / Страны"
    if location:
        category = f"География / Страны / {location}"
    
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
    
    codes_text = "\n".join(codes_section) if codes_section else ""
    
    # Создаем содержимое заметки
    content = f"""---
title: {name}
type: Evergreen
status: TODO
category: {category}
topic: География
---

# {name}

{f"## {fullname}" if fullname and fullname != name else ""}

## Основная информация

{f"**Полное название:** {fullname}" if fullname and fullname != name else ""}
{f"**Часть света:** {location}" if location else ""}
{f"**Расположение:** {location_precise}" if location_precise else ""}
{f"\n{codes_text}" if codes_text else ""}

## Признаки для GeoGuessr

*Заполняется пользователем*

## Географические особенности

*Заполняется пользователем*

## Культурные особенности

*Заполняется пользователем*

## Связанные заметки

*Ссылки на связанные заметки добавляются по мере наполнения*

"""
    
    # Если есть существующий файл с другим timestamp, обновляем его
    if existing_file and existing_file != filepath:
        # Читаем существующий файл
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Проверяем, есть ли уже коды в файле
        has_codes = 'Alpha-2 код' in existing_content or 'Название на английском' in existing_content
        
        if not has_codes:
            # Добавляем коды в раздел "Основная информация"
            # Ищем раздел "Основная информация" и добавляем коды после него
            if '## Основная информация' in existing_content:
                # Находим позицию после "Основная информация"
                info_section_start = existing_content.find('## Основная информация')
                # Находим следующий раздел
                next_section = existing_content.find('\n## ', info_section_start + 1)
                if next_section == -1:
                    next_section = len(existing_content)
                
                # Вставляем коды перед следующим разделом
                before_section = existing_content[:next_section].rstrip()
                after_section = existing_content[next_section:]
                
                # Добавляем коды
                codes_insert = f"\n{codes_text}" if codes_text else ""
                updated_content = before_section + codes_insert + "\n\n" + after_section.lstrip()
                
                # Записываем обновленный файл
                with open(existing_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"  Обновлен: {existing_file.name}")
                return existing_file
    
    # Записываем файл (перезаписываем, если существует)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath


def parse_xml_and_create_notes(xml_path: Path, timestamp: str):
    """
    Парсит XML файл и создает заметки для всех стран.
    
    Returns:
        Словарь с данными о странах, организованными по регионам
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    countries_by_region = defaultdict(list)
    created_files = []
    
    for country in root.findall('country'):
        country_data = {}
        for child in country:
            tag = child.tag
            text = child.text.strip() if child.text else ''
            # Обрабатываем HTML entities
            text = text.replace('&#160;', ' ')
            country_data[tag] = text
        
        # Пропускаем страны без названия
        if not country_data.get('name'):
            continue
        
        # Создаем заметку
        try:
            filepath = create_country_note(country_data, timestamp)
            created_files.append(filepath)
            
            # Организуем по регионам для MOC
            location = country_data.get('location', 'Другое').strip()
            if not location:
                location = 'Другое'
            
            countries_by_region[location].append({
                'name': country_data.get('name', ''),
                'filename': filepath.name,
                'location_precise': country_data.get('location-precise', '').strip()
            })
            
        except Exception as e:
            print(f"Ошибка при создании заметки для {country_data.get('name', 'unknown')}: {e}")
    
    return countries_by_region, created_files


def update_moc_countries(countries_by_region: dict):
    """
    Обновляет MOC - Страны с новыми заметками.
    """
    moc_file = SRC_DIR / "20250101_moc-countries.md"
    
    # Читаем существующий MOC
    if moc_file.exists():
        with open(moc_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = """---
title: MOC - Страны
type: Evergreen
status: IN PROGRESS
category: Навигация / Страны
topic: География
---

# MOC - Страны

Навигация по всем заметкам о странах.

"""
    
    # Создаем новый контент MOC
    lines = [
        "---",
        "title: MOC - Страны",
        "type: Evergreen",
        "status: IN PROGRESS",
        "category: Навигация / Страны",
        "topic: География",
        "---",
        "",
        "# MOC - Страны",
        "",
        "Навигация по всем заметкам о странах.",
        ""
    ]
    
    # Сортируем регионы
    region_order = ['Европа', 'Азия', 'Америка', 'Африка', 'Океания', 'Антарктика', 'Другое']
    
    for region in region_order:
        if region not in countries_by_region:
            continue
        
        countries = countries_by_region[region]
        if not countries:
            continue
        
        # Добавляем заголовок региона
        lines.append(f"## {region}")
        lines.append("")
        
        # Сортируем страны по названию
        countries_sorted = sorted(countries, key=lambda x: x['name'])
        
        for country in countries_sorted:
            filename = country['filename']
            name = country['name']
            lines.append(f"- [{name}](./{filename})")
        
        lines.append("")
    
    # Добавляем остальные регионы, если есть
    for region in sorted(countries_by_region.keys()):
        if region not in region_order:
            countries = countries_by_region[region]
            if countries:
                lines.append(f"## {region}")
                lines.append("")
                countries_sorted = sorted(countries, key=lambda x: x['name'])
                for country in countries_sorted:
                    filename = country['filename']
                    name = country['name']
                    lines.append(f"- [{name}](./{filename})")
                lines.append("")
    
    # Записываем обновленный MOC
    with open(moc_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"OK: Обновлен {moc_file}")


def main():
    """Основная функция скрипта."""
    if not XML_FILE.exists():
        print(f"Ошибка: файл {XML_FILE} не найден!")
        return
    
    print(f"Парсинг XML файла: {XML_FILE}")
    print(f"Timestamp: {TIMESTAMP}")
    print()
    
    # Парсим XML и создаем заметки
    countries_by_region, created_files = parse_xml_and_create_notes(XML_FILE, TIMESTAMP)
    
    print(f"Создано заметок: {len(created_files)}")
    print()
    
    # Обновляем MOC
    print("Обновление MOC - Страны...")
    update_moc_countries(countries_by_region)
    
    # Статистика по регионам
    print()
    print("Статистика по регионам:")
    for region in sorted(countries_by_region.keys()):
        count = len(countries_by_region[region])
        print(f"  {region}: {count} стран")
    
    print()
    print("Готово!")


if __name__ == "__main__":
    main()

