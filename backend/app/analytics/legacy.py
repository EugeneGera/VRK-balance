from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from app.analytics.balance import BalanceData
from app.analytics.catalog import TABLE_METRICS
from app.analytics.contracts import AnalyticsError, Period, QuerySpec, names, decimal, json_numbers, percent, nullable_sum
from app.entities.models import DealCategoryDictModel, TransDirDictModel
from app.utils import MONTHS


class BalancePresentation:
    """Screen formats only; every volume comes from BalanceData's calculator."""

    def __init__(self, session, args):
        self.session = session
        self.args = args
        self.data = BalanceData(session, QuerySpec(
            Period.parse({key: args[key] for key in ('year', 'month_start', 'month_end') if args.get(key) is not None}),
            names(args.get('product'), 'product'), names(args.get('category_product'), 'category_product'), names(args.get('basises'), 'basises')))
        self.unit = self.data.single_unit()

    def finish(self, value, count):
        return value, self.data.metadata(), count, self.data.empty

    def waterfall(self):
        def chart(name, metrics):
            return dict(name=name, data=dict(
                total=dict(plan=metrics['production_plan'], leftovers=metrics['opening_stock']),
                available_resource=dict(available=metrics['available_resource'], restrictions=metrics['restrictions']),
                distribution=[dict(name=label, value=-metrics[value] if metrics[value] is not None else None, claim=metrics[claim])
                              for label, value, claim in [('Внутренний рынок', 'domestic_volume', 'domestic_unmet_demand'),
                                                         ('Экспорт', 'export_volume', 'export_unmet_demand'),
                                                         ('Нужды ДО', 'own_needs_volume', 'own_needs_unmet_demand')]],
                resource_leftover=dict(leftovers=metrics['unallocated_resource']), need=dict(need=metrics['unmet_demand'])))
        charts = [chart(row['dimensions']['basis']['name'], row['metrics']) for row in self.data.aggregate(('basis',))]
        totals = self.data.aggregate()
        if totals:
            charts.append(chart('Total', totals[0]['metrics']))
        return self.finish(dict(data=dict(data=charts), unit=self.unit), len(charts))

    def table(self, formatted=True):
        decimals = self.args.get('decimals', 2)
        try:
            decimals = int(decimals)
        except (ValueError, TypeError):
            raise AnalyticsError('invalid_format', 'decimals должен быть целым числом от 0 до 10.')
        if not 0 <= decimals <= 10:
            raise AnalyticsError('invalid_format', 'decimals должен быть целым числом от 0 до 10.')
        dash_zero = str(self.args.get('dash_zero', '1')).lower() not in ('0', 'false', 'no')

        def row(name, metrics):
            cells = [name]
            for metric in TABLE_METRICS:
                value = metrics[metric]
                if not formatted:
                    cells.append(value)
                elif value is None:
                    cells.append(None)
                elif value == 0 and dash_zero:
                    cells.append('—')
                else:
                    cells.append(format(decimal(value).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP), 'f'))
            return cells
        monthly = self.data.aggregate(('basis', 'month'))
        result = []
        for group in self.data.aggregate(('basis',)):
            basis = group['dimensions']['basis']
            result.append(row(basis['name'], group['metrics']))
            for month in monthly:
                if month['dimensions']['basis']['id'] == basis['id']:
                    result.append(row('Итого %s (%s)' % (MONTHS[month['dimensions']['month']['month'] - 1].lower(), basis['name']), month['metrics']))
        totals = self.data.aggregate()
        if totals:
            result.append(row('Итого', totals[0]['metrics']))
        return self.finish(result, len(result))

    def stock(self):
        result = dict(percent=[], absolute=[])
        for group in self.data.aggregate(('month',)):
            m = group['metrics']
            stock, allocated = m['exchange_volume'], m['allocated_volume']
            outside = None if stock is None or allocated is None else allocated - stock
            points = [('Реализация на бирже', stock, 'Реализация'),
                      ('Биржа обязательства', m['exchange_obligations_volume'], 'Реализация на бирже'),
                      ('Биржа доп. объёмы', m['exchange_additional_volume'], 'Реализация на бирже'),
                      ('Внебиржевая реализация', outside, 'Реализация')]
            for key in ('absolute', 'percent'):
                result[key].append(dict(month=MONTHS[group['dimensions']['month']['month'] - 1], data=[
                    dict(type=label, value=value if key == 'absolute' else json_numbers(percent(decimal(value), decimal(allocated))), category=category)
                    for label, value, category in points]))
        return self.finish(result, len(result['absolute']))

    def graph(self):
        mode = self.args.get('grouping_mode', 'factories')
        if mode not in ('factories', 'products'):
            raise AnalyticsError('unsupported_grouping', 'grouping_mode должен быть factories или products.')
        directions = {row.id: row.name for row in self.session.query(TransDirDictModel)}
        deals = {row.id: row.name for row in self.session.query(DealCategoryDictModel)}
        first, second = defaultdict(list), defaultdict(list)
        for application in self.data.applications:
            if not application['application_id'] or application['accepted'] is None or application['accepted'] <= 0:
                continue
            base = self.data.resolved['basises'][application['basis_id']]['name'] if mode == 'factories' else self.data.resolved['products'][application['product_id']]['name']
            first[(base, application['direction_id'])].append(application)
            second[(application['direction_id'], application['deal_category_id'])].append(application)

        def total(values):
            return nullable_sum(decimal(row['accepted']) for row in values)

        def price(values):
            weighted = nullable_sum(None if row['price'] is None else decimal(row['accepted']) * decimal(row['price']) for row in values)
            ratio = percent(weighted, total(values))
            return json_numbers(ratio / 100) if ratio is not None else None

        flows = [dict(source=base, target=directions[direction], value=json_numbers(total(values)), kind='заводы' if mode == 'factories' else 'продукты', price=price(values), unit=self.unit)
                 for (base, direction), values in sorted(first.items())]
        flows += [dict(source=directions[direction], target=deals[deal], value=json_numbers(total(values)), kind='направления сбыта', price=price(values), unit=self.unit)
                  for (direction, deal), values in sorted(second.items())]
        return self.finish(dict(data=flows, products=[product['name'] for product in self.data.resolved['products'].values()],
                                trans_dirs=[directions[key] for key in sorted({key[1] for key in first})]), len(flows))
