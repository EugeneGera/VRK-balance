import { BASE_URL } from "@/shared/config/consts";

export interface Period { year: number; month_start: number; month_end?: number }
export interface Context { period: Period; products: string[]; categories: string[]; basises: string[] }
export interface NamedValue { id: number; name: string; category_id?: number; unit_id?: number }
export interface FilterValues { products: NamedValue[]; categories: NamedValue[]; basises: NamedValue[]; periods: {year:number; month:number}[] }
export interface ModelStatus { ready: boolean; reason: string | null; model: string; local: boolean; templates_available: boolean }
export interface MetricRow {
  metric: string; label: string; unit: string; value?: number | null;
  baseline?: number | null; comparison?: number | null; absolute_change?: number | null;
  percent_change?: number | null; change_unit?: string; null_reason?: string | null;
}
export interface ReportTable {
  title: string; unit: NamedValue; kind: "values" | "comparison";
  period: Period; baseline: Period | null; rows: MetricRow[]; query_id: string;
}
export interface Source {
  query_id: string; tool: string; period: Period; baseline: Period | null;
  filters: {products: NamedValue[]; categories: NamedValue[]; basises: NamedValue[]};
  snapshot_id: string; warnings: unknown[]; links: {label: string; url: string}[];
  pagination?: {has_more: boolean; total_count: number};
}
export interface Report {
  id: string; mode: "template" | "local_model"; text: string; tables: ReportTable[]; sources: Source[];
  context: Context; created_at: string; model: string | null; empty: boolean;
}
export type Action = "summary" | "comparison" | "details" | "chat";
export interface ChatInput {
  action: Action; context: Context; baseline?: Period; message?: string;
  history: {role: "user" | "assistant"; content: string}[];
}

export async function assistantRequest<T>(path: string, signal?: AbortSignal, body?: ChatInput): Promise<T> {
  const response = await fetch(`${BASE_URL}/assistant/${path}`, {
    method: body ? "POST" : "GET", signal,
    headers: body ? {"Content-Type": "application/json"} : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const result = await response.json().catch(() => null);
  if (!response.ok || result?.status !== "ok") {
    throw new Error(result?.error?.message || "Сервис аналитики недоступен. Попробуйте повторить запрос.");
  }
  return result.data as T;
}

export function contextFromSearch(search: string): Context {
  const params = new URLSearchParams(search);
  const values = (key: string) => (params.get(key) || "").split(",").map(item => item.trim()).filter(Boolean);
  const start = Number(params.get("month_start"));
  return {
    period: {year: Number(params.get("year")), month_start: start, month_end: Number(params.get("month_end") || start)},
    products: values("product"), categories: values("category_product"), basises: values("basises"),
  };
}

export function validPeriod(period: Period): boolean {
  const end = period.month_end ?? period.month_start;
  return Number.isInteger(period.year) && period.year >= 1 && period.year <= 9999 &&
    Number.isInteger(period.month_start) && period.month_start >= 1 && end <= 12 &&
    Number.isInteger(end) && end >= period.month_start;
}

export function monthInput(year: number, month: number): string {
  return year > 0 && month >= 1 && month <= 12 ? `${String(year).padStart(4,"0")}-${String(month).padStart(2,"0")}` : "";
}

export function periodLabel(period: Period): string {
  const start = monthInput(period.year,period.month_start).split("-").reverse().join(".");
  return period.month_end && period.month_end !== period.month_start ? `${start} — ${monthInput(period.year,period.month_end).split("-").reverse().join(".")}` : start;
}

export function previousPeriod(period: Period): Period | null {
  if (!validPeriod(period)) return null;
  const width = (period.month_end ?? period.month_start) - period.month_start + 1;
  const end = period.month_start - 1;
  if (end >= width) return {year: period.year,month_start: end - width + 1,month_end: end};
  if (end === 0 && period.year > 1) return {year: period.year - 1,month_start: 13 - width,month_end: 12};
  return null;
}
