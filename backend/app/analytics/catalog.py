TABLE_METRICS = [
    'opening_stock', 'production_plan', 'available_resource', 'allocated_volume', 'domestic_volume',
    'exchange_volume', 'exchange_obligations_volume', 'exchange_additional_volume', 'government_orders_volume',
    'wholesale_volume', 'retail_volume', 'domestic_fixed_contracts_volume', 'domestic_other_volume',
    'domestic_unmet_demand', 'export_volume', 'export_fixed_contracts_volume', 'export_other_volume',
    'export_unmet_demand', 'own_needs_volume', 'own_needs_unmet_demand', 'unallocated_resource',
]
LABELS = [
    'Остатки на начало месяца', 'План производства', 'Доступный ресурс', 'Распределённый объём', 'Внутренний рынок',
    'Биржа всего', 'Биржа обязательства', 'Биржа дополнительные объёмы', 'ГОЗ', 'Мелкий опт', 'Розничная сеть',
    'Обязательные контракты внутреннего рынка', 'Прочие контракты внутреннего рынка', 'Потребность внутреннего рынка',
    'Экспорт', 'Обязательные экспортные контракты', 'Прочие экспортные контракты', 'Потребность экспорта',
    'Нужды ДО', 'Дополнительная потребность ДО', 'Нераспределённый ресурс',
]
METRICS = {key: dict(name=label, unit='volume', aggregation='sum') for key, label in zip(TABLE_METRICS, LABELS)}
METRICS.update({
    'requested_volume': dict(name='Объём заявок', unit='volume', aggregation='sum'),
    'unmet_demand': dict(name='Общая неудовлетворённая потребность', unit='volume', aggregation='sum'),
    'restrictions': dict(name='Объём, недоступный для распределения', unit='volume', aggregation='sum'),
    'application_count': dict(name='Количество заявок', unit='count', aggregation='sum'),
    'utilization_percent': dict(name='Распределение доступного ресурса', unit='percent', aggregation='ratio_of_totals', formula='allocated_volume / available_resource * 100'),
    'demand_coverage_percent': dict(name='Обеспечение заявок', unit='percent', aggregation='ratio_of_totals', formula='allocated_volume / requested_volume * 100'),
    'exchange_share_percent': dict(name='Доля биржи в реализации', unit='percent', aggregation='ratio_of_totals', formula='exchange_volume / allocated_volume * 100'),
})
METRICS['available_resource']['formula'] = 'Из tab_resource_bk. calc_resource: base = plan + opening_stock - minimum_stock; resource = base, если shipment_cap = 0 или (base < shipment_cap и base != 0), иначе shipment_cap. Ограничения применяются к каждой плановой записи до агрегации.'
METRICS['restrictions']['formula'] = 'production_plan + opening_stock - available_resource'
METRICS['unallocated_resource']['formula'] = 'available_resource - allocated_volume'
METRICS['unmet_demand']['formula'] = 'sum(max(requested_volume - accepted_volume, 0)) по заявкам'


def data_catalog():
    return dict(
        schema_version='balance-analytics-v1',
        datasets=[
            dict(id='production_plans', source='tab_zayav_proizv_bk', description='Планы, начальные остатки и ограничения по продукту, базису и месяцу.'),
            dict(id='applications', source='tab_dataset_bk', description='Расчётные заявки: запрошенный и принятый объёмы, направление и категория сделки.'),
            dict(id='leftovers', source='tab_zayav_proizv_bk.ost', description='Входящие остатки по продукту, базису и месяцу.'),
            dict(id='restrictions', source='tab_zayav_proizv_bk + tab_resource_bk.ogr', description='Минимальный запас, лимит отгрузки и рассчитанный недоступный объём.'),
            dict(id='balance', source='tab_resource_bk + tab_dataset_bk', description='Материализованный доступный ресурс, распределение и оставшийся ресурс.'),
        ],
        metrics=METRICS,
        dimensions=['product', 'basis', 'month'],
        filters=['year', 'month_start', 'month_end', 'products', 'categories', 'basises'],
        period_rules=dict(required=['year', 'month_start'], inclusive=True, single_year=True, maximum_months=12, default_end='month_start'),
        semantics=dict(
            units='Суммирование выполняется только внутри одной единицы измерения. Между т, тыс. т и тыс. м3 автоматического пересчёта нет.',
            missing='null означает неизвестный показатель; 0 означает известное нулевое значение. Любое неизвестное слагаемое делает итог null.',
            inventory='При суммировании нескольких месяцев opening_stock является суммой месячных входящих остатков, а не единственным начальным остатком периода.',
            resources='Доступный ресурс берётся из результата расчёта tab_resource_bk. При отсутствии расчёта возвращается null и предупреждение, а не ноль.',
            ratios='Деление на ноль и неизвестное значение дают null с объяснением. Доли рассчитываются по итоговым объёмам, а не средним процентам строк.',
            precision='Вычисления выполняются Decimal без округления для отображения. JSON содержит числа; exact_metrics сохраняет их десятичное представление для проверки.',
            comparison='Изменение = comparison - baseline; относительное изменение = изменение / baseline * 100. Для процентных показателей абсолютное изменение измеряется в процентных пунктах.',
        ),
    )
