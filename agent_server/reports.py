from urllib.parse import urlencode
from decimal import Decimal, ROUND_HALF_UP

CORE_METRICS = ['production_plan','opening_stock','available_resource','allocated_volume','domestic_volume',
                'exchange_volume','export_volume','own_needs_volume','unallocated_resource','unmet_demand',
                'utilization_percent','exchange_share_percent']


def period_label(period):
    if not period:
        return ''
    start, end = period['month_start'], period.get('month_end') or period['month_start']
    return f'{start:02d}.{period["year"]}' if start == end else f'{start:02d}–{end:02d}.{period["year"]}'


def screen_link(period, filters):
    args = dict(period or {})
    for source,target in [('products','product'),('categories','category_product'),('basises','basises')]:
        values = filters.get(source, [])
        if values:
            args[target] = ','.join(item['name'] for item in values)
    return '/balance_comission?'+urlencode(args)


def presentation(sources, catalog):
    """Tables are built from actual MCP values, independently of generated prose."""
    definitions = catalog['metrics']
    tables, provenance = [], []
    for source in sources:
        response, tool = source['response'], source['tool']
        metadata, data = response['metadata'], response['data']
        if tool not in ('get_balance_summary','get_balance_details','compare_periods'):
            continue
        is_compare = tool == 'compare_periods'
        current = metadata['comparison'] if is_compare else metadata
        period, filters = current['period'], current['applied_filters']
        # A screen table supports one exact unit; the analytical API can return several.
        units = {group['unit']['id'] for group in data.get('groups', data.get('rows', []))}
        links = [dict(label='Данные выбранного периода', url=screen_link(period,filters))] if len(units) <= 1 else []
        if is_compare and len(units) <= 1:
            links.insert(0, dict(label='Данные базового периода',url=screen_link(metadata['baseline']['period'],metadata['baseline']['applied_filters'])))
        provenance.append(dict(query_id=metadata['query_id'], tool=tool, period=period,
            baseline=metadata['baseline']['period'] if is_compare else None, filters=filters,
            snapshot_id=metadata['data_version']['snapshot_id'], warnings=current.get('warnings',[])+(metadata['baseline'].get('warnings',[]) if is_compare else []),
            links=links, pagination=metadata.get('pagination')))
        for group in data.get('groups', data.get('rows', [])):
            dimensions = group.get('dimensions', {})
            title = ' · '.join(value.get('name') or period_label(dict(year=value['year'],month_start=value['month']))
                               for value in dimensions.values()) or ('Сравнение периодов' if is_compare else 'Сводные показатели')
            rows = []
            metric_order = [key for key in CORE_METRICS if key in group['metrics']]
            metric_order += sorted(set(group['metrics']) - set(metric_order))
            for metric in metric_order:
                value = group['metrics'][metric]
                definition = definitions[metric]
                unit = '%' if definition['unit']=='percent' else 'шт.' if definition['unit']=='count' else group['unit']['name']
                row = dict(metric=metric,label=definition['name'],unit=unit)
                if is_compare:
                    row.update(value)
                    row['change_unit'] = 'п. п.' if definition['unit']=='percent' else unit
                else:
                    row['value'] = value
                rows.append(row)
            tables.append(dict(title=title,unit=group['unit'],kind='comparison' if is_compare else 'values',
                period=period,baseline=metadata['baseline']['period'] if is_compare else None,rows=rows,
                query_id=metadata['query_id']))
    return tables,provenance


def template_text(action, sources):
    analytical = [source for source in sources if source['tool'] in ('get_balance_summary','get_balance_details','compare_periods')]
    if not analytical or all(source['response']['status']=='empty' for source in analytical):
        return 'За выбранный период и фильтры данных нет. Выберите другой период или измените фильтры.'
    if action == 'comparison':
        return 'Сравнение подготовлено. В таблице приведены значения двух периодов, абсолютные изменения и изменения в процентах. При нулевой базе процент не определяется.'
    if action == 'details':
        return 'Подготовлена детализация по базисам. Показатели приведены отдельно для каждой единицы измерения. Откройте данные отчёта, чтобы проверить период и фильтры.'
    return 'Подготовлена сводка по выбранному периоду. Таблица показывает ресурс, распределение, направления реализации и неудовлетворённую потребность. Неизвестные значения отмечены отдельно от нулевых.'


def format_value(value, unit):
    if value is None:
        return 'нет данных'
    rounded = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    number = format(rounded, 'f').rstrip('0').rstrip('.').replace('.', ',')
    return f'{number} {unit}'


def verified_facts(tables):
    facts, primary = [], []
    for table in tables:
        rows = {row['metric']: row for row in table['rows']}
        heading = table['title']
        basis = heading not in ('Сводные показатели', 'Сравнение периодов')
        if basis and 'allocated_volume' in rows:
            items = []
            for metric in ('allocated_volume', 'available_resource', 'unallocated_resource'):
                if metric in rows:
                    row = rows[metric]
                    items.append(f'{row["label"].lower()} — {format_value(row["value"], row["unit"])}')
            primary.append(len(facts))
            facts.append({'id': len(facts), 'text': f'{heading}. '+', '.join(items)+'.'})
            continue
        for metric in ['allocated_volume', *(key for key in rows if key != 'allocated_volume')]:
            if metric not in rows:
                continue
            row = rows[metric]
            label, unit = row['label'], row['unit']
            period = period_label(table['period'])
            if table['kind'] == 'comparison':
                baseline = period_label(table['baseline'])
                change = format_value(row['absolute_change'], row['change_unit'])
                if row['absolute_change'] is not None and row['absolute_change'] > 0:
                    change = '+' + change
                line = f'{label} ({baseline} → {period}) — {format_value(row["baseline"], unit)} → {format_value(row["comparison"], unit)}. Изменение {change}.'
            else:
                line = f'{label} за {period} — {format_value(row["value"], unit)}.'
            if metric == 'allocated_volume':
                primary.append(len(facts))
            facts.append({'id': len(facts), 'text': line})
    return facts, primary
