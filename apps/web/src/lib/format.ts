export type Language = "pt" | "en";
export const locale = (language: Language) => language === "pt" ? "pt-BR" : "en-GB";
const hubTimeZone = "America/Sao_Paulo";
// Match the API's business date, including the three hours around UTC midnight.
export const today = (now = new Date()) => new Intl.DateTimeFormat("en-CA", {
  timeZone: hubTimeZone, year: "numeric", month: "2-digit", day: "2-digit",
}).format(now);
export const unavailable = (language: Language) => language === "pt" ? "Indisponível" : "Unavailable";

export function money(value: string | null | undefined, language: Language): string {
  if (value === null || value === undefined || value === "" || !Number.isFinite(Number(value))) return unavailable(language);
  // Modern Intl accepts exact decimal strings; the assertion only bridges TypeScript's older signature.
  return new Intl.NumberFormat(locale(language), { style: "currency", currency: "BRL" }).format(value as unknown as number);
}
export function unitPrice(value: string | null | undefined, language: Language): string {
  if (value === null || value === undefined || value === "" || !Number.isFinite(Number(value))) return unavailable(language);
  return new Intl.NumberFormat(locale(language), { style: "currency", currency: "BRL", maximumFractionDigits: 8 }).format(value as unknown as number);
}
export function number(value: string | null | undefined, language: Language): string {
  if (value === null || value === undefined || value === "" || !Number.isFinite(Number(value))) return unavailable(language);
  return new Intl.NumberFormat(locale(language), { maximumFractionDigits: 8 }).format(value as unknown as number);
}
export function percent(value: string, language: Language): string {
  return value !== "" && Number.isFinite(Number(value)) ? `${new Intl.NumberFormat(locale(language), { maximumFractionDigits: 2 }).format(value as unknown as number)}%` : unavailable(language);
}
export function date(value: string | null | undefined, language: Language, time = false): string {
  if (!value) return unavailable(language);
  const parsed = new Date(value.length === 10 ? `${value}T12:00:00Z` : value);
  if (!Number.isFinite(parsed.getTime())) return unavailable(language);
  return new Intl.DateTimeFormat(locale(language), { dateStyle: "short", ...(time ? { timeStyle: "short" as const } : {}), timeZone: hubTimeZone }).format(parsed);
}
export const eventLabels: Record<string, [string, string]> = {
  deposit: ["Aporte", "Deposit"], withdrawal: ["Retirada", "Withdrawal"], buy: ["Compra realizada", "Recorded buy"],
  sell: ["Venda realizada", "Recorded sell"], dividend: ["Provento", "Income"], fee: ["Taxa", "Fee"], tax: ["Imposto", "Tax"], split: ["Desdobramento", "Split"],
};
export const classLabels: Record<string, [string, string]> = {
  stock: ["Ações", "Equities"], fii: ["Fundos imobiliários", "Real estate funds"], etf: ["ETFs", "ETFs"], fixed_income: ["Renda fixa", "Fixed income"], other: ["Outros", "Other"],
};
export function label(map: Record<string, [string, string]>, key: string, language: Language) {
  return map[key]?.[language === "pt" ? 0 : 1] ?? key;
}

// Translate known contract messages; preserve any unrecognized server evidence verbatim.
export function serverMessage(message: string, language: Language): string {
  if (language === "pt") return message;
  const messages: Record<string, string> = {
    "Séries de avaliações e fluxos para TWR/MWR ainda pendentes.": "Valuation and cash-flow series required for TWR/MWR are still pending.",
    "Avaliações manuais; histórico de patrimônio a custo. Rentabilidade TWR/MWR ainda indisponível.": "Manual valuations; equity history at cost. TWR/MWR performance remains unavailable.",
    "Caixa reconhecido por data de negociação; não representa saldo liquidado para saque.": "Trade-date cash; this does not represent a settled balance available for withdrawal.",
  };
  if (messages[message]) return messages[message];
  const suffixes: Record<string, string> = {
    ": registre uma avaliação após o desdobramento.": ": record a valuation after the split.",
    ": avaliação ausente.": ": missing valuation.",
    ": avaliação desatualizada.": ": stale valuation.",
  };
  for (const [suffix, translated] of Object.entries(suffixes)) {
    if (message.endsWith(suffix)) return message.slice(0, -suffix.length) + translated;
  }
  return message;
}
