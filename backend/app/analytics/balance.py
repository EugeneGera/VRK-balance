import hashlib
import json
from collections import defaultdict
from decimal import Decimal

from app.analytics.catalog import METRICS
from app.analytics.contracts import AnalyticsError, decimal, json_numbers, nullable_sum, percent, subtract, names
from app.analytics.filters import resolve_filters, applied_filters
from app.entities.models import AllResourceModel as R, ProductionPlanModel as P, ShipmentsModel as S

CALCULATION_VERSION = 'balance-core-1'

def rows(query):
    return [dict(row._mapping) for row in query.all()]


def fingerprint(value):
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str, separators=(',', ':'))
    return 'sha256:' + hashlib.sha256(serialized.encode()).hexdigest()


class BalanceData:
    """Immutable source rows and one common calculator for UI and analytics."""

    def __init__(self, session, spec, principal=None):
        self.spec = spec
        self.resolved = resolve_filters(session, spec, principal)
        product_ids, basis_ids = list(self.resolved['products']), list(self.resolved['basises'])

        def filtered(query, model):
            return query.filter(model.year == spec.period.year, model.month.in_(spec.period.months),
                                model.product_id.in_(product_ids), model.shipping_basis_id.in_(basis_ids))

        self.plans = rows(filtered(session.query(
            P.id.label('id'), P.year.label('year'), P.month.label('month'),
            P.shipping_basis_id.label('basis_id'), P.product_id.label('product_id'), P.unit_id.label('unit_id'),
            P.product_owner_id.label('owner_id'), P.plan.label('plan'), P.left.label('opening_stock'),
            P.min_left.label('minimum_stock'), P.max_shipment.label('shipment_cap'),
        ), P))
        self.resources = rows(filtered(session.query(
            R.year.label('year'), R.month.label('month'), R.shipping_basis_id.label('basis_id'),
            R.product_id.label('product_id'), R.resource.label('resource'), R.restrictions.label('restrictions'),
            R.plan.label('plan'), R.leftovers.label('opening_stock'),
        ), R))
        self.applications = rows(filtered(session.query(
            S.id.label('id'), S.year.label('year'), S.month.label('month'), S.shipping_basis_id.label('basis_id'),
            S.product_id.label('product_id'), S.unit_id.label('unit_id'), S.value.label('requested'),
            S.accepted_deal.label('accepted'), S.cost.label('price'), S.trans_dir_id.label('direction_id'),
            S.deal_category_id.label('deal_category_id'), S.trans_application_id.label('application_id'),
        ), S))
        sources = dict(plans=self.plans, resources=self.resources, applications=self.applications)
        self.source_counts = {key: len(value) for key, value in sources.items()}
        self.snapshot_id = fingerprint(dict(calculation_version=CALCULATION_VERSION, period=spec.period.as_dict(),
            sources={key: sorted(value, key=lambda row: json.dumps(row, sort_keys=True, default=str))
                     for key, value in sources.items()}, dictionaries=self.resolved))
        self.warnings = []
        self.points = self._calculate()

    @property
    def empty(self):
        return not self.points

    def _calculate(self):
        groups = defaultdict(lambda: dict(plans=[], resources=[], applications=[]))
        application_keys = set()
        for source, records in [('plans', self.plans), ('resources', self.resources), ('applications', self.applications)]:
            for row in records:
                product = self.resolved['products'][row['product_id']]
                unit = product['unit_id']
                if unit not in self.resolved['units'] or (row.get('unit_id') is not None and row['unit_id'] != unit):
                    raise AnalyticsError('unit_mismatch', 'Единицы измерения исходных записей не соответствуют продукту.', 422)
                key = (row['year'], row['month'], row['basis_id'], row['product_id'], unit)
                if source == 'applications' and row['application_id'] is not None and row['application_id'] > 0:
                    identity = (row['year'], row['month'], row['application_id'])
                    if identity in application_keys:
                        raise AnalyticsError('duplicate_application', 'Расчётный набор содержит повтор одной заявки.', 422)
                    application_keys.add(identity)
                groups[key][source].append(row)
        points = []
        for key in sorted(groups):
            group = groups[key]
            plans, resources = group['plans'], group['resources']
            if len(resources) > 1:
                raise AnalyticsError('duplicate_resource', 'Несколько записей ресурса для одного продукта, базиса и месяца.', 422)
            apps = [row for row in group['applications'] if row['application_id'] is not None and row['application_id'] > 0]
            for row in apps:
                requested, accepted = decimal(row['requested']), decimal(row['accepted'])
                if (requested is not None and requested < 0) or (accepted is not None and accepted < 0) or (
                    requested is not None and accepted is not None and accepted > requested
                ):
                    raise AnalyticsError('invalid_allocation', 'Обнаружен некорректный объём заявки или распределения.', 422)
                if row['direction_id'] not in (1, 2, 3) or row['deal_category_id'] not in range(1, 10):
                    raise AnalyticsError('invalid_application', 'Заявка содержит неизвестное направление или категорию сделки.', 422)

            def allocated(direction=None, deals=None):
                return nullable_sum(decimal(row['accepted']) for row in apps
                                    if (direction is None or row['direction_id'] == direction)
                                    and (deals is None or row['deal_category_id'] in deals))

            def unmet(direction=None):
                return nullable_sum(None if row['requested'] is None or row['accepted'] is None else max(
                    Decimal(0), subtract(decimal(row['requested']), decimal(row['accepted']))) for row in apps
                    if direction is None or row['direction_id'] == direction)

            supply = resources[0] if resources else None
            metrics = dict(
                production_plan=nullable_sum(decimal(row['plan']) for row in plans) if plans else decimal(supply['plan']) if supply else None,
                opening_stock=nullable_sum(decimal(row['opening_stock']) for row in plans) if plans else decimal(supply['opening_stock']) if supply else None,
                available_resource=decimal(supply['resource']) if supply else None,
                restrictions=decimal(supply['restrictions']) if supply else None,
                allocated_volume=allocated(), requested_volume=nullable_sum(decimal(row['requested']) for row in apps),
                unmet_demand=unmet(), application_count=len(apps),
                domestic_volume=allocated(2), exchange_volume=allocated(2, (3, 8)),
                exchange_obligations_volume=allocated(2, (3,)), exchange_additional_volume=allocated(2, (8,)),
                government_orders_volume=allocated(2, (2,)), wholesale_volume=allocated(2, (5,)), retail_volume=allocated(2, (4,)),
                domestic_fixed_contracts_volume=allocated(2, (6,)), domestic_other_volume=allocated(2, (7, 9)), domestic_unmet_demand=unmet(2),
                export_volume=allocated(3), export_fixed_contracts_volume=allocated(3, (6,)), export_other_volume=allocated(3, (7, 9)),
                export_unmet_demand=unmet(3), own_needs_volume=allocated(1), own_needs_unmet_demand=unmet(1),
            )
            metrics['unallocated_resource'] = subtract(metrics['available_resource'], metrics['allocated_volume'])
            if not supply:
                self.warnings.append(dict(code='missing_resource_calculation', year=key[0], month=key[1], basis_id=key[2], product_id=key[3]))
            if any(value is None for value in metrics.values()):
                self.warnings.append(dict(code='missing_values', year=key[0], month=key[1], basis_id=key[2], product_id=key[3],
                                          metrics=[name for name, value in metrics.items() if value is None]))
            points.append(dict(year=key[0], month=key[1], basis_id=key[2], product_id=key[3], unit_id=key[4], metrics=metrics))
        return points

    def metadata(self):
        return dict(period=self.spec.period.as_dict(), requested_filters=self.spec.as_dict(),
                    applied_filters=applied_filters(self.resolved),
                    data_version=dict(schema='balance-analytics-v1', calculation_version=CALCULATION_VERSION, snapshot_id=self.snapshot_id,
                                      source_tables=['tab_zayav_proizv_bk', 'tab_resource_bk', 'tab_dataset_bk'], source_counts=self.source_counts),
                    warnings=self.warnings)

    def aggregate(self, dimensions=(), metrics=None):
        dimensions = tuple(dimensions)
        if len(set(dimensions)) != len(dimensions) or set(dimensions) - {'product', 'basis', 'month'}:
            raise AnalyticsError('unsupported_grouping', 'Поддерживаются уникальные измерения product, basis, month.')
        requested = names(metrics, 'metrics') or tuple(METRICS)
        if set(requested) - set(METRICS):
            raise AnalyticsError('unknown_metric', 'Запрошен неизвестный показатель.', details={'values': sorted(set(requested) - set(METRICS))})
        buckets = defaultdict(list)
        for point in self.points:
            key = (point['unit_id'],) + tuple(point['product_id'] if dim == 'product' else point['basis_id'] if dim == 'basis' else point['month'] for dim in dimensions)
            buckets[key].append(point)
        result = []
        additive = [key for key, definition in METRICS.items() if definition['aggregation'] == 'sum']
        for key in sorted(buckets):
            points = buckets[key]
            totals = {metric: nullable_sum(point['metrics'][metric] for point in points) for metric in additive}
            totals['application_count'] = int(totals['application_count'])
            ratios = dict(utilization_percent=('allocated_volume', 'available_resource'),
                          demand_coverage_percent=('allocated_volume', 'requested_volume'),
                          exchange_share_percent=('exchange_volume', 'allocated_volume'))
            null_reasons = {metric: 'missing_value' for metric, value in totals.items() if value is None}
            for metric, (numerator, denominator) in ratios.items():
                totals[metric] = percent(totals[numerator], totals[denominator])
                if totals[metric] is None:
                    null_reasons[metric] = 'missing_value' if totals[numerator] is None or totals[denominator] is None else 'zero_denominator'
            dims = {}
            for dim, value in zip(dimensions, key[1:]):
                dims[dim] = self.resolved['products'][value] if dim == 'product' else self.resolved['basises'][value] if dim == 'basis' else dict(year=self.spec.period.year, month=value)
            values = {name: totals[name] for name in requested}
            result.append(dict(unit=self.resolved['units'][key[0]], dimensions=dims, metrics=json_numbers(values),
                               exact_metrics={name: str(value) if value is not None else None for name, value in values.items()},
                               null_reasons={name: reason for name, reason in null_reasons.items() if name in requested}))
        return result

    def single_unit(self):
        units = {point['unit_id'] for point in self.points}
        if len(units) > 1:
            raise AnalyticsError('incompatible_units', 'Для экранной диаграммы выберите продукты в одной единице измерения. Аналитический API группирует их отдельно.')
        return self.resolved['units'][next(iter(units))]['name'] if units else None


def compare_data(baseline, comparison, metrics=None):
    left = {row['unit']['id']: row for row in baseline.aggregate(metrics=metrics)}
    right = {row['unit']['id']: row for row in comparison.aggregate(metrics=metrics)}
    result = []
    requested = names(metrics, 'metrics') or tuple(METRICS)
    for unit_id in sorted(set(left) | set(right)):
        a, b = left.get(unit_id), right.get(unit_id)
        differences = {}
        for metric in requested:
            av = decimal(a['exact_metrics'][metric]) if a else None
            bv = decimal(b['exact_metrics'][metric]) if b else None
            absolute = subtract(bv, av)
            relative = percent(absolute, av)
            reason = 'missing_value' if av is None or bv is None else 'zero_baseline' if av == 0 else None
            differences[metric] = dict(baseline=json_numbers(av), comparison=json_numbers(bv),
                                       absolute_change=json_numbers(absolute), percent_change=json_numbers(relative),
                                       absolute_unit='percentage_points' if METRICS[metric]['unit'] == 'percent' else METRICS[metric]['unit'],
                                       null_reason=reason)
        result.append(dict(unit=(a or b)['unit'], metrics=differences))
    return result
