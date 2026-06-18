import type { CategoryTrendPoint } from "../types/category";
import { formatCurrency } from "../lib/format";
import "./CategoryTrendBars.css";

interface CategoryTrendBarsProps {
  data: CategoryTrendPoint[];
}

function formatMonthLabel(monthStr: string): string {
  // monthStr is "YYYY-MM"
  const [year, month] = monthStr.split("-").map(Number);
  const date = new Date(year, month - 1, 1);
  return date.toLocaleDateString("en-GB", { month: "short", year: "2-digit" });
}

export function CategoryTrendBars({ data }: CategoryTrendBarsProps) {
  const maxTotal = Math.max(...data.map((d) => d.total), 1);

  return (
    <div className="trend-bars">
      {data.map((point) => {
        const widthPct = (point.total / maxTotal) * 100;
        return (
          <div key={point.month} className="trend-bar-row">
            <span className="trend-bar-row__month font-display">
              {formatMonthLabel(point.month)}
            </span>
            <div className="trend-bar-row__track">
              <div
                className="trend-bar-row__fill"
                style={{ width: `${Math.max(widthPct, 2)}%` }}
              />
            </div>
            <span className="trend-bar-row__amount numeral">
              {formatCurrency(point.total)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
