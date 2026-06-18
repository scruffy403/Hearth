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

const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
});

export function formatDateShort(isoDate: string): string {
  return dateFormatter.format(new Date(isoDate));
}

export function formatMonthName(date = new Date()): string {
  return date.toLocaleDateString("en-GB", { month: "long" });
}
