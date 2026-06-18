import type { DateRangeFilter } from "../pages/useTransactionsData";
import "./DateRangeSelector.css";

const RANGES: { value: DateRangeFilter; label: string }[] = [
  { value: "this_month", label: "This month" },
  { value: "last_month", label: "Last month" },
  { value: "last_30_days", label: "Last 30 days" },
  { value: "last_6_months", label: "Last 6 months" },
  { value: "all", label: "All time" },
];

interface DateRangeSelectorProps {
  value: DateRangeFilter;
  onChange: (range: DateRangeFilter) => void;
}

export function DateRangeSelector({ value, onChange }: DateRangeSelectorProps) {
  return (
    <div className="date-range" role="group" aria-label="Filter by date range">
      {RANGES.map((range) => (
        <button
          key={range.value}
          type="button"
          className={
            value === range.value ? "date-range__option date-range__option--active" : "date-range__option"
          }
          onClick={() => onChange(range.value)}
          aria-pressed={value === range.value}
        >
          {range.label}
        </button>
      ))}
    </div>
  );
}
