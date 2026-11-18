import { Fragment, useState } from "react";
import { Report } from "./api";
import { periodLabel } from "./api";

const number = (value: number | null | undefined) => value == null ? "Нет данных" : new Intl.NumberFormat("ru-RU", {maximumFractionDigits: 2}).format(value);

function inline(text: string) {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part,index) => part.startsWith("**") ?
    <strong key={index}>{part.slice(2,-2)}</strong> : part.startsWith("`") ? <code key={index}>{part.slice(1,-1)}</code> : <Fragment key={index}>{part}</Fragment>);
}

function Narrative({text}: {text: string}) {
  return <div className="balance-report-narrative">{text.split(/\n\s*\n/).map((block,index) => {
    const lines = block.split("\n");
    if (lines.every(line => /^\s*[-*] /.test(line))) return <ul key={index}>{lines.map((line,i) => <li key={i}>{inline(line.replace(/^\s*[-*] /,""))}</li>)}</ul>;
    if (/^#{1,3} /.test(block)) return <h3 key={index}>{inline(block.replace(/^#{1,3} /,""))}</h3>;
    return <p key={index}>{inline(block)}</p>;
  })}</div>;
}

export function ReportView({report}: {report: Report}) {
  const [copied,setCopied] = useState(false);
  const [copyError,setCopyError] = useState(false);
  const copy = async () => {
    const text = [report.text, `ID попытки: ${report.attempt_id}`, ...report.tables.map(table => `${table.title} (${periodLabel(table.period)})\n` + table.rows.map(row =>
      table.kind === "comparison" ? `${row.label}: ${number(row.baseline)} → ${number(row.comparison)} ${row.unit}; изменение ${number(row.absolute_change)} ${row.change_unit}; ${number(row.percent_change)} %` :
        `${row.label}: ${number(row.value)} ${row.unit}`).join("\n")),
      ...report.sources.map(source => `Источник: ${source.query_id}; снимок: ${source.snapshot_id}`)].join("\n\n");
    try { await navigator.clipboard.writeText(text); setCopied(true); setCopyError(false); }
    catch { setCopyError(true); }
  };
  return <article className="balance-report-report" aria-label="Аналитический отчёт">
    <div className="balance-report-report__head">
      <div>
        <time dateTime={report.created_at}>{new Date(report.created_at).toLocaleTimeString("ru-RU",{hour:"2-digit",minute:"2-digit"})}</time></div>
      <button type="button" className="balance-report-text-button" onClick={copy}>{copied ? "Скопировано" : "Копировать отчёт"}</button>
    </div>
    {copyError && <p role="status">Не удалось скопировать автоматически. Можно выделить текст отчёта.</p>}
    {report.execution_mode === "template" && report.fallback_reason !== "empty_data" && (
      <p className="balance-report-notice" role="status">Выводы недоступны. Показан отчёт по шаблону.</p>
    )}
    <Narrative text={report.text} />
    {report.tables.map((table,index) => <section className="balance-report-report__table" key={`${table.query_id}-${index}`}>
      <h3>{table.title} <span>{table.unit.name}</span></h3>
      <div className="balance-report-table-scroll"><table>
        <thead><tr><th scope="col">Показатель</th>
          {table.kind === "comparison" ? <><th scope="col">{table.baseline && periodLabel(table.baseline)}</th><th scope="col">{periodLabel(table.period)}</th><th scope="col">Изменение</th><th scope="col">Изменение, %</th></> :
            <th scope="col">{periodLabel(table.period)}</th>}
        </tr></thead>
        <tbody>{table.rows.map(row => <tr key={row.metric}><th scope="row">{row.label}</th>
          {table.kind === "comparison" ? <><td>{number(row.baseline)} <small>{row.unit}</small></td><td>{number(row.comparison)} <small>{row.unit}</small></td>
            <td>{row.absolute_change != null && row.absolute_change > 0 ? "+" : ""}{number(row.absolute_change)} <small>{row.change_unit}</small></td>
            <td title={row.null_reason === "zero_baseline" ? "При нулевой базе процент не определяется" : undefined}>{number(row.percent_change)}</td></> :
            <td>{number(row.value)} <small>{row.unit}</small></td>}
        </tr>)}</tbody>
      </table></div>
    </section>)}
    {report.sources.length > 0 && <details className="balance-report-sources"><summary>Данные отчёта · {report.sources.length} {report.sources.length === 1 ? "запрос" : "запроса"}</summary>
      <p>ID попытки <code>{report.attempt_id}</code></p>
      {report.sources.map(source => <div className="balance-report-source" key={source.query_id}>
        <p><strong>{periodLabel(source.period)}</strong>{source.baseline && ` · сравнение с ${periodLabel(source.baseline)}`}</p>
        <p>{source.filters.categories.map(item => item.name).join(", ") || "Все разрешённые категории"}</p>
        <p>Продукты: {source.filters.products.map(item => item.name).join(", ") || "Нет разрешённых продуктов"}</p>
        <p>Базисы: {source.filters.basises.map(item => item.name).join(", ") || "Нет разрешённых базисов"}</p>
        {source.links.map(link => <a key={link.url} href={link.url} target="_blank" rel="noopener noreferrer">{link.label} ↗</a>)}
        {source.links.length === 0 && <p>Выборка содержит разные единицы. Для открытия экранной таблицы выберите одну категорию.</p>}
        {source.warnings.length > 0 && <p className="balance-report-warning">В исходных данных есть неизвестные значения. Они не заменяются нулями.</p>}
        {source.pagination?.has_more && <p className="balance-report-warning">Показана часть строк. Уточните фильтры или запросите следующую страницу.</p>}
        <dl><dt>ID запроса</dt><dd>{source.query_id}</dd><dt>Снимок данных</dt><dd>{source.snapshot_id}</dd></dl>
      </div>)}
    </details>}
  </article>;
}
