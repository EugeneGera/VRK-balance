from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Optional, Union


def round_to_significant(num: Optional[Union[int, float, Decimal]], digits: int = 2) -> Optional[Union[int, float, Decimal]]:
    """
    Округление "как в математике" до `digits` знаков после запятой.
    По умолчанию — 2 знака.
    Используем Decimal + ROUND_HALF_UP, чтобы избежать проблем с float.
    """
    if num is None:
        return None

    # целые оставляем как есть — JSON всё равно можно отрисовать с .toFixed(2) на фронте
    if isinstance(num, int):
        return num

    # строгий конверт в Decimal по строке
    d = Decimal(str(num))

    if digits <= 0:
        quant = Decimal("1")
    else:
        quant = Decimal("0." + "0" * (digits - 1) + "1")

    rounded = d.quantize(quant, rounding=ROUND_HALF_UP)

    # если получилось целое — возвращаем int, иначе float
    if rounded == rounded.to_integral():
        return int(rounded)
    return float(rounded)


def safe_none_sum(*args):
    numbers = []
    for arg in args:
        if arg is not None:
            numbers.append(arg)
    if len(numbers) == 0:
        return None
    return sum(numbers)


def safe_percent(a, b):
    if a is None:
        a = 0
    if b is None or b == 0:
        return b

    return a / b * 100


def none_to_zero(item: Any) -> float:
    return 0 if item is None else item


NumericType = Union[int, float, Decimal]


def zero_to_none(item: NumericType) -> Optional[Any]:
    if not (isinstance(item, int) or isinstance(item, float), isinstance(item, Decimal)) or item is None:
        # print(f'WHAT THE {item}')
        return item
    if item == 0:
        return None
    return item


MONTHS = ["Январь", "Февраль", "Март", "Апрель",
          "Май", "Июнь", "Июль", "Август",
          "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
