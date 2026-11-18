from app.analytics.contracts import AnalyticsError
from app.entities.models import ProductDictModel, ProductCategoryDictModel, ShippingBasisDictModel, UnitDictModel


def resolve_filters(session, spec, principal=None):
    products = {row.id: dict(id=row.id, name=row.name, category_id=row.product_category_id, unit_id=row.unit_id)
                for row in session.query(ProductDictModel).order_by(ProductDictModel.id)}
    categories = {row.id: dict(id=row.id, name=row.name) for row in session.query(ProductCategoryDictModel)
                  if row.name not in (None, '', '0')}
    basises = {row.id: dict(id=row.id, name=row.name) for row in session.query(ShippingBasisDictModel)}
    units = {row.id: dict(id=row.id, name=row.name) for row in session.query(UnitDictModel)}
    for field, requested, dictionary in [('products', spec.products, products), ('categories', spec.categories, categories), ('basises', spec.basises, basises)]:
        unknown = sorted(set(requested) - {item['name'] for item in dictionary.values()})
        if unknown:
            raise AnalyticsError('unknown_filter', 'В справочнике нет выбранных значений.', details={'field': field, 'values': unknown})
    selected = {pid: product for pid, product in products.items() if product['category_id'] in categories
                and (not spec.products or product['name'] in spec.products)
                and (not spec.categories or categories[product['category_id']]['name'] in spec.categories)}
    if spec.products and len(selected) != len(spec.products):
        raise AnalyticsError('filter_conflict', 'Выбранные продукты не соответствуют выбранным категориям.')
    selected_basises = {bid: basis for bid, basis in basises.items() if not spec.basises or basis['name'] in spec.basises}
    if principal is not None:
        if principal.product_ids is not None:
            forbidden = [p['name'] for pid, p in selected.items() if pid not in principal.product_ids and (spec.products or spec.categories)]
            if forbidden:
                raise AnalyticsError('forbidden_filter', 'Нет доступа к выбранным продуктам.', 403)
            selected = {pid: p for pid, p in selected.items() if pid in principal.product_ids}
        if principal.basis_ids is not None:
            if spec.basises and any(bid not in principal.basis_ids for bid in selected_basises):
                raise AnalyticsError('forbidden_filter', 'Нет доступа к выбранным базисам.', 403)
            selected_basises = {bid: b for bid, b in selected_basises.items() if bid in principal.basis_ids}
    used_categories = {p['category_id'] for p in selected.values()}
    used_units = {p['unit_id'] for p in selected.values()}
    return dict(products=selected, categories={key: categories[key] for key in sorted(used_categories)},
                basises=selected_basises, units={key: units[key] for key in sorted(used_units) if key in units})


def applied_filters(resolved):
    return {key: [values[k] for k in sorted(values)] for key, values in resolved.items()}
