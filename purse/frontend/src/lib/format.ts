const currencyFormatter = new Intl.NumberFormat("en-GB", {
  style: "currency",
  currency: "GBP",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatCurrency(amount: number): string {
  return currencyFormatter.format(Math.abs(amount));
}

export function formatCurrencySigned(amount: number): string {
  const formatted = currencyFormatter.format(Math.abs(amount));
  return amount < 0 ? `−${formatted}` : `+${formatted}`;
}

const dateFormatterNoYear = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
});

const dateFormatterWithYear = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

export function formatDateShort(isoDate: string): string {
  const date = new Date(isoDate);
  const currentYear = new Date().getFullYear();
  const formatter =
    date.getFullYear() === currentYear ? dateFormatterNoYear : dateFormatterWithYear;
  return formatter.format(date);
}

export function formatMonthName(date = new Date()): string {
  return date.toLocaleDateString("en-GB", { month: "long" });
}
