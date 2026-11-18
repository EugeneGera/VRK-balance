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
  type AnalystResponse,
  type Context,
} from "./api";
import { ReportView } from "./ReportView";
import "./style.scss";

type Mode = "task" | "summary" | "comparison" | "details";
type MonthRange = [Dayjs | null, Dayjs | null] | null;

type Result = {
  reply: AnalystResponse;
  context: Context;
  task: string;
  baseline?: Period;
  question?: string;
  history: ChatInput["history"];
};

const modes: {value: Mode; label: string}[] = [
  {value: "task", label: "Задание"},
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
  const [mode, setMode] = useState<Mode>("task");
  const [months, setMonths] = useState(() => toMonthRange(previousPeriod(context.period)));
  const [result, setResult] = useState<Result | null>(null);
  const [question, setQuestion] = useState("");
  const [pending, setPending] = useState<"report" | "question" | null>(null);
  const [error, setError] = useState("");
  const active = useRef<AbortController | null>(null);
  const attemptId = useRef<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const resultAnchor = useRef<HTMLDivElement | null>(null);

  const baseline = mode === "comparison" ? toPeriod(months) : undefined;
  const canGenerate = hasPeriod && (mode !== "comparison" || !!baseline);
  const modeLabel = modes.find(item => item.value === mode)?.label ?? "";
  const submitLabel = mode === "comparison" ? "Сравнить периоды" : "Сформировать отчёт";

  useEffect(() => () => active.current?.abort(), []);

  useEffect(() => {
    if (result?.reply.kind === "clarification") inputRef.current?.focus();
    else if (result?.question) resultAnchor.current?.scrollIntoView({block: "start"});
  }, [result]);

  function resetResult() {
    active.current?.abort();
    active.current = null;
    attemptId.current = null;
    setPending(null);
    setResult(null);
    setQuestion("");
    setError("");
  }

  async function run(useText = false) {
    if (active.current || !canGenerate || (!useText && mode === "task")) return;

    const message = useText ? question.trim() : undefined;
    if (useText && !message) return;
    const previous = useText ? result : null;
    const task = previous?.task || message || modeLabel;
    if (!useText || !attemptId.current) attemptId.current = globalThis.crypto?.randomUUID?.() ?? null;
    const input: ChatInput = {
      action: useText || mode === "task" ? "chat" : mode,
      context: previous?.context ?? context,
      baseline: previous?.baseline ?? baseline,
      attempt_id: attemptId.current ?? undefined,
      task,
      message,
      history: previous?.history ?? [],
    };
    const controller = new AbortController();
    active.current = controller;
    setError("");
    setPending(useText ? "question" : "report");
    if (!useText) {
      setResult(null);
      setQuestion("");
    }

    try {
      const reply = await assistantRequest<AnalystResponse>("chat", controller.signal, input);
      if (controller.signal.aborted) return;
      attemptId.current = reply.attempt_id;
      const exchange: ChatInput["history"] = [
        {role: "user", content: (message || modeLabel).slice(0, 1600)},
        {role: "assistant", content: reply.text.slice(0, 1600)},
      ];
      // A single data selection provides the operating context for the next turn.
      const source = reply.kind === "report" && reply.sources.length === 1 ? reply.sources[0] : undefined;
      setResult({
        reply,
        task,
        context: source ? {
          period: source.period,
          categories: source.filters.categories.map(item => item.name),
          products: source.filters.products.map(item => item.name),
          basises: source.filters.basises.map(item => item.name),
        } : input.context,
        baseline: source?.baseline ?? input.baseline,
        question: previous ? message : undefined,
        history: [...input.history, ...exchange].slice(-6),
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

  const clarification = result?.reply.kind === "clarification" ? result.reply : null;
  const report = result?.reply.kind === "report" ? result.reply : null;
  const inputLabel = clarification ? "Ответ на уточнение" : report ? "Уточнить отчёт" : "Задание";
  const composer = (
    <form className="balance-report-composer" onSubmit={event => {
      event.preventDefault();
      void run(true);
    }}>
      {clarification && (
        <div className="balance-report-notice" role="status">
          {clarification.text}
          <small>ID попытки {clarification.attempt_id}</small>
        </div>
      )}
      <label htmlFor="balance-report-question">{inputLabel}</label>
      <textarea
        ref={inputRef}
        id="balance-report-question"
        placeholder={report ? "Например, покажи распределение по базисам" :
          clarification ? "Укажите недостающие данные" : "Например, подготовь сводку по выбранному периоду"}
        value={question}
        maxLength={4000}
        rows={2}
        onChange={event => setQuestion(event.target.value)}
        disabled={!!pending}
      />
      <div className="balance-report-form-buttons">
        {mode === "task" && result && <Button type="button" variant="outline" onClick={resetResult}>Новое задание</Button>}
        <Button type="submit" loading={pending === "question"} disabled={!!pending || !question.trim() || !canGenerate}>
          {clarification || report ? "Отправить" : "Выполнить задание"}
        </Button>
      </div>
    </form>
  );

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

        {mode !== "task" && <div className="balance-report-actions">
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
        </div>}
      </div>

      {mode === "task" && composer}
      {pending === "report" && (
        <p className="balance-report-pending" role="status">Подготавливаем отчёт…</p>
      )}

      {report && (
        <div ref={resultAnchor} className="balance-report-result">
          {result?.question && <p className="balance-report-question">{result.question}</p>}
          <ReportView key={report.id} report={report} />
        </div>
      )}

      {error && (
        <div className="balance-report-notice is-error" role="alert">
          {error}
          {attemptId.current && <small>ID попытки {attemptId.current}</small>}
        </div>
      )}

      {mode !== "task" && result && composer}
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
