from app.analytics.contracts import Period, QuerySpec, names
from app.analytics.filters import resolve_filters


def product_filters(session, year, months, basis_names=None, product_names=None, category_names=None):
    """Resolve only the current call's arguments; no Flask request/session state."""
    period = Period.parse(dict(year=year, month_start=min(months), month_end=max(months)))
    spec = QuerySpec(period, names(product_names, 'products'), names(category_names, 'categories'), names(basis_names, 'basises'))
    resolved = resolve_filters(session, spec)
    units = list(resolved['units'].values())
    return dict(product_ids=list(resolved['products']), product_names=list(spec.products) or None,
                category_ids=list(resolved['categories']), category_names=list(spec.categories) or None,
                unit_names=units[0]['name'] if len(units) == 1 else None)
