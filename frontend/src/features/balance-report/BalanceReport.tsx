import { Button, DatePicker, Drawer, Radio } from "@tinkerbells/xenon-ui";
import ruRU from "antd/es/date-picker/locale/ru_RU";
import dayjs, { type Dayjs } from "dayjs";
import "dayjs/locale/ru";
import { useEffect, useRef, useState } from "react";
import {
  assistantRequest,
  contextFromSearch,
  monthInput,
  previousPeriod,
  validPeriod,
  type ChatInput,
  type Period,
  type Report,
} from "./api";
import { ReportView } from "./ReportView";
import "./style.scss";

type Mode = "summary" | "comparison" | "details";
type MonthRange = [Dayjs | null, Dayjs | null] | null;

type Result = {
  report: Report;
  baseline?: Period;
  question?: string;
  history: ChatInput["history"];
};

const modes: {value: Mode; label: string}[] = [
  {value: "summary", label: "Сводка"},
  {value: "comparison", label: "Сравнение"},
  {value: "details", label: "По базисам"},
];

function toMonthRange(period: Period | null): MonthRange {
  if (!period) return null;
  return [
    dayjs(monthInput(period.year, period.month_start)),
    dayjs(monthInput(period.year, period.month_end ?? period.month_start)),
  ];
}

function toPeriod(range: MonthRange): Period | undefined {
  const [start, end] = range ?? [];
  if (!start || !end || start.year() !== end.year()) return;
  const period = {year: start.year(), month_start: start.month() + 1, month_end: end.month() + 1};
  return validPeriod(period) ? period : undefined;
}

function formatPeriod(period: Period) {
  const range = toMonthRange(period);
  if (!range) return "";
  const [start, end] = range;
  if (!start || !end) return "";
  return start.isSame(end, "month")
    ? start.locale("ru").format("MMMM YYYY")
    : start.locale("ru").format("MMMM") + " — " + end.locale("ru").format("MMMM YYYY");
}

