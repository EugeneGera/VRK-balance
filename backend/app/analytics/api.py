from flask import Blueprint, request
from app.analytics.balance import BalanceData, CALCULATION_VERSION, compare_data, fingerprint
from app.analytics.catalog import data_catalog
from app.analytics.contracts import AnalyticsError, Period, QuerySpec, names, integer
from app.analytics.filters import resolve_filters, applied_filters
from app.analytics.transport import read_endpoint
from app.entities.models import ShipmentsModel, AllResourceModel, ProductionPlanModel

blueprint = Blueprint('analytics', __name__, url_prefix='/analytics')
FILTER_KEYS = {'year', 'month_start', 'month_end', 'products', 'categories', 'basises', 'snapshot_id'}


def arguments(allowed):
    unknown = set(request.args) - set(allowed)
    if unknown:
        raise AnalyticsError('unsupported_parameter', 'Неподдерживаемые параметры запроса.', details={'parameters': sorted(unknown)})
    if any(len(request.args.getlist(key)) != 1 for key in request.args):
        raise AnalyticsError('duplicate_parameter', 'Передавайте списки через запятую, без повторяющихся ключей.')
    return request.args.to_dict()


def assert_snapshot(data, expected):
    if expected is not None and data != expected:
        raise AnalyticsError('snapshot_changed', 'Снимок данных изменился. Повторите получение данных.', 409,
                             {'expected': expected, 'actual': data})


@blueprint.get('/access')
@read_endpoint('get_access', database=False)
def access(session, principal):
    return dict(subject=principal.subject, scopes=list(principal.scopes)), {}, 1, False


@blueprint.get('/catalog')
@read_endpoint('get_data_catalog', database=False)
def catalog(session, principal):
    arguments(set())
    data = data_catalog()
    return data, dict(data_version=dict(schema='balance-analytics-v1', snapshot_id=fingerprint(data))), len(data['metrics']), False


@blueprint.get('/filter-values')
@read_endpoint('get_filter_values')
def filter_values(session, principal):
    args = arguments(FILTER_KEYS - {'snapshot_id'})
    period = Period.parse({key: args[key] for key in ('year', 'month_start', 'month_end') if key in args}) if any(key in args for key in ('year', 'month_start', 'month_end')) else Period(1, 1, 12)
    spec = QuerySpec(period, names(args.get('products'), 'products'), names(args.get('categories'), 'categories'), names(args.get('basises'), 'basises'))
    resolved = resolve_filters(session, spec, principal)
    periods = set()
    for model in (ShipmentsModel, AllResourceModel, ProductionPlanModel):
        query = session.query(model.year, model.month).filter(model.product_id.in_(list(resolved['products'])),
                model.shipping_basis_id.in_(list(resolved['basises'])), model.year.between(1, 9999), model.month.between(1, 12))
        if any(key in args for key in ('year', 'month_start', 'month_end')):
            query = query.filter(model.year == period.year, model.month.in_(period.months))
        periods.update((row.year, row.month) for row in query.distinct())
    data = applied_filters(resolved)
    data['periods'] = [dict(year=year, month=month) for year, month in sorted(periods)]
    return data, dict(applied_filters=applied_filters(resolved), data_version=dict(schema='balance-analytics-v1', snapshot_id=fingerprint(data))), sum(len(value) for value in data.values()), not periods


@blueprint.get('/balance-summary')
@read_endpoint('get_balance_summary')
def summary(session, principal):
    args = arguments(FILTER_KEYS | {'metrics'})
    data = BalanceData(session, QuerySpec.parse(args), principal)
    assert_snapshot(data.snapshot_id, args.get('snapshot_id'))
    groups = data.aggregate(metrics=args.get('metrics'))
    return dict(groups=groups), data.metadata(), len(groups), data.empty


@blueprint.get('/balance-details')
@read_endpoint('get_balance_details')
def details(session, principal):
    args = arguments(FILTER_KEYS | {'metrics', 'group_by', 'limit', 'offset'})
    dimensions = args.get('group_by', 'product,basis').split(',')
    limit = integer(args.get('limit', 500), 'limit', 1, 10000)
    offset = integer(args.get('offset', 0), 'offset', 0, 1000000)
    data = BalanceData(session, QuerySpec.parse(args), principal)
    assert_snapshot(data.snapshot_id, args.get('snapshot_id'))
    groups = data.aggregate(dimensions, args.get('metrics'))
    page = groups[offset:offset + limit]
    metadata = dict(data.metadata(), pagination=dict(total_count=len(groups), limit=limit, offset=offset, has_more=offset + limit < len(groups)))
    return dict(rows=page), metadata, len(page), data.empty


@blueprint.get('/compare-periods')
@read_endpoint('compare_periods')
def compare(session, principal):
    period_keys = {prefix + key for prefix in ('baseline_', 'comparison_') for key in ('year', 'month_start', 'month_end')}
    args = arguments(period_keys | {'products', 'categories', 'basises', 'metrics', 'snapshot_id'})
    datasets = []
    for prefix in ('baseline_', 'comparison_'):
        values = {key: value for key, value in args.items() if key in ('products', 'categories', 'basises')}
        values.update({key[len(prefix):]: value for key, value in args.items() if key.startswith(prefix)})
        datasets.append(BalanceData(session, QuerySpec.parse(values), principal))
    baseline, comparison = datasets
    snapshot = fingerprint([baseline.snapshot_id, comparison.snapshot_id])
    assert_snapshot(snapshot, args.get('snapshot_id'))
    data = compare_data(baseline, comparison, args.get('metrics'))
    metadata = dict(baseline=baseline.metadata(), comparison=comparison.metadata(),
                    data_version=dict(schema='balance-analytics-v1', calculation_version=CALCULATION_VERSION, snapshot_id=snapshot))
    return dict(groups=data), metadata, len(data), baseline.empty and comparison.empty
