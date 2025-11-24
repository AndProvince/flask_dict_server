# useless calendar 2026
# by Andrei Ponomarev

import datetime
import calendar
import random
import io
from typing import Dict, List, Union
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def generate_calendar(year: Union[int, None] = None, hide_probability: float = 0.0) -> Dict[str, List[List[Union[int, str]]]]:
    """
    Генерирует календарь на указанный год в виде словаря:
    ключи – месяцы (английские),
    значения – список недель, каждая неделя – список из 7 элементов (числа или пробелы).
    :param year: Год (по умолчанию следующий за текущим)
    :param hide_probability: Вероятность скрытия номера дня (0 = не скрывать, 1 = скрыть всё)
    """
    if year is None:
        year = datetime.datetime.now().year + 1

    months = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    ]

    calendar.setfirstweekday(calendar.MONDAY)
    result: Dict[str, List[List[Union[int, str]]]] = {}

    for month_index, month_name in enumerate(months, start=1):
        month_calendar = calendar.monthcalendar(year, month_index)

        formatted_weeks = []
        for week in month_calendar:
            formatted_week = []
            for day in week:
                if day == 0:
                    formatted_week.append(" ")
                else:
                    # С вероятностью hide_probability скрываем день
                    if random.random() < hide_probability:
                        formatted_week.append(" ")
                    else:
                        formatted_week.append(day)
            formatted_weeks.append(formatted_week)

        result[month_name] = formatted_weeks

    return result


def createLines(clndr, year, hide_probability):
    lines = []
    header_width = 66

    # Год
    lines.append(f"{year}".center(header_width))
    lines.append("")

    months = list(clndr.keys())

    for quarter_start in range(0, 12, 3):
        month_names = months[quarter_start:quarter_start + 3]
        lines.append("".join(name.center(25) for name in month_names))

        month_weeks = [clndr[name] for name in month_names]
        max_weeks = max(len(w) for w in month_weeks)

        for weeks in month_weeks:
            while len(weeks) < max_weeks:
                weeks.append([" " for _ in range(7)])

        for w in range(max_weeks):
            row = ""
            for m in month_weeks:
                week = m[w]
                row += " ".join(f"{day:>2}" if isinstance(day, int) else "  " for day in week).ljust(25)
            lines.append(row)
        lines.append("")

    # Надпись про скрытые дни
    hidden_percent = int(hide_probability * 100)
    hidden_text = f"~ {hidden_percent}% of days missing in action"
    lines.append(hidden_text.rjust(header_width))
    lines.append("")

    return "\n".join(lines)


def create_calendar_image(lines: str,
                          width: int,
                          height: int,
                          bgcolor: str = 'white',
                          ftcolor: str = 'black',
                          base_ftsize: int = 20,
                          font_path: str = Path(__file__).parent / 'static' / 'CartographCF-Regular.otf',
                          margin_ratio: float = 0.1) -> None:
    """
    Рисует календарь так, чтобы он занимал максимум пространства изображения.

    :param lines: Текст календаря (с годом в первой строке)
    :param width: Ширина изображения
    :param height: Высота изображения
    :param bgcolor: Цвет фона
    :param ftcolor: Цвет текста
    :param base_ftsize: Базовый размер шрифта (будет масштабироваться)
    :param margin_ratio: Доля отступов (0.1 = 10% сверху/снизу/сбоку)
    """
    lines_list = lines.split("\n")
    year_text = lines_list[0].strip()
    calendar_text = "\n".join(lines_list[1:])

    img = Image.new('RGB', (width, height), bgcolor)
    draw = ImageDraw.Draw(img)

    # Определяем доступное пространство
    max_w = int(width * (1 - margin_ratio * 2))
    max_h = int(height * (1 - margin_ratio * 2))

    # Ищем оптимальный размер шрифта
    ftsize = base_ftsize
    while True:
        font = ImageFont.truetype(font_path, ftsize)
        year_font = ImageFont.truetype(font_path, int(3 * ftsize))

        _, _, yw, yh = draw.textbbox((0, 0), year_text, font=year_font)
        _, _, cw, ch = draw.textbbox((0, 0), calendar_text, font=font)

        total_height = yh + 20 + ch  # отступ между годом и календарем
        total_width = max(cw, yw)

        if total_width < max_w and total_height < max_h:
            ftsize += 2  # увеличиваем пока помещается
        else:
            ftsize -= 2  # возвращаем на последний подходящий
            break

    # Пересоздаём шрифты с оптимальным размером
    font = ImageFont.truetype(font_path, ftsize)
    year_font = ImageFont.truetype(font_path, int(3 * ftsize))

    _, _, yw, yh = draw.textbbox((0, 0), year_text, font=year_font)
    _, _, cw, ch = draw.textbbox((0, 0), calendar_text, font=font)

    year_x = width / 2 - yw / 2
    year_y = (height - (yh + 20 + ch)) / 2
    text_x = width / 2 - cw / 2
    text_y = year_y + yh + 20

    draw.text((year_x, year_y), year_text, font=year_font, fill=ftcolor)
    draw.multiline_text((text_x, text_y), calendar_text, font=font, fill=ftcolor, spacing=5)

    # filename = f"uncalendar_{year_text}.png"
    # img.save(filename)
    # img.show()

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


if __name__ == '__main__':
    year = 2026
    hide_probability = random.random()
    clndr = generate_calendar(year, hide_probability=hide_probability)
    lines = createLines(clndr, year, hide_probability)
    print(lines)
    create_calendar_image(lines, 3840, 2160)