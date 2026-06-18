import { Link } from "react-router-dom";
import { useCategoriesSummary } from "./useCategoriesData";
import { formatCurrency } from "../lib/format";
import "./CategoriesListPage.css";

export function CategoriesListPage() {
  const { data: summary, isLoading } = useCategoriesSummary();
  const sorted = [...(summary ?? [])].sort((a, b) => b.total - a.total);

  return (
    <div className="categories-list-page">
      <h2>Categories</h2>
      <p className="categories-list-page__subtitle">
        This month's spending, by category. Choose one to see its trend and
        where the money actually goes.
      </p>

      <div className="ledger">
        {isLoading && <p className="categories-empty">Loading categories&hellip;</p>}

        {!isLoading && sorted.length === 0 && (
          <p className="categories-empty">No spending recorded yet this month.</p>
        )}

        {sorted.map((category) => (
          <Link
            key={category.category}
            to={`/categories/${encodeURIComponent(category.category)}`}
            className="category-list-row"
          >
            <div className="category-list-row__main">
              <span className="category-list-row__label font-display">
                {category.category}
              </span>
              <span className="category-list-row__meta">
                {category.transaction_count} transaction
                {category.transaction_count === 1 ? "" : "s"}
              </span>
            </div>
            <span className="category-list-row__amount numeral">
              {formatCurrency(category.total)}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
