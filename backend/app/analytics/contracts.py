from dataclasses import dataclass
from decimal import Decimal, localcontext
from typing import Optional, Tuple


class AnalyticsError(Exception):
    def __init__(self, code, message, status=400, details=None):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status
        self.details = details or {}


def names(value, field_name):
    if value is None or value == [] or value == ():
        return ()
    if isinstance(value, str):
        value = value.split(',')
    if not isinstance(value, (list, tuple)) or len(value) > 100:
        raise AnalyticsError('invalid_filter', 'Фильтр должен быть списком не более 100 значений.', details={'field': field_name})
    if any(not isinstance(item, str) or not item.strip() or len(item) > 255 for item in value):
        raise AnalyticsError('invalid_filter', 'Названия фильтров должны быть непустыми строками.', details={'field': field_name})
    return tuple(sorted(set(item.strip() for item in value)))


def integer(value, field_name, minimum, maximum):
    if isinstance(value, bool) or value is None:
        raise AnalyticsError('invalid_period', 'Укажите целочисленный период.', details={'field': field_name})
    try:
        parsed = int(value)
    except (ValueError, TypeError, OverflowError):
        raise AnalyticsError('invalid_period', 'Параметр периода должен быть целым числом.', details={'field': field_name})
    if str(parsed) != str(value).strip() or not minimum <= parsed <= maximum:
        raise AnalyticsError('invalid_period', 'Параметр периода вне допустимых границ.', details={'field': field_name, 'minimum': minimum, 'maximum': maximum})
    return parsed


@dataclass(frozen=True)
class Period:
    year: int
    month_start: int
    month_end: int

    @classmethod
    def parse(cls, data):
        if not isinstance(data, dict) or set(data) - {'year', 'month_start', 'month_end'}:
            raise AnalyticsError('invalid_period', 'Период содержит неподдерживаемые параметры.')
        year = integer(data.get('year'), 'year', 1, 9999)
        start = integer(data.get('month_start'), 'month_start', 1, 12)
        end = integer(data.get('month_end', start), 'month_end', 1, 12)
        if end < start:
            raise AnalyticsError('invalid_period', 'Конец периода раньше начала. Диапазон должен находиться внутри одного года.')
        return cls(year, start, end)

    @property
    def months(self):
        return tuple(range(self.month_start, self.month_end + 1))

    def as_dict(self):
        return dict(year=self.year, month_start=self.month_start, month_end=self.month_end)


@dataclass(frozen=True)
class QuerySpec:
    period: Period
    products: Tuple[str, ...] = ()
    categories: Tuple[str, ...] = ()
    basises: Tuple[str, ...] = ()

    @classmethod
    def parse(cls, data):
        return cls(Period.parse({key: data[key] for key in ('year', 'month_start', 'month_end') if key in data}),
                   names(data.get('products'), 'products'), names(data.get('categories'), 'categories'), names(data.get('basises'), 'basises'))

    def as_dict(self):
        return dict(period=self.period.as_dict(), products=list(self.products), categories=list(self.categories), basises=list(self.basises))


@dataclass(frozen=True)
class Principal:
    subject: str
    product_ids: Optional[Tuple[int, ...]] = None
    basis_ids: Optional[Tuple[int, ...]] = None
    scopes: Tuple[str, ...] = ('balance:read',)


def decimal(value):
    if value is None:
        return None
    try:
        result = Decimal(str(value))
    except Exception:
        raise AnalyticsError('calculation_error', 'Источник содержит нечисловое значение.', 422)
    if not result.is_finite():
        raise AnalyticsError('calculation_error', 'Источник содержит бесконечное или неопределённое значение.', 422)
    return result


def nullable_sum(values):
    values = list(values)
    with localcontext() as context:
        context.prec = 50
        return None if any(value is None for value in values) else sum(values, Decimal(0))


def subtract(a, b):
    with localcontext() as context:
        context.prec = 50
        return None if a is None or b is None else a - b


def percent(a, b):
    with localcontext() as context:
        context.prec = 50
        return None if a is None or b is None or b == 0 else a * Decimal(100) / b


def json_numbers(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, dict):
        return {key: json_numbers(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_numbers(item) for item in value]
    return value