function ReportContent({search}: {search: string}) {
  const context = contextFromSearch(search);
  const hasPeriod = validPeriod(context.period);
  const [mode, setMode] = useState<Mode>("summary");
  const [months, setMonths] = useState(() => toMonthRange(previousPeriod(context.period)));
  const [result, setResult] = useState<Result | null>(null);
  const [question, setQuestion] = useState("");
  const [pending, setPending] = useState<"report" | "question" | null>(null);
  const [error, setError] = useState("");
  const active = useRef<AbortController | null>(null);
  const resultAnchor = useRef<HTMLDivElement | null>(null);

  const baseline = mode === "comparison" ? toPeriod(months) : undefined;
  const canGenerate = hasPeriod && (mode !== "comparison" || !!baseline);
  const modeLabel = modes.find(item => item.value === mode)?.label ?? "";
  const submitLabel = mode === "comparison" ? "Сравнить периоды" : "Сформировать отчёт";

  useEffect(() => () => active.current?.abort(), []);

  useEffect(() => {
    if (result?.question) resultAnchor.current?.scrollIntoView({block: "start"});
  }, [result]);

  function resetResult() {
    active.current?.abort();
    active.current = null;
    setPending(null);
    setResult(null);
    setQuestion("");
    setError("");
  }

  async function run(followUp = false) {
    if (active.current || !canGenerate) return;

    const message = followUp ? question.trim() : undefined;
    if (followUp && (!result || !message)) return;

    const input: ChatInput = {
      action: followUp ? "chat" : mode,
      context,
      baseline: followUp ? result?.baseline : baseline,
      message,
      history: followUp ? result?.history ?? [] : [],
    };
    const controller = new AbortController();
    active.current = controller;
    setError("");
    setPending(followUp ? "question" : "report");
    if (!followUp) {
      setResult(null);
      setQuestion("");
    }

    try {
      const report = await assistantRequest<Report>("chat", controller.signal, input);
      if (controller.signal.aborted) return;
      const exchange: ChatInput["history"] = [
        {role: "user", content: message || modeLabel},
        {role: "assistant", content: report.text.slice(0, 1600)},
      ];
      setResult({
        report,
        baseline: input.baseline,
        question: message,
        history: [...input.history, ...exchange].slice(-4),
      });
      setQuestion("");
    } catch (failure) {
      if (!controller.signal.aborted) {
        setError(failure instanceof Error ? failure.message : "Не удалось подготовить отчёт.");
      }
    } finally {
      if (active.current === controller) {
        active.current = null;
        setPending(null);
      }
    }
  }

  return (
    <div className="balance-report">
      <div className="balance-report-context">
        <div>
          <span className="balance-report-field-label">Период в фильтрах</span>
          <strong>{hasPeriod ? formatPeriod(context.period) : "Выберите период на панели баланса"}</strong>
        </div>
        <p>{[
          context.categories.join(", ") || "Все категории",
          context.products.join(", "),
          context.basises.join(", ") || "Все базисы",
        ].filter(Boolean).join(" · ")}</p>
      </div>

      <div className="balance-report-controls">
        <div className="balance-report-field">
          <span id="balance-report-mode" className="balance-report-field-label">Вид отчёта</span>
          <Radio.Group
            aria-labelledby="balance-report-mode"
            className="balance-report-modes"
            optionType="button"
            buttonStyle="solid"
            options={modes}
            value={mode}
            onChange={event => {
              resetResult();
              setMode(event.target.value as Mode);
            }}
          />
        </div>

        <div className="balance-report-actions">
          {mode === "comparison" && (
            <div className="balance-report-field balance-report-period">
              <span id="balance-report-baseline" className="balance-report-field-label">С чем сравнить</span>
              <DatePicker.RangePicker
                aria-labelledby="balance-report-baseline"
                classNames={{popup: {root: "balance-report-calendar"}}}
                picker="month"
                format="MMM YYYY"
                locale={ruRU}
                value={months}
                placeholder={["Первый месяц", "Последний месяц"]}
                disabledDate={(date, {from}) => !!from && date.year() !== from.year()}
                onChange={range => {
                  resetResult();
                  setMonths(range);
                }}
              />
              {months && !baseline && <small>Выберите оба месяца внутри одного года.</small>}
            </div>
          )}
          <Button
            type="button"
            color="primary"
            variant="solid"
            loading={pending === "report"}
            disabled={!!pending || !canGenerate}
            onClick={() => void run()}
          >
            {submitLabel}
          </Button>
        </div>
      </div>

      {pending === "report" && (
        <p className="balance-report-pending" role="status">Подготавливаем отчёт…</p>
      )}

      {result && (
        <div ref={resultAnchor} className="balance-report-result">
          {result.question && <p className="balance-report-question">{result.question}</p>}
          <ReportView key={result.report.id} report={result.report} />
        </div>
      )}

      {error && <div className="balance-report-notice is-error" role="alert">{error}</div>}

      {result && (
        <form className="balance-report-composer" onSubmit={event => {
          event.preventDefault();
          void run(true);
        }}>
          <label htmlFor="balance-report-question">Уточнить отчёт</label>
          <textarea
            id="balance-report-question"
            placeholder="Например, покажи распределение по базисам"
            value={question}
            maxLength={4000}
            rows={2}
            onChange={event => setQuestion(event.target.value)}
            disabled={!!pending}
          />
          <div>
            <Button type="submit" loading={pending === "question"} disabled={!!pending || !question.trim()}>
              Отправить
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}

export function BalanceReport({open, onClose, search}: {open: boolean; onClose: () => void; search: string}) {
  useEffect(() => {
    if (!open) return;
    const escape = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    document.addEventListener("keydown", escape);
    return () => document.removeEventListener("keydown", escape);
  }, [open, onClose]);

  return <Drawer title="Отчёт по балансу" aria-label="Отчёт по балансу" open={open} onClose={onClose} width="min(940px, 100vw)" destroyOnHidden>
    {open && <ReportContent key={search} search={search} />}
  </Drawer>;
}
